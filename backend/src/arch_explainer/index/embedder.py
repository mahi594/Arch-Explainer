"""Turns CodeChunks into vectors using Gemini's text-embedding-004 model.

The actual Gemini SDK call is isolated behind a small `EmbedFn` so this
module is fully unit-testable without network access or an API key — tests
inject a fake embed function instead of hitting the real API.
"""

from __future__ import annotations

import time
from typing import Callable, Sequence

from arch_explainer.models import CodeChunk, Embedding

EMBEDDING_MODEL = "models/text-embedding-004"
EMBEDDING_DIMENSIONS = 768
DEFAULT_BATCH_SIZE = 100
MAX_RETRIES = 3

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


def _default_embed_fn(api_key: str, model: str) -> EmbedFn:
    """Builds the real network-calling embed function.

    Deliberately created lazily (only when no embed_fn is injected) so
    importing this module never requires the google-generativeai package
    to be configured, and tests never accidentally reach the network.
    """
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    def embed(texts: list[str]) -> list[list[float]]:
        result = genai.embed_content(model=model, content=texts, task_type="RETRIEVAL_DOCUMENT")
        return result["embedding"]

    return embed


class GeminiEmbedder:
    """Embeds CodeChunks in batches, retrying transient failures with backoff."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = EMBEDDING_MODEL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        embed_fn: EmbedFn | None = None,
    ):
        if embed_fn is None and not api_key:
            raise ValueError("Either api_key or embed_fn must be provided")
        self.model = model
        self.batch_size = batch_size
        self.dimensions = EMBEDDING_DIMENSIONS
        self._embed_fn = embed_fn or _default_embed_fn(api_key, model)  # type: ignore[arg-type]

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


def create_embedder(api_key: str, model: str = EMBEDDING_MODEL) -> GeminiEmbedder:
    return GeminiEmbedder(api_key=api_key, model=model)