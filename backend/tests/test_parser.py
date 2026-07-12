from arch_explainer.ingest.parser import parse_file
from arch_explainer.models import ChunkType

SAMPLE = '''\
"""A sample module."""
import os
from typing import Optional

MAX_RETRIES = 3


class Greeter:
    """Greets people."""

    def __init__(self, name: str):
        self.name = name

    def greet(self, loud: bool = False) -> str:
        def shout(s):
            return s.upper()
        msg = f"Hello, {self.name}"
        return shout(msg) if loud else msg


def standalone_function(x: int, y: int) -> int:
    return x + y
'''

BROKEN = "def broken(:\n    not valid\n"


def test_file_chunk_always_present():
    chunks = parse_file("sample.py", SAMPLE)
    file_chunks = [c for c in chunks if c.type == ChunkType.FILE]
    assert len(file_chunks) == 1
    assert file_chunks[0].content == SAMPLE


def test_extracts_class_and_methods_with_correct_parent():
    chunks = parse_file("sample.py", SAMPLE)
    by_name = {c.name: c for c in chunks}

    assert by_name["Greeter"].type == ChunkType.CLASS
    assert by_name["__init__"].type == ChunkType.METHOD
    assert by_name["__init__"].parent_id == by_name["Greeter"].id
    assert by_name["greet"].parent_id == by_name["Greeter"].id


def test_nested_function_not_extracted_separately():
    # `shout` is defined inside `greet` — it should be part of greet's
    # content, not its own top-level chunk.
    chunks = parse_file("sample.py", SAMPLE)
    names = [c.name for c in chunks]
    assert "shout" not in names
    by_name = {c.name: c for c in chunks}
    assert "def shout" in by_name["greet"].content


def test_extracts_standalone_function():
    chunks = parse_file("sample.py", SAMPLE)
    by_name = {c.name: c for c in chunks}
    fn = by_name["standalone_function"]
    assert fn.type == ChunkType.FUNCTION
    assert fn.metadata["parameters"] == ["x", "y"]


def test_extracts_imports():
    chunks = parse_file("sample.py", SAMPLE)
    imports = [c for c in chunks if c.type == ChunkType.IMPORT]
    names = {c.name for c in imports}
    assert names == {"os", "typing"}


def test_extracts_top_level_constant():
    chunks = parse_file("sample.py", SAMPLE)
    by_name = {c.name: c for c in chunks}
    const = by_name["MAX_RETRIES"]
    assert const.type == ChunkType.VARIABLE
    assert const.metadata["is_constant"] is True


def test_chunk_ids_are_stable_across_runs():
    a = parse_file("sample.py", SAMPLE)
    b = parse_file("sample.py", SAMPLE)
    assert [c.id for c in a] == [c.id for c in b]


def test_syntax_error_falls_back_instead_of_raising():
    chunks = parse_file("broken.py", BROKEN)
    assert len(chunks) >= 1
    assert any(c.metadata.get("fallback") for c in chunks)


def test_empty_file_returns_single_file_chunk():
    chunks = parse_file("empty.py", "")
    assert len(chunks) == 1
    assert chunks[0].type == ChunkType.FILE