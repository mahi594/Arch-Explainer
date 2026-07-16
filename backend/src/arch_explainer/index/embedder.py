"""Turns CodeChunks into vectors, either via Gemini's API or a fully local
sentence-transformers model.

The actual embedding call is isolated behind a small `EmbedFn` so this
module is fully unit-testable without network access or an API key — tests
inject a fake embed function instead of hitting the real API.

Two things solve the "API key ran out of quota mid-run" problem:

1. `create_embedder(provider="local")` (the default) uses sentence-transformers,
   which runs on your own machine — no key, no quota, no cost. Trades some
   retrieval quality for that.
2. `EmbeddingCache` persists every vector to a local SQLite file, keyed by a
   hash of (model, text). If a run dies partway through — quota exhaustion,
   crash, Ctrl-C — re-running the pipeline skips every chunk already embedded
   and only pays for the remainder. This applies to both providers.

Uses the `google-genai` SDK for the Gemini path (the `google-generativeai`
package it replaced was fully sunset by Google in 2026).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Callable, Sequence

from arch_explainer.models import CodeChunk, Embedding

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768  # gemini-embedding-001 defaults to 3072; we request 768 explicitly to match our schema
LOCAL_MODEL = "all-MiniLM-L6-v2"  # 384 dims, ~80MB, good default for local/offline use
DEFAULT_BATCH_SIZE = 100
MAX_RETRIES = 3
DEFAULT_CACHE_PATH = ".cache/embeddings.db"

# Takes a list of texts, returns one vector per text, same order.
EmbedFn = Callable[[list[str]], list[list[float]]]


def chunk_to_embedding_text(chunk: CodeChunk) -> str:
    """Builds the string actually sent to the embedding model.

    Embedding raw code alone throws away context an LLM would use — what
    kind of thing is this, what's it called, what file is it in. Prepending
    that metadata measurably improves retrieval for queries like "find the
    auth logic" versus embedding bare code text.
    """
    label = f"{chunk.type.value}: {chunk.name}" if chunk.name else chunk.type.value
    return f"{label}\nFile: {chunk.file_path}\nContent:\n{chunk.content}"


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------


class EmbeddingCache:
    """Persists text -> vector on disk so repeated runs don't re-pay for
    embeddings that already succeeded.

    Keyed on a hash of (model, text) rather than chunk id: if a chunk's
    content hasn't changed, its embedding is reused even across pipeline
    runs on different days; if the model changes (e.g. switching from
    Gemini to local), the key changes too, so vectors from incompatible
    models never get mixed.
    """

    def __init__(self, path: str | Path = DEFAULT_CACHE_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                cache_key TEXT PRIMARY KEY,
                model TEXT NOT NULL,
                vector TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    @staticmethod
    def _key(text: str, model: str) -> str:
        return hashlib.sha256(f"{model}::{text}".encode("utf-8")).hexdigest()

    def get(self, text: str, model: str) -> list[float] | None:
        row = self._conn.execute(
            "SELECT vector FROM embeddings WHERE cache_key = ?",
            (self._key(text, model),),
        ).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, text: str, model: str, vector: list[float]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO embeddings (cache_key, model, vector) VALUES (?, ?, ?)",
            (self._key(text, model), model, json.dumps(vector)),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def with_cache(embed_fn: EmbedFn, cache: EmbeddingCache, model: str) -> EmbedFn:
    """Wraps an EmbedFn so only cache-miss texts hit the network/model.

    Transparent to callers: still takes a list of texts, still returns a
    same-length, same-order list of vectors. Only the misses get embedded
    and then written back to the cache.
    """

    def cached_embed(texts: list[str]) -> list[list[float]]:
        results: list[list[float] | None] = [cache.get(t, model) for t in texts]
        missing_indices = [i for i, v in enumerate(results) if v is None]

        if missing_indices:
            missing_texts = [texts[i] for i in missing_indices]
            fresh_vectors = embed_fn(missing_texts)
            if len(fresh_vectors) != len(missing_texts):
                raise RuntimeError(
                    f"Embed fn returned {len(fresh_vectors)} vectors for {len(missing_texts)} texts"
                )
            for i, vector in zip(missing_indices, fresh_vectors):
                cache.set(texts[i], model, vector)
                results[i] = vector

        return results  # type: ignore[return-value]

    return cached_embed


# --------------------------------------------------------------------------
# Embed function builders (lazy imports so neither SDK is required just to
# import this module or run tests against an injected embed_fn)
# --------------------------------------------------------------------------


def _default_gemini_embed_fn(api_key: str, model: str) -> EmbedFn:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    def embed(texts: list[str]) -> list[list[float]]:
        result = client.models.embed_content(
            model=model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )
        return [e.values for e in result.embeddings]

    return embed


def _default_local_embed_fn(model_name: str) -> tuple[EmbedFn, int]:
    """Loads a sentence-transformers model once and returns an EmbedFn plus
    its output dimensionality (model-dependent, so we return it rather than
    hardcode it)."""
    from sentence_transformers import SentenceTransformer

    st_model = SentenceTransformer(model_name)
    dims = st_model.get_sentence_embedding_dimension()

    def embed(texts: list[str]) -> list[list[float]]:
        return st_model.encode(texts, convert_to_numpy=True).tolist()

    return embed, dims


# --------------------------------------------------------------------------
# Embedder
# --------------------------------------------------------------------------


class GeminiEmbedder:
    """Embeds CodeChunks in batches, retrying transient failures with backoff.

    Despite the name, this class is provider-agnostic — it just calls
    whatever `embed_fn` it's given. Use `create_gemini_embedder` /
    `create_local_embedder` / `create_embedder` below rather than
    constructing this directly, unless you're injecting a fake for tests.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = EMBEDDING_MODEL,
        dimensions: int = EMBEDDING_DIMENSIONS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        embed_fn: EmbedFn | None = None,
    ):
        if embed_fn is None and not api_key:
            raise ValueError("Either api_key or embed_fn must be provided")
        self.model = model
        self.batch_size = batch_size
        self.dimensions = dimensions
        self._embed_fn = embed_fn or _default_gemini_embed_fn(api_key, model)  # type: ignore[arg-type]

    def embed_chunks(self, chunks: Sequence[CodeChunk]) -> list[Embedding]:
        """Embeds every chunk, batching requests to stay within API limits."""
        embeddings: list[Embedding] = []
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            vectors = self._embed_batch_with_retry(batch)
            if len(vectors) != len(batch):
                raise RuntimeError(
                    f"Embedding count mismatch: sent {len(batch)} chunks, got {len(vectors)} vectors back"
                )
            for chunk, vector in zip(batch, vectors):
                embeddings.append(
                    Embedding(chunk_id=chunk.id, vector=vector, model=self.model, dimensions=len(vector))
                )
        return embeddings

    def _embed_batch_with_retry(self, batch: Sequence[CodeChunk]) -> list[list[float]]:
        texts = [chunk_to_embedding_text(c) for c in batch]
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self._embed_fn(texts)
            except Exception as e:  # noqa: BLE001 - deliberately broad, re-raised below
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)
        raise RuntimeError(f"Embedding failed after {MAX_RETRIES} attempts") from last_error


# --------------------------------------------------------------------------
# Factories
# --------------------------------------------------------------------------


def create_gemini_embedder(
    api_key: str,
    model: str = EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    cache_path: str | Path | None = DEFAULT_CACHE_PATH,
) -> GeminiEmbedder:
    embed_fn = _default_gemini_embed_fn(api_key, model)
    if cache_path:
        embed_fn = with_cache(embed_fn, EmbeddingCache(cache_path), model)
    return GeminiEmbedder(model=model, dimensions=EMBEDDING_DIMENSIONS, batch_size=batch_size, embed_fn=embed_fn)


def create_local_embedder(
    model_name: str = LOCAL_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    cache_path: str | Path | None = DEFAULT_CACHE_PATH,
) -> GeminiEmbedder:
    """Builds an embedder that runs fully offline via sentence-transformers.

    No API key, no quota, no cost — the trade-off is retrieval quality vs.
    a small general-purpose model rather than Gemini's. First call downloads
    the model (a few hundred MB) then runs entirely locally after that.
    """
    embed_fn, dims = _default_local_embed_fn(model_name)
    if cache_path:
        embed_fn = with_cache(embed_fn, EmbeddingCache(cache_path), model_name)
    return GeminiEmbedder(model=model_name, dimensions=dims, batch_size=batch_size, embed_fn=embed_fn)


def create_embedder(
    provider: str = "local",
    api_key: str | None = None,
    **kwargs,
) -> GeminiEmbedder:
    """Single entry point for the pipeline orchestrator.

    provider="local"  (default) -> sentence-transformers, free, offline
    provider="gemini"           -> Gemini API, needs api_key, costs quota
    """
    if provider == "gemini":
        if not api_key:
            raise ValueError("api_key is required when provider='gemini'")
        return create_gemini_embedder(api_key=api_key, **kwargs)
    if provider == "local":
        return create_local_embedder(**kwargs)
    raise ValueError(f"Unknown embedder provider: {provider!r}")