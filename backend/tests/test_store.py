from arch_explainer.index.store import SCHEMA_SQL, SearchOptions, _row_to_chunk
from arch_explainer.models import ChunkType


def test_schema_sql_embeds_correct_vector_dimensions():
    sql = SCHEMA_SQL.format(dimensions=768)
    assert "VECTOR(768)" in sql
    assert "CREATE EXTENSION IF NOT EXISTS vector" in sql


def test_schema_sql_is_idempotent_ddl():
    # Every statement must be safe to run on every startup.
    sql = SCHEMA_SQL.format(dimensions=768)
    for statement in ["CREATE TABLE", "CREATE INDEX"]:
        assert f"{statement} IF NOT EXISTS" in sql


def test_search_options_defaults():
    opts = SearchOptions()
    assert opts.limit == 10
    assert opts.threshold == 0.7
    assert opts.file_path is None
    assert opts.chunk_type is None


def test_row_to_chunk_converts_db_row_to_code_chunk():
    row = {
        "id": "fn-abc123",
        "file_path": "src/auth.py",
        "start_line": 10,
        "end_line": 20,
        "content": "def login(): ...",
        "type": "function",
        "name": "login",
        "parent_id": None,
        "metadata": {"is_async": False},
    }
    chunk = _row_to_chunk(row)
    assert chunk.id == "fn-abc123"
    assert chunk.type == ChunkType.FUNCTION
    assert chunk.metadata == {"is_async": False}


def test_row_to_chunk_handles_null_metadata():
    row = {
        "id": "fn-1",
        "file_path": "a.py",
        "start_line": 1,
        "end_line": 1,
        "content": "pass",
        "type": "function",
        "name": "f",
        "parent_id": None,
        "metadata": None,
    }
    chunk = _row_to_chunk(row)
    assert chunk.metadata == {}