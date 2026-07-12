import pytest

from arch_explainer.index.embedder import GeminiEmbedder, chunk_to_embedding_text
from arch_explainer.models import ChunkType, CodeChunk


def make_chunk(id="c1", name="foo", chunk_type=ChunkType.FUNCTION, content="def foo(): pass"):
    return CodeChunk(
        id=id,
        file_path="a.py",
        start_line=1,
        end_line=1,
        content=content,
        type=chunk_type,
        name=name,
    )


def fake_embed_fn(dimensions=8):
    """Returns a deterministic fake embed function + a call log, so tests
    can assert on what was actually sent without hitting the network.
    """
    calls = []

    def embed(texts: list[str]) -> list[list[float]]:
        calls.append(list(texts))
        return [[float(len(t) % 10)] * dimensions for t in texts]

    return embed, calls


def test_embed_text_includes_type_name_and_path():
    chunk = make_chunk()
    text = chunk_to_embedding_text(chunk)
    assert "function: foo" in text
    assert "File: a.py" in text
    assert "def foo(): pass" in text


def test_embed_chunks_returns_one_embedding_per_chunk():
    embed_fn, _ = fake_embed_fn()
    embedder = GeminiEmbedder(embed_fn=embed_fn)
    chunks = [make_chunk(id=f"c{i}", name=f"fn{i}") for i in range(5)]

    embeddings = embedder.embed_chunks(chunks)

    assert len(embeddings) == 5
    assert [e.chunk_id for e in embeddings] == [c.id for c in chunks]


def test_embed_chunks_batches_requests():
    embed_fn, calls = fake_embed_fn()
    embedder = GeminiEmbedder(embed_fn=embed_fn, batch_size=2)
    chunks = [make_chunk(id=f"c{i}", name=f"fn{i}") for i in range(5)]

    embedder.embed_chunks(chunks)

    # 5 chunks at batch_size=2 -> batches of 2, 2, 1
    assert [len(c) for c in calls] == [2, 2, 1]


def test_retries_on_transient_failure_then_succeeds():
    attempts = {"n": 0}

    def flaky_embed(texts):
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise ConnectionError("simulated transient failure")
        return [[1.0] * 8 for _ in texts]

    embedder = GeminiEmbedder(embed_fn=flaky_embed)
    embeddings = embedder.embed_chunks([make_chunk()])

    assert attempts["n"] == 2
    assert len(embeddings) == 1


def test_raises_after_exhausting_retries():
    def always_fails(texts):
        raise ConnectionError("simulated permanent failure")

    embedder = GeminiEmbedder(embed_fn=always_fails)

    with pytest.raises(RuntimeError, match="Embedding failed after"):
        embedder.embed_chunks([make_chunk()])


def test_raises_on_vector_count_mismatch():
    def wrong_count(texts):
        return [[1.0] * 8]  # always returns 1, regardless of input size

    embedder = GeminiEmbedder(embed_fn=wrong_count)

    with pytest.raises(RuntimeError, match="mismatch"):
        embedder.embed_chunks([make_chunk(id="c1"), make_chunk(id="c2")])


def test_requires_api_key_or_embed_fn():
    with pytest.raises(ValueError):
        GeminiEmbedder()