"""Deterministic AST-based extraction of class relationships and function
call edges from Python source.

Separate from ingest.parser (which chunks code for embedding) — this is a
second, focused AST pass whose only job is answering "what calls what" and
"what inherits from / is composed of what". Chunking alone doesn't capture
that. Kept deterministic rather than LLM-based for the same reason the
diagram step already is: accuracy should track parseable code structure,
not a model's guess, and it costs no API quota.

Scope (v1, matching this project's existing "good first draft over
over-engineering" philosophy — see group_chunks_into_modules in
understand/summarizer.py): only top-level classes and top-level functions
are analyzed. Nested classes/functions and dynamic dispatch are out of
scope, and calls that can't be resolved to something defined in this repo
are dropped rather than guessed at.
"""

from __future__ import annotations

import ast
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class ClassRelationship:
    class_name: str
    file_path: str
    base_classes: list[str] = field(default_factory=list)
    composed_of: list[str] = field(default_factory=list)  # from self.x = SomeClass(...) in __init__


@dataclass
class CallEdge:
    caller: str  # "func_name" or "ClassName.method_name"
    callee: str  # same shape, as written at the call site (unresolved until resolve_and_filter_calls)
    file_path: str
    line: int
    callee_file_path: str | None = None  # populated by resolve_and_filter_calls; lets callers distinguish cross-module calls


def _dotted_name(node: ast.AST) -> str | None:
    """Turns a Name or Attribute chain into a dotted string, e.g.
    `self.store.save` -> 'self.store.save'. None for anything more complex
    (calls on subscripts, comprehensions, etc.) — those are dropped, not guessed at.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


class _CallCollector(ast.NodeVisitor):
    """Walks one function/method body, recording every call it makes."""

    def __init__(self, caller_name: str, file_path: str):
        self.caller_name = caller_name
        self.file_path = file_path
        self.calls: list[CallEdge] = []

    def visit_Call(self, node: ast.Call) -> None:
        target = _dotted_name(node.func)
        if target:
            self.calls.append(CallEdge(self.caller_name, target, self.file_path, node.lineno))
        self.generic_visit(node)


def _composed_types_in_init(class_node: ast.ClassDef) -> list[str]:
    """Finds `self.x = SomeClass(...)` assignments in __init__ — the common
    composition pattern. Heuristic: a call assigned to a self-attribute
    whose target name is PascalCase is treated as instantiating a class.
    """
    composed = []
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            for stmt in ast.walk(item):
                if not (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)):
                    continue
                is_self_attr = any(
                    isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"
                    for t in stmt.targets
                )
                target_name = _dotted_name(stmt.value.func)
                if is_self_attr and target_name and target_name[:1].isupper():
                    composed.append(target_name)
    return composed


def extract_graph(
    file_path: str, content: str
) -> tuple[list[ClassRelationship], list[CallEdge], list[str]]:
    """Parses one file into (classes, calls, defined_callables).

    `defined_callables` lists every top-level function name and
    "ClassName.method" name this file defines — used later to resolve raw
    call-site text (which may be "self.foo", "obj.foo", or just "foo")
    against what's actually defined in the repo, across files.

    Returns ([], [], []) for files that fail to parse, consistent with
    ingest.parser's guarantee of never crashing the pipeline on one bad file.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [], [], []

    classes: list[ClassRelationship] = []
    calls: list[CallEdge] = []
    defined: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            classes.append(
                ClassRelationship(
                    class_name=node.name,
                    file_path=file_path,
                    base_classes=bases,
                    composed_of=_composed_types_in_init(node),
                )
            )
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    caller_name = f"{node.name}.{item.name}"
                    defined.append(caller_name)
                    collector = _CallCollector(caller_name, file_path)
                    collector.visit(item)
                    calls.extend(collector.calls)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.append(node.name)
            collector = _CallCollector(node.name, file_path)
            collector.visit(node)
            calls.extend(collector.calls)

    return classes, calls, defined


def _last_segment(dotted_name: str) -> str:
    return dotted_name.rsplit(".", 1)[-1]


def resolve_and_filter_calls(
    calls: list[CallEdge],
    defined_callables: list[str],
    defined_locations: dict[str, str] | None = None,
) -> list[CallEdge]:
    """Keeps only calls that resolve to something actually defined in this
    repo, dropping calls to external libraries/builtins/stdlib.

    Resolution matches on the *last* dotted segment (so "self.embed_chunks",
    "embedder.embed_chunks", and bare "embed_chunks" all resolve to the
    real definition "GeminiEmbedder.embed_chunks") — same segment-matching
    approach diagram.generator already uses for module-level dependency
    resolution, applied here at function granularity. Ambiguous — two
    unrelated methods with the same name collide onto one node — but that's
    an acceptable v1 trade-off, not silently wrong data.

    `defined_locations` (name -> file_path) is used to stamp each resolved
    edge with where its target actually lives, so callers can tell a
    cross-module call apart from one that stays inside a single module.
    """
    by_last_segment: dict[str, str] = {}
    for name in defined_callables:
        by_last_segment[_last_segment(name)] = name

    resolved = []
    for edge in calls:
        target = by_last_segment.get(_last_segment(edge.callee))
        if target and target != edge.caller:
            callee_file = (defined_locations or {}).get(target)
            resolved.append(
                CallEdge(caller=edge.caller, callee=target, file_path=edge.file_path, line=edge.line, callee_file_path=callee_file)
            )
    return resolved


def module_of(file_path: str) -> str:
    """Same grouping heuristic as understand.summarizer.group_chunks_into_modules:
    immediate parent directory, or 'root' for files directly under the repo root.
    Duplicated here (not imported) to keep this module dependency-free of
    the rest of the pipeline — it only needs file paths and source text.
    """
    parts = file_path.strip("/").split("/")
    return parts[-2] if len(parts) > 1 else "root"


def extract_repo_graph(
    files: dict[str, str],
) -> tuple[list[ClassRelationship], list[CallEdge]]:
    """Runs extract_graph across every file, then resolves calls repo-wide.

    `files` maps relative file_path -> source content (exactly what
    run_pipeline.py already has after reading each discovered .py file).
    Resolution has to happen after seeing every file, since a call in
    module A might target a definition in module B.
    """
    all_classes: list[ClassRelationship] = []
    all_calls: list[CallEdge] = []
    all_defined: list[str] = []
    defined_locations: dict[str, str] = {}

    for file_path, content in files.items():
        classes, calls, defined = extract_graph(file_path, content)
        all_classes.extend(classes)
        all_calls.extend(calls)
        all_defined.extend(defined)
        for name in defined:
            defined_locations.setdefault(name, file_path)

    resolved_calls = resolve_and_filter_calls(all_calls, all_defined, defined_locations)
    return all_classes, resolved_calls