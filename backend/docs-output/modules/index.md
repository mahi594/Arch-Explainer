# index

**Purpose:** To serve as the core indexing and retrieval layer for code chunks within the `arch_explainer` system. It enables semantic search over the codebase by transforming code into vector representations and efficiently storing and querying these representations. This module abstracts away the complexities of interacting with embedding models and vector databases, providing a unified interface for the rest of the application.

**Description:** This module is responsible for the entire lifecycle of creating, caching, storing, and retrieving vector embeddings for `CodeChunk` objects. It provides flexible options for embedding generation (local or cloud-based) and robust persistence and search capabilities using a PostgreSQL database with the `pgvector` extension.

## Key Files

- `src/arch_explainer/index/embedder.py`
- `src/arch_explainer/index/store.py`

## Dependencies

- arch_explainer.models
- hashlib
- json
- sqlite3
- time
- pathlib
- typing
- dataclasses
- google.genai
- sentence_transformers
- psycopg_pool
- psycopg

## Public API

### `EmbedFn`

- **Type:** `variable`
- **Signature:** `Callable[[list[str]], list[list[float]]]`
- **File:** `src/arch_explainer/index/embedder.py`

A type alias for a function that takes a list of strings and returns a list of corresponding embedding vectors.

### `chunk_to_embedding_text`

- **Type:** `function`
- **Signature:** `def chunk_to_embedding_text(chunk: CodeChunk) -> str`
- **File:** `src/arch_explainer/index/embedder.py`

Builds the string actually sent to the embedding model, prepending metadata for improved retrieval.

### `EmbeddingCache`

- **Type:** `class`
- **Signature:** `class EmbeddingCache(path: str | Path = DEFAULT_CACHE_PATH)`
- **File:** `src/arch_explainer/index/embedder.py`

Persists text -> vector on disk using SQLite, preventing re-computation of existing embeddings.

### `GeminiEmbedder`

- **Type:** `class`
- **Signature:** `class GeminiEmbedder(api_key: str | None = None, model: str = EMBEDDING_MODEL, dimensions: int = EMBEDDING_DIMENSIONS, batch_size: int = DEFAULT_BATCH_SIZE, embed_fn: EmbedFn | None = None)`
- **File:** `src/arch_explainer/index/embedder.py`

Embeds `CodeChunk`s in batches, handling retries. It is provider-agnostic, calling the `embed_fn` it's given.

### `create_gemini_embedder`

- **Type:** `function`
- **Signature:** `def create_gemini_embedder(api_key: str, model: str = EMBEDDING_MODEL, batch_size: int = DEFAULT_BATCH_SIZE, cache_path: str | Path | None = DEFAULT_CACHE_PATH) -> GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

Factory function to build a `GeminiEmbedder` configured to use the Gemini API, optionally with caching.

### `create_local_embedder`

- **Type:** `function`
- **Signature:** `def create_local_embedder(model_name: str = LOCAL_MODEL, batch_size: int = DEFAULT_BATCH_SIZE, cache_path: str | Path | None = DEFAULT_CACHE_PATH) -> GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

Factory function to build a `GeminiEmbedder` configured to use a local `sentence-transformers` model, optionally with caching.

### `create_embedder`

- **Type:** `function`
- **Signature:** `def create_embedder(provider: str = "local", api_key: str | None = None, **kwargs) -> GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

The primary entry point for creating an embedder, allowing selection between 'local' (sentence-transformers) and 'gemini' providers.

### `SearchOptions`

- **Type:** `class`
- **Signature:** `class SearchOptions`
- **File:** `src/arch_explainer/index/store.py`

Defines parameters for similarity search queries, such as limit, similarity threshold, and optional filters.

### `PgVectorStore`

- **Type:** `class`
- **Signature:** `class PgVectorStore(database_url: str, dimensions: int = 768)`
- **File:** `src/arch_explainer/index/store.py`

Manages storage and retrieval of `CodeChunk`s and their embeddings in a PostgreSQL database with the `pgvector` extension.
