# index

**Purpose:** The primary purpose of the 'index' module is to create a searchable index of a codebase. It enables the conversion of raw code into a format (vector embeddings) that can be efficiently queried for semantic similarity, allowing new engineers to find relevant code based on natural language descriptions or example code snippets. It handles the full lifecycle from embedding generation to storage and retrieval.

**Description:** This module is responsible for transforming code chunks into numerical vector embeddings and storing them in a searchable database. It supports both local (sentence-transformers) and cloud-based (Gemini API) embedding providers, includes caching mechanisms to optimize performance and cost, and provides a PostgreSQL-based vector store for persistence and similarity search.

## Key Files

- `src/arch_explainer/index/embedder.py`
- `src/arch_explainer/index/store.py`

## Dependencies

- hashlib
- json
- sqlite3
- time
- pathlib
- typing
- arch_explainer.models
- google.genai
- sentence_transformers
- dataclasses
- psycopg_pool
- psycopg.rows

## Public API

### `EMBEDDING_MODEL`

- **Type:** `variable`
- **Signature:** `str`
- **File:** `src/arch_explainer/index/embedder.py`

The default model name used for Gemini embeddings.

### `EMBEDDING_DIMENSIONS`

- **Type:** `variable`
- **Signature:** `int`
- **File:** `src/arch_explainer/index/embedder.py`

The default output dimensionality for Gemini embeddings.

### `LOCAL_MODEL`

- **Type:** `variable`
- **Signature:** `str`
- **File:** `src/arch_explainer/index/embedder.py`

The default model name used for local sentence-transformers embeddings.

### `DEFAULT_BATCH_SIZE`

- **Type:** `variable`
- **Signature:** `int`
- **File:** `src/arch_explainer/index/embedder.py`

The default batch size for embedding requests.

### `MAX_RETRIES`

- **Type:** `variable`
- **Signature:** `int`
- **File:** `src/arch_explainer/index/embedder.py`

The maximum number of retries for embedding API calls.

### `DEFAULT_CACHE_PATH`

- **Type:** `variable`
- **Signature:** `str`
- **File:** `src/arch_explainer/index/embedder.py`

The default file path for the SQLite embedding cache.

### `EmbedFn`

- **Type:** `variable`
- **Signature:** `Callable[[list[str]], list[list[float]]]`
- **File:** `src/arch_explainer/index/embedder.py`

A type alias for a function that takes a list of strings and returns a list of their corresponding vector embeddings.

### `chunk_to_embedding_text`

- **Type:** `function`
- **Signature:** `def chunk_to_embedding_text(chunk: CodeChunk) -> str`
- **File:** `src/arch_explainer/index/embedder.py`

Constructs the input string for the embedding model from a CodeChunk, including metadata for better retrieval.

### `EmbeddingCache`

- **Type:** `class`
- **Signature:** `class EmbeddingCache`
- **File:** `src/arch_explainer/index/embedder.py`

A local SQLite-based cache for storing text-to-vector mappings, preventing redundant embedding calls.

### `EmbeddingCache.__init__`

- **Type:** `method`
- **Signature:** `def __init__(self, path: str | Path = DEFAULT_CACHE_PATH)`
- **File:** `src/arch_explainer/index/embedder.py`

Initializes the embedding cache, creating the SQLite database and table if they don't exist.

### `EmbeddingCache.get`

- **Type:** `method`
- **Signature:** `def get(self, text: str, model: str) -> list[float] | None`
- **File:** `src/arch_explainer/index/embedder.py`

Retrieves an embedding vector from the cache for a given text and model.

### `EmbeddingCache.set`

- **Type:** `method`
- **Signature:** `def set(self, text: str, model: str, vector: list[float]) -> None`
- **File:** `src/arch_explainer/index/embedder.py`

Stores an embedding vector in the cache for a given text and model.

### `EmbeddingCache.close`

- **Type:** `method`
- **Signature:** `def close(self) -> None`
- **File:** `src/arch_explainer/index/embedder.py`

Closes the SQLite database connection for the cache.

### `with_cache`

- **Type:** `function`
- **Signature:** `def with_cache(embed_fn: EmbedFn, cache: EmbeddingCache, model: str) -> EmbedFn`
- **File:** `src/arch_explainer/index/embedder.py`

A higher-order function that wraps an `EmbedFn` with caching logic, only calling the underlying function for cache misses.

### `GeminiEmbedder`

- **Type:** `class`
- **Signature:** `class GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

A class that orchestrates the embedding of CodeChunks, handling batching and retries. It is provider-agnostic, using an injected `EmbedFn`.

### `GeminiEmbedder.__init__`

- **Type:** `method`
- **Signature:** `def __init__(self, api_key: str | None = None, model: str = EMBEDDING_MODEL, dimensions: int = EMBEDDING_DIMENSIONS, batch_size: int = DEFAULT_BATCH_SIZE, embed_fn: EmbedFn | None = None)`
- **File:** `src/arch_explainer/index/embedder.py`

Initializes the embedder with an API key (for Gemini), model, dimensions, batch size, and an optional custom embedding function.

### `GeminiEmbedder.embed_chunks`

- **Type:** `method`
- **Signature:** `def embed_chunks(self, chunks: Sequence[CodeChunk]) -> list[Embedding]`
- **File:** `src/arch_explainer/index/embedder.py`

Embeds a sequence of CodeChunks, batching requests and applying retry logic.

### `create_gemini_embedder`

- **Type:** `function`
- **Signature:** `def create_gemini_embedder(api_key: str, model: str = EMBEDDING_MODEL, batch_size: int = DEFAULT_BATCH_SIZE, cache_path: str | Path | None = DEFAULT_CACHE_PATH) -> GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

Factory function to create a `GeminiEmbedder` configured to use the Gemini API, optionally with caching.

### `create_local_embedder`

- **Type:** `function`
- **Signature:** `def create_local_embedder(model_name: str = LOCAL_MODEL, batch_size: int = DEFAULT_BATCH_SIZE, cache_path: str | Path | None = DEFAULT_CACHE_PATH) -> GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

Factory function to create a `GeminiEmbedder` configured to use a local sentence-transformers model, optionally with caching.

### `create_embedder`

- **Type:** `function`
- **Signature:** `def create_embedder(provider: str = "local", api_key: str | None = None, **kwargs) -> GeminiEmbedder`
- **File:** `src/arch_explainer/index/embedder.py`

A unified factory function to create an embedder based on the specified provider ('local' or 'gemini').

### `SCHEMA_SQL`

- **Type:** `variable`
- **Signature:** `str`
- **File:** `src/arch_explainer/index/store.py`

SQL script for creating the necessary tables and indexes (code_chunks, embeddings) in a Postgres database with pgvector.

### `SearchOptions`

- **Type:** `class`
- **Signature:** `class SearchOptions`
- **File:** `src/arch_explainer/index/store.py`

A class defining options for similarity search queries, such as limit, similarity threshold, and filters.

### `PgVectorStore`

- **Type:** `class`
- **Signature:** `class PgVectorStore`
- **File:** `src/arch_explainer/index/store.py`

A class for interacting with a PostgreSQL database using the pgvector extension to store and search CodeChunks and their embeddings.

### `PgVectorStore.__init__`

- **Type:** `method`
- **Signature:** `def __init__(self, database_url: str, dimensions: int = 768)`
- **File:** `src/arch_explainer/index/store.py`

Initializes the PgVectorStore with a database URL and the expected embedding dimensions.

### `PgVectorStore.initialize`

- **Type:** `method`
- **Signature:** `def initialize(self) -> None`
- **File:** `src/arch_explainer/index/store.py`

Ensures the pgvector extension is enabled and creates the `code_chunks` and `embeddings` tables and indexes if they do not exist.

### `PgVectorStore.store_chunks`

- **Type:** `method`
- **Signature:** `def store_chunks(self, chunks: list[CodeChunk], embeddings: dict[str, list[float]], model: str) -> None`
- **File:** `src/arch_explainer/index/store.py`

Upserts a list of CodeChunks and their corresponding embeddings into the database within a single transaction.

### `PgVectorStore.search_similar`

- **Type:** `method`
- **Signature:** `def search_similar(self, query_vector: list[float], options: SearchOptions | None = None) -> list[VectorSearchResult]`
- **File:** `src/arch_explainer/index/store.py`

Performs a similarity search against stored embeddings using a query vector, returning matching CodeChunks and their similarity scores.

### `PgVectorStore.delete_chunks`

- **Type:** `method`
- **Signature:** `def delete_chunks(self, chunk_ids: list[str]) -> None`
- **File:** `src/arch_explainer/index/store.py`

Deletes CodeChunks and their associated embeddings from the database by a list of chunk IDs.

### `PgVectorStore.close`

- **Type:** `method`
- **Signature:** `def close(self) -> None`
- **File:** `src/arch_explainer/index/store.py`

Closes the database connection pool.
