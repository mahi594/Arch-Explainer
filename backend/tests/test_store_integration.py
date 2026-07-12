"""Integration tests against a real Postgres+pgvector instance.

These are skipped by default. To run them:

    docker compose -f backend/docker-compose.yml up -d
    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/arch_explainer \\
        pytest tests/test_store_integration.py -v
"""

import os

import pytest

from arch_explainer.index.store import PgVectorStore, SearchOptions
from arch_explainer.models import ChunkType, CodeChunk

DATABASE_URL = os.environ.get("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="Set DATABASE_URL to a running Postgres+pgvector instance to run this"
)


@pytest.fixture
def store():
    s = PgVectorStore(DATABASE_URL, dimensions=8)
    s.initialize()
    yield s
    s.close()


def make_chunk(id, content="def f(): pass"):
    return CodeChunk(
        id=id, file_path="a.py", start_line=1, end_line=1, content=content, type=ChunkType.FUNCTION, name="f"
    )


def test_store_and_search_round_trip(store):
    chunk = make_chunk("integration-test-1")
    vector = [0.1] * 8

    store.store_chunks([chunk], {chunk.id: vector})
    results = store.search_similar(vector, SearchOptions(limit=5, threshold=0.0))

    assert any(r.chunk.id == chunk.id for r in results)
    store.delete_chunks([chunk.id])


def test_delete_chunks_removes_them(store):
    chunk = make_chunk("integration-test-2")
    vector = [0.2] * 8
    store.store_chunks([chunk], {chunk.id: vector})

    store.delete_chunks([chunk.id])
    results = store.search_similar(vector, SearchOptions(limit=5, threshold=0.0))

    assert not any(r.chunk.id == chunk.id for r in results)