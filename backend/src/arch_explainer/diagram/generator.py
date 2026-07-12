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

from arch_explainer.models import Diagram, ModuleDoc, ModuleRelationship


def extract_relationships(modules: list[ModuleDoc]) -> list[ModuleRelationship]:
    """Turns each module's `dependencies` list into typed edges.

    A dependency is classified "imports" if it matches another module in
    this same repo (case-insensitive name match), otherwise "uses" (an
    external library). This is a heuristic, not perfect resolution —
    dependency names come from the LLM's own summary, so exact matches
    aren't guaranteed — but it's a reasonable first draft per the plan doc.
    """
    module_names = {m.name.lower(): m.name for m in modules}
    relationships: list[ModuleRelationship] = []

    for module in modules:
        for dep in module.dependencies:
            dep_lower = dep.lower().strip()
            if not dep_lower or dep_lower == module.name.lower():
                continue  # skip empty entries and accidental self-references

            if dep_lower in module_names:
                target = module_names[dep_lower]
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
    """Full picture: internal modules plus the key external libraries they depend on."""
    module_ids = {m.name: _sanitize_id(m.name) for m in modules}
    external_names = sorted({r.to_module for r in relationships if r.type == "uses"})
    external_ids = {name: _sanitize_id(f"ext_{name}") for name in external_names}

    lines = ["graph TD"]

    for module in modules:
        lines.append(f'  {module_ids[module.name]}["{module.name}"]')

    for name in external_names:
        lines.append(f'  {external_ids[name]}(["{name}"])')

    for rel in relationships:
        from_id = module_ids.get(rel.from_module)
        to_id = module_ids.get(rel.to_module) if rel.type == "imports" else external_ids.get(rel.to_module)
        if from_id and to_id:
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
        description="High-level view of modules and their key external dependencies.",
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