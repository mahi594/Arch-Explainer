"""Stores CodeChunks + their embeddings in Postgres/pgvector, and searches
by similarity.

Uses psycopg3 directly rather than an ORM — the schema is small and fixed,
and raw SQL keeps the vector-specific syntax (`<=>` cosine distance,
`vector(N)` column type) visible instead of hidden behind an abstraction
that doesn't know about pgvector.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from arch_explainer.models import ChunkType, CodeChunk, VectorSearchResult

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS code_chunks (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    name TEXT,
    parent_id TEXT,
    metadata JSONB DEFAULT '{{}}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id TEXT PRIMARY KEY REFERENCES code_chunks(id) ON DELETE CASCADE,
    vector VECTOR({dimensions}) NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_code_chunks_file_path ON code_chunks(file_path);
CREATE INDEX IF NOT EXISTS idx_code_chunks_type ON code_chunks(type);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector
    ON embeddings USING ivfflat (vector vector_cosine_ops) WITH (lists = 100);
"""


@dataclass
class SearchOptions:
    limit: int = 10
    threshold: float = 0.7
    file_path: str | None = None
    chunk_type: ChunkType | None = None


def _row_to_chunk(row: dict) -> CodeChunk:
    return CodeChunk(
        id=row["id"],
        file_path=row["file_path"],
        start_line=row["start_line"],
        end_line=row["end_line"],
        content=row["content"],
        type=row["type"],
        name=row["name"],
        parent_id=row["parent_id"],
        metadata=row["metadata"] or {},
    )


class PgVectorStore:
    """Wraps a psycopg connection pool. Call `initialize()` once before use."""

    def __init__(self, database_url: str, dimensions: int = 768):
        self.database_url = database_url
        self.dimensions = dimensions
        self._pool = None

    def initialize(self) -> None:
        """Creates the extension, tables, and indexes if they don't exist.

        Safe to call on every startup — every statement is idempotent
        (CREATE ... IF NOT EXISTS). Note this means it will NOT resize an
        existing `embeddings.vector` column if `dimensions` changes between
        runs (e.g. switching embedding providers) — that needs a manual
        migration: TRUNCATE the table, then ALTER COLUMN ... TYPE vector(N).
        """
        from psycopg_pool import ConnectionPool

        self._pool = ConnectionPool(self.database_url, min_size=1, max_size=10, open=True)
        with self._pool.connection() as conn:
            conn.execute(SCHEMA_SQL.format(dimensions=self.dimensions))
            conn.commit()

    def store_chunks(
        self,
        chunks: list[CodeChunk],
        embeddings: dict[str, list[float]],
        model: str,
    ) -> None:
        """Upserts chunks and their embeddings in one transaction.

        `embeddings` maps chunk_id -> vector. A chunk without a matching
        embedding is stored but skipped in the embeddings table — this
        can happen if embedding a batch partially failed upstream, and
        we'd rather keep the chunk record than lose it entirely.

        `model` is the name of whichever embedder actually produced these
        vectors (e.g. `embedder.model` from index/embedder.py) — recorded
        per-row so `embeddings.model` reflects reality instead of a fixed
        string, since the pipeline can run against either the local
        sentence-transformers model or Gemini.
        """
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                for chunk in chunks:
                    cur.execute(
                        """
                        INSERT INTO code_chunks
                            (id, file_path, start_line, end_line, content, type, name, parent_id, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            file_path = EXCLUDED.file_path,
                            start_line = EXCLUDED.start_line,
                            end_line = EXCLUDED.end_line,
                            content = EXCLUDED.content,
                            type = EXCLUDED.type,
                            name = EXCLUDED.name,
                            parent_id = EXCLUDED.parent_id,
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                        """,
                        (
                            chunk.id,
                            chunk.file_path,
                            chunk.start_line,
                            chunk.end_line,
                            chunk.content,
                            chunk.type.value,
                            chunk.name,
                            chunk.parent_id,
                            json.dumps(chunk.metadata),
                        ),
                    )

                    vector = embeddings.get(chunk.id)
                    if vector is None:
                        continue

                    cur.execute(
                        """
                        INSERT INTO embeddings (chunk_id, vector, model, dimensions)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            vector = EXCLUDED.vector,
                            model = EXCLUDED.model,
                            dimensions = EXCLUDED.dimensions,
                            created_at = NOW()
                        """,
                        (chunk.id, str(vector), model, len(vector)),
                    )
            conn.commit()

    def search_similar(self, query_vector: list[float], options: SearchOptions | None = None) -> list[VectorSearchResult]:
        opts = options or SearchOptions()

        query = """
            SELECT c.id, c.file_path, c.start_line, c.end_line, c.content, c.type,
                   c.name, c.parent_id, c.metadata,
                   1 - (e.vector <=> %s::vector) AS similarity
            FROM code_chunks c
            JOIN embeddings e ON c.id = e.chunk_id
            WHERE 1 - (e.vector <=> %s::vector) > %s
        """
        params: list = [str(query_vector), str(query_vector), opts.threshold]

        if opts.file_path:
            query += " AND c.file_path = %s"
            params.append(opts.file_path)

        if opts.chunk_type:
            query += " AND c.type = %s"
            params.append(opts.chunk_type.value)

        query += " ORDER BY similarity DESC LIMIT %s"
        params.append(opts.limit)

        from psycopg.rows import dict_row

        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

        return [
            VectorSearchResult(chunk=_row_to_chunk(row), score=float(row["similarity"]))
            for row in rows
        ]

    def delete_chunks(self, chunk_ids: list[str]) -> None:
        if not chunk_ids:
            return
        with self._pool.connection() as conn:
            conn.execute("DELETE FROM code_chunks WHERE id = ANY(%s)", (chunk_ids,))
            conn.commit()

    def close(self) -> None:
        if self._pool:
            self._pool.close()