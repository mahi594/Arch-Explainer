"""Renders an ArchitectureDoc as Markdown files and writes them to disk.

Deliberately has zero knowledge of GitHub, git, or any specific repo host.
Per the plan doc, "Publish" just means writing docs + diagrams out as
files — either as a standalone docs site, or into a repo's working
directory so they get committed alongside the code. Which of those
happens is a decision made by the *caller* of write_docs_to_directory(),
not by this module. That's what keeps the exact same function usable
whether the pipeline was pointed at a GitHub repo, a local folder, or
anything else with files on disk.
"""

from __future__ import annotations

import re
from pathlib import Path

from arch_explainer.models import ArchitectureDoc, Diagram, ModuleDoc


def slugify(name: str) -> str:
    """Turns a module/diagram name into a filesystem- and URL-safe slug."""
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "untitled"


def render_module_markdown(module: ModuleDoc) -> str:
    lines = [f"# {module.name}", ""]

    if module.purpose:
        lines += [f"**Purpose:** {module.purpose}", ""]

    lines += [f"**Description:** {module.description}", ""]

    if module.key_files:
        lines += ["## Key Files", ""]
        lines += [f"- `{f}`" for f in module.key_files]
        lines.append("")

    if module.dependencies:
        lines += ["## Dependencies", ""]
        lines += [f"- {d}" for d in module.dependencies]
        lines.append("")

    if module.public_api:
        lines += ["## Public API", ""]
        for api in module.public_api:
            lines += [
                f"### `{api.name}`",
                "",
                f"- **Type:** `{api.type}`",
                f"- **Signature:** `{api.signature}`",
                f"- **File:** `{api.file_path}`",
                "",
                api.description,
                "",
            ]

    return "\n".join(lines).rstrip() + "\n"


def render_diagram_markdown(diagram: Diagram) -> str:
    return f"# {diagram.title}\n\n{diagram.description}\n\n```mermaid\n{diagram.mermaid}\n```\n"


def render_overview_markdown(doc: ArchitectureDoc) -> str:
    repo = doc.repo_context
    lines = [
        f"# {repo.owner}/{repo.repo} — Architecture",
        "",
        f"> Auto-generated from commit `{doc.commit_sha[:8]}` on {doc.generated_at.strftime('%Y-%m-%d')}",
        "",
        doc.overview,
        "",
        "## Modules",
        "",
    ]
    for module in doc.modules:
        lines.append(f"- [{module.name}](modules/{slugify(module.name)}.md) — {module.description}")

    if doc.diagrams:
        lines += ["", "## Diagrams", ""]
        for diagram in doc.diagrams:
            lines.append(f"- [{diagram.title}](diagrams/{diagram.id}.md)")

    return "\n".join(lines).rstrip() + "\n"


def write_docs_to_directory(doc: ArchitectureDoc, output_dir: str | Path) -> list[Path]:
    """Writes the full doc set (index + one file per module + one per
    diagram) under `output_dir`. Returns every file written, so a caller
    that wants to commit back to a repo (Step 7) knows exactly what to
    `git add` — this function itself never touches git.
    """
    output_dir = Path(output_dir)
    written: list[Path] = []

    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.md"
    index_path.write_text(render_overview_markdown(doc), encoding="utf-8")
    written.append(index_path)

    if doc.modules:
        modules_dir = output_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        for module in doc.modules:
            path = modules_dir / f"{slugify(module.name)}.md"
            path.write_text(render_module_markdown(module), encoding="utf-8")
            written.append(path)

    if doc.diagrams:
        diagrams_dir = output_dir / "diagrams"
        diagrams_dir.mkdir(exist_ok=True)
        for diagram in doc.diagrams:
            path = diagrams_dir / f"{diagram.id}.md"
            path.write_text(render_diagram_markdown(diagram), encoding="utf-8")
            written.append(path)

    return written