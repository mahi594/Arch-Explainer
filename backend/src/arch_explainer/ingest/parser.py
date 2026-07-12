"""Splits a Python source file into CodeChunks using the standard `ast` module.

Why `ast` instead of tree-sitter: it ships with Python, is guaranteed to
parse valid Python correctly, and needs no extra binding. We chunk on
function/class boundaries (per the plan doc: "meaningful chunks", not
arbitrary line windows) with a fixed-window fallback for files that fail
to parse (e.g. syntax errors in a WIP branch).
"""

from __future__ import annotations

import ast
import hashlib

from arch_explainer.models import ChunkType, CodeChunk

FALLBACK_WINDOW_LINES = 60


def _make_id(file_path: str, start_line: int, chunk_type: ChunkType, name: str | None) -> str:
    """Stable, collision-resistant chunk id — same input always produces the same id,
    which matters for the Index step's upsert-by-id logic.
    """
    raw = f"{file_path}:{start_line}:{chunk_type.value}:{name or ''}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"{chunk_type.value}-{digest}"


def _source_slice(lines: list[str], start_line: int, end_line: int) -> str:
    return "\n".join(lines[start_line - 1 : end_line])


def parse_file(file_path: str, content: str) -> list[CodeChunk]:
    """Parse a single Python file into a list of CodeChunks.

    Always returns at least one chunk (the whole-file chunk) even if the
    file fails to parse, so downstream steps never have to special-case
    "no chunks for this file".
    """
    lines = content.splitlines()
    chunks: list[CodeChunk] = []

    file_chunk = CodeChunk(
        id=_make_id(file_path, 1, ChunkType.FILE, "file"),
        file_path=file_path,
        start_line=1,
        end_line=max(len(lines), 1),
        content=content,
        type=ChunkType.FILE,
        name="file",
    )
    chunks.append(file_chunk)

    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError:
        chunks.extend(_fallback_chunks(file_path, lines, parent_id=file_chunk.id))
        return chunks

    for node in ast.iter_child_nodes(tree):
        chunks.extend(_parse_node(node, file_path, lines, parent_id=file_chunk.id))

    return chunks


def _fallback_chunks(file_path: str, lines: list[str], parent_id: str) -> list[CodeChunk]:
    """Fixed-window chunking for files that don't parse as valid Python."""
    chunks: list[CodeChunk] = []
    for start in range(0, len(lines), FALLBACK_WINDOW_LINES):
        end = min(start + FALLBACK_WINDOW_LINES, len(lines))
        start_line, end_line = start + 1, end
        chunks.append(
            CodeChunk(
                id=_make_id(file_path, start_line, ChunkType.MODULE, f"window-{start_line}"),
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                content=_source_slice(lines, start_line, end_line),
                type=ChunkType.MODULE,
                name=f"window-{start_line}-{end_line}",
                parent_id=parent_id,
                metadata={"fallback": True, "reason": "syntax_error"},
            )
        )
    return chunks


def _parse_node(
    node: ast.AST, file_path: str, lines: list[str], parent_id: str | None
) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        chunks.append(_parse_function(node, file_path, lines, parent_id))
        # Note: we don't recurse into function bodies — nested functions
        # are captured as part of the parent function's content, since a
        # nested helper rarely deserves its own top-level doc entry.

    elif isinstance(node, ast.ClassDef):
        class_chunk = _parse_class(node, file_path, lines, parent_id)
        chunks.append(class_chunk)
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunks.append(_parse_function(child, file_path, lines, class_chunk.id, is_method=True))

    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        chunks.append(_parse_import(node, file_path, lines, parent_id))

    elif isinstance(node, ast.Assign) and _is_top_level_constant(node):
        chunks.append(_parse_assignment(node, file_path, lines, parent_id))

    return chunks


def _parse_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    file_path: str,
    lines: list[str],
    parent_id: str | None,
    is_method: bool = False,
) -> CodeChunk:
    start_line = node.lineno
    end_line = node.end_lineno or start_line
    chunk_type = ChunkType.METHOD if is_method else ChunkType.FUNCTION

    params = [a.arg for a in node.args.args]
    decorators = [_unparse_safe(d) for d in node.decorator_list]

    return CodeChunk(
        id=_make_id(file_path, start_line, chunk_type, node.name),
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        content=_source_slice(lines, start_line, end_line),
        type=chunk_type,
        name=node.name,
        parent_id=parent_id,
        metadata={
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "parameters": params,
            "decorators": decorators,
            "docstring": ast.get_docstring(node),
        },
    )


def _parse_class(
    node: ast.ClassDef, file_path: str, lines: list[str], parent_id: str | None
) -> CodeChunk:
    start_line = node.lineno
    end_line = node.end_lineno or start_line
    bases = [_unparse_safe(b) for b in node.bases]

    return CodeChunk(
        id=_make_id(file_path, start_line, ChunkType.CLASS, node.name),
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        content=_source_slice(lines, start_line, end_line),
        type=ChunkType.CLASS,
        name=node.name,
        parent_id=parent_id,
        metadata={"bases": bases, "docstring": ast.get_docstring(node)},
    )


def _parse_import(
    node: ast.Import | ast.ImportFrom, file_path: str, lines: list[str], parent_id: str | None
) -> CodeChunk:
    start_line = node.lineno
    end_line = node.end_lineno or start_line

    if isinstance(node, ast.ImportFrom):
        module_name = node.module or "."
    else:
        module_name = node.names[0].name if node.names else "unknown"

    return CodeChunk(
        id=_make_id(file_path, start_line, ChunkType.IMPORT, module_name),
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        content=_source_slice(lines, start_line, end_line),
        type=ChunkType.IMPORT,
        name=module_name,
        parent_id=parent_id,
        metadata={"names": [n.name for n in node.names]},
    )


def _parse_assignment(
    node: ast.Assign, file_path: str, lines: list[str], parent_id: str | None
) -> CodeChunk:
    start_line = node.lineno
    end_line = node.end_lineno or start_line
    name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else "unknown"

    return CodeChunk(
        id=_make_id(file_path, start_line, ChunkType.VARIABLE, name),
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        content=_source_slice(lines, start_line, end_line),
        type=ChunkType.VARIABLE,
        name=name,
        parent_id=parent_id,
        metadata={"is_constant": name.isupper()},
    )


def _is_top_level_constant(node: ast.Assign) -> bool:
    """Only chunk simple `NAME = value` assignments — skip tuple/attribute targets."""
    return len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)


def _unparse_safe(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "<unknown>"