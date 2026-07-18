"""Turns ModuleDocs into Mermaid diagrams.

Deliberately mostly deterministic rather than another LLM call: the plan
doc's step 5 ("Diagram") renders the Understand step's already-validated
structured output, instead of asking a model to freehand a diagram from
raw code a second time. This also means diagram accuracy tracks module-doc
accuracy directly, rather than introducing a second, independent source
of error on top of it.
"""

from __future__ import annotations

import re
from pathlib import Path

from arch_explainer.models import Diagram, ModuleDoc, ModuleRelationship

# Every module touching os/json/pathlib/etc. is true but not interesting —
# collapsing these into one shared "Python stdlib" node keeps the whole-repo
# architecture diagram legible instead of exploding into dozens of near-
# identical boxes that add clutter without adding decision-relevant signal.
STDLIB_MODULES = {
    "os", "sys", "re", "json", "ast", "time", "enum", "typing", "pathlib",
    "hashlib", "sqlite3", "collections", "dataclasses", "datetime",
    "argparse", "subprocess", "tempfile", "shutil", "functools", "itertools",
    "logging", "io", "csv", "uuid", "math", "random", "threading", "asyncio",
    "unittest", "abc", "contextlib", "copy", "pickle", "socket", "struct",
    "textwrap", "traceback", "warnings", "weakref", "string", "urllib",
    "http", "email", "base64", "hmac", "secrets", "decimal", "fractions",
    "statistics", "operator", "glob",
}


def _external_node_key(name: str) -> str:
    """Groups any stdlib dependency under one shared key, leaves everything
    else (real third-party libraries) as its own distinct node."""
    root = name.split(".")[0].lower().strip()
    return "stdlib" if root in STDLIB_MODULES else name


def _build_internal_resolvers(
    modules: list[ModuleDoc],
) -> tuple[dict[str, str], dict[str, str]]:
    """Builds two lookup maps used to recognize a dependency string as
    actually referring to one of *this repo's* modules, even when the LLM
    didn't phrase it as that module's exact display name.

    LLM-written dependency lists are inconsistent by nature — the same
    internal module gets referenced as its short name ("diagram"), a full
    dotted import path ("arch_explainer.diagram.generator"), or just a
    filename ("run_pipeline"). Matching only on exact module-name equality
    (the original approach) silently misclassifies most of these as
    external libraries. Two maps fix this:

    - `module_names`: lowercased module name -> real module name
    - `file_stem_to_module`: lowercased filename (no extension) -> owning
      module name, built from every module's key_files. This catches
      references to a specific file (e.g. "run_pipeline") that don't
      textually match the module's own name (e.g. "scripts").
    """
    module_names = {m.name.lower(): m.name for m in modules}
    file_stem_to_module: dict[str, str] = {}
    for m in modules:
        for f in m.key_files:
            stem = Path(f).stem.lower()
            file_stem_to_module.setdefault(stem, m.name)
    return module_names, file_stem_to_module


def _resolve_internal_target(
    dep_lower: str,
    module_names: dict[str, str],
    file_stem_to_module: dict[str, str],
) -> str | None:
    """Returns the real module name this dependency string refers to, if
    it's internal to the repo — checking, in order: exact name match, then
    each dotted-path segment (deepest first, so "arch_explainer.diagram.generator"
    resolves to "diagram" rather than the more general "arch_explainer"),
    then a bare filename match. Returns None if nothing matches, meaning
    this is genuinely an external dependency.
    """
    if dep_lower in module_names:
        return module_names[dep_lower]

    segments = dep_lower.split(".")
    for segment in reversed(segments):
        if segment in module_names:
            return module_names[segment]
        if segment in file_stem_to_module:
            return file_stem_to_module[segment]

    return None


def extract_relationships(modules: list[ModuleDoc]) -> list[ModuleRelationship]:
    """Turns each module's `dependencies` list into typed edges.

    A dependency is classified "imports" if it resolves to another module
    in this same repo (via `_resolve_internal_target`), otherwise "uses"
    (an external library). Still a heuristic — dependency names come from
    the LLM's own summary, not static import analysis — but resolving
    dotted paths and filenames, not just exact names, catches the large
    majority of internal references that used to be misfiled as external.
    """
    module_names, file_stem_to_module = _build_internal_resolvers(modules)
    relationships: list[ModuleRelationship] = []

    for module in modules:
        for dep in module.dependencies:
            dep_lower = dep.lower().strip()
            if not dep_lower:
                continue

            target = _resolve_internal_target(dep_lower, module_names, file_stem_to_module)

            if target is not None:
                if target.lower() == module.name.lower():
                    continue  # self-reference (e.g. two files in the same module) — not a useful edge
                relationships.append(
                    ModuleRelationship(
                        from_module=module.name,
                        to_module=target,
                        type="imports",
                        description=f"{module.name} imports from {target}",
                    )
                )
            else:
                relationships.append(
                    ModuleRelationship(
                        from_module=module.name,
                        to_module=dep,
                        type="uses",
                        description=f"{module.name} uses external dependency {dep}",
                    )
                )

    return relationships


def _sanitize_id(name: str) -> str:
    """Mermaid node IDs can't contain spaces/punctuation — collapse to underscores."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip())
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized or "node"


def generate_architecture_diagram(
    modules: list[ModuleDoc], relationships: list[ModuleRelationship]
) -> Diagram:
    """Full picture: internal modules plus the external libraries they
    depend on. Standard-library dependencies are collapsed into a single
    "Python stdlib" node (see _external_node_key) rather than one box per
    module — otherwise the diagram is dominated by low-signal edges to
    os/json/pathlib/etc. and the actually-interesting third-party
    dependencies (pydantic, google.genai, psycopg...) get lost in the noise.
    """
    module_ids = {m.name: _sanitize_id(m.name) for m in modules}

    external_keys = sorted({_external_node_key(r.to_module) for r in relationships if r.type == "uses"})
    external_ids = {key: _sanitize_id(f"ext_{key}") for key in external_keys}
    external_labels = {key: ("Python stdlib" if key == "stdlib" else key) for key in external_keys}

    lines = ["graph TD"]

    for module in modules:
        lines.append(f'  {module_ids[module.name]}["{module.name}"]')

    for key in external_keys:
        lines.append(f'  {external_ids[key]}(["{external_labels[key]}"])')

    seen_edges = set()
    for rel in relationships:
        from_id = module_ids.get(rel.from_module)
        if rel.type == "imports":
            to_id = module_ids.get(rel.to_module)
        else:
            to_id = external_ids.get(_external_node_key(rel.to_module))
        if not (from_id and to_id):
            continue
        edge_key = (from_id, rel.type, to_id)
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        lines.append(f"  {from_id} -->|{rel.type}| {to_id}")

    if module_ids:
        lines.append("  classDef moduleNode fill:#0ea5e9,color:#fff,stroke:#0369a1,stroke-width:2px;")
        lines.append(f"  class {','.join(module_ids.values())} moduleNode;")
    if external_ids:
        lines.append("  classDef externalNode fill:#6b7280,color:#fff,stroke:#374151,stroke-width:1px;")
        lines.append(f"  class {','.join(external_ids.values())} externalNode;")

    return Diagram(
        id="architecture",
        type="architecture",
        title="System Architecture",
        mermaid="\n".join(lines),
        description="High-level view of modules and the external libraries they depend on (standard library collapsed into one node).",
    )


def generate_dependency_diagram(
    modules: list[ModuleDoc], relationships: list[ModuleRelationship]
) -> Diagram:
    """Internal-only view: how modules in this repo depend on each other, no external noise."""
    module_ids = {m.name: _sanitize_id(m.name) for m in modules}
    internal = [r for r in relationships if r.type == "imports"]

    lines = ["graph LR"]
    for module in modules:
        lines.append(f'  {module_ids[module.name]}["{module.name}"]')
    for rel in internal:
        from_id = module_ids.get(rel.from_module)
        to_id = module_ids.get(rel.to_module)
        if from_id and to_id:
            lines.append(f"  {from_id} --> {to_id}")

    return Diagram(
        id="dependencies",
        type="dependency",
        title="Module Dependencies",
        mermaid="\n".join(lines),
        description="Which modules in this repo depend on which others.",
    )


def generate_diagrams(modules: list[ModuleDoc]) -> list[Diagram]:
    """Convenience entrypoint used by the pipeline: extracts relationships
    and builds every v1 diagram type in one call.
    """
    relationships = extract_relationships(modules)
    return [
        generate_architecture_diagram(modules, relationships),
        generate_dependency_diagram(modules, relationships),
    ]


# --------------------------------------------------------------------------
# Class / call-graph / sequence diagrams (from ingest.graph_extractor output)
# --------------------------------------------------------------------------


def generate_class_diagram(
    classes: list["ClassRelationship"], title: str = "Class Relationships", diagram_id: str = "classes"
) -> Diagram:
    """Mermaid classDiagram: inheritance (`<|--`) and composition (`*--`).

    Only classes that appear in at least one edge get drawn — a class with
    no detected inheritance or composition adds a floating, disconnected
    box that clutters a diagram whose entire purpose is showing
    relationships, without conveying any relationship itself.
    """
    edge_lines: list[str] = []
    referenced: set[str] = set()

    for c in classes:
        cid = _sanitize_id(c.class_name)
        for base in c.base_classes:
            base_id = _sanitize_id(base)
            edge_lines.append(f"  {base_id} <|-- {cid}")
            referenced.add(base_id)
            referenced.add(cid)
        for comp in c.composed_of:
            comp_id = _sanitize_id(comp)
            edge_lines.append(f"  {cid} *-- {comp_id}")
            referenced.add(cid)
            referenced.add(comp_id)

    lines = ["classDiagram"]
    declared = set()
    for c in classes:
        cid = _sanitize_id(c.class_name)
        if cid in referenced and cid not in declared:
            lines.append(f"  class {cid}")
            declared.add(cid)
    lines.extend(edge_lines)

    if len(lines) == 1:
        lines.append("  class NoRelationshipsDetected")

    omitted = len(classes) - len(declared)
    description = "Inheritance and composition between classes."
    if omitted > 0:
        description += f" {omitted} class(es) with no detected relationship are omitted from this view."

    return Diagram(id=diagram_id, type="class", title=title, mermaid="\n".join(lines), description=description)


def generate_call_graph(
    calls: list["CallEdge"],
    title: str = "Function Call Graph",
    diagram_id: str = "calls",
    cross_module_only: bool = False,
) -> Diagram:
    """Mermaid graph TD of resolved (repo-internal only) call edges.

    Expects `calls` already run through graph_extractor.resolve_and_filter_calls
    — this function just renders, it doesn't decide what counts as internal.

    `cross_module_only=True` keeps only calls where caller and callee live
    in different modules — used for the whole-repo view, where showing
    every intra-module call as well produces a dense, low-signal hairball.
    Per-module call graphs should leave this False to get full detail.
    """
    if cross_module_only:
        from arch_explainer.ingest.graph_extractor import module_of

        calls = [
            c for c in calls
            if c.callee_file_path and module_of(c.file_path) != module_of(c.callee_file_path)
        ]

    node_ids: dict[str, str] = {}
    lines = ["graph TD"]

    def node_id(name: str) -> str:
        if name not in node_ids:
            node_ids[name] = _sanitize_id(name)
            lines.append(f'  {node_ids[name]}["{name}"]')
        return node_ids[name]

    edge_lines = []
    seen_edges = set()
    for edge in calls:
        key = (edge.caller, edge.callee)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        from_id = node_id(edge.caller)
        to_id = node_id(edge.callee)
        edge_lines.append(f"  {from_id} --> {to_id}")

    lines.extend(edge_lines)
    if len(edge_lines) == 0:
        lines.append('  none["no cross-module calls detected"]' if cross_module_only else '  none["no resolved calls detected"]')

    description = (
        "Which modules' functions call into other modules (intra-module calls omitted for clarity)."
        if cross_module_only
        else "Which functions/methods call which others, resolved to repo-internal definitions only."
    )

    return Diagram(id=diagram_id, type="call_graph", title=title, mermaid="\n".join(lines), description=description)


def generate_sequence_diagram(
    calls: list["CallEdge"], entry_point: str, max_depth: int = 4
) -> Diagram:
    """Mermaid sequenceDiagram, breadth-first from `entry_point` (e.g. "run_pipeline"
    or "GeminiEmbedder.embed_chunks") out to `max_depth` levels.

    Only meaningful for one traced flow at a time — there's no single
    "whole repo" entry point, unlike the other diagram types.
    """
    call_map: dict[str, list[str]] = {}
    for edge in calls:
        call_map.setdefault(edge.caller, []).append(edge.callee)

    lines = ["sequenceDiagram"]
    visited_edges = set()
    queue = [(entry_point, 0)]
    while queue:
        caller, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        for callee in call_map.get(caller, []):
            key = (caller, callee)
            if key in visited_edges:
                continue
            visited_edges.add(key)
            lines.append(f"  {_sanitize_id(caller)}->>+{_sanitize_id(callee)}: call")
            queue.append((callee, depth + 1))

    if len(lines) == 1:
        lines.append(f"  Note over {_sanitize_id(entry_point)}: no resolved internal calls found from this entry point")

    return Diagram(
        id=f"sequence_{_sanitize_id(entry_point)}",
        type="sequence",
        title=f"Call Sequence: {entry_point}",
        mermaid="\n".join(lines),
        description=f"Traced call sequence starting from {entry_point}, depth-limited to {max_depth}.",
    )


def generate_class_and_call_diagrams(
    classes: list["ClassRelationship"],
    calls: list["CallEdge"],
    sequence_entry_points: list[str] | None = None,
) -> list[Diagram]:
    """Builds the whole-repo class + call diagrams, plus one per-module pair,
    plus one sequence diagram per requested entry point.

    Whole-repo call graphs get large fast, so unlike the per-module view
    (full detail), this doesn't attempt to trim the whole-repo one — if it's
    too dense to be useful on a big repo, that's a signal to look at the
    per-module diagrams instead, not a reason to silently drop edges.
    """
    from arch_explainer.ingest.graph_extractor import module_of

    diagrams: list[Diagram] = []

    if classes:
        diagrams.append(generate_class_diagram(classes, title="Class Relationships (whole repo)", diagram_id="classes_all"))
    if calls:
        diagrams.append(
            generate_call_graph(
                calls, title="Function Call Graph (whole repo, cross-module only)", diagram_id="calls_all", cross_module_only=True
            )
        )

    classes_by_module: dict[str, list["ClassRelationship"]] = {}
    for c in classes:
        classes_by_module.setdefault(module_of(c.file_path), []).append(c)

    calls_by_module: dict[str, list["CallEdge"]] = {}
    for call in calls:
        calls_by_module.setdefault(module_of(call.file_path), []).append(call)

    for module_name in sorted(set(classes_by_module) | set(calls_by_module)):
        mod_classes = classes_by_module.get(module_name, [])
        mod_calls = calls_by_module.get(module_name, [])
        if mod_classes:
            diagrams.append(
                generate_class_diagram(
                    mod_classes, title=f"Class Relationships: {module_name}", diagram_id=f"classes_{_sanitize_id(module_name)}"
                )
            )
        if mod_calls:
            diagrams.append(
                generate_call_graph(
                    mod_calls, title=f"Function Call Graph: {module_name}", diagram_id=f"calls_{_sanitize_id(module_name)}"
                )
            )

    for entry_point in sequence_entry_points or []:
        diagrams.append(generate_sequence_diagram(calls, entry_point))

    return diagrams