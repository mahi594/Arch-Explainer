# publish

**Purpose:** To finalize and output the generated architectural insights into a user-consumable format (Markdown and images), independent of the final deployment or hosting mechanism. It acts as the final step in the documentation generation pipeline, preparing files for commitment to a repository or deployment as a static site.

**Description:** This module is responsible for taking structured architecture documentation (represented by `ArchitectureDoc` and its sub-components) and transforming it into publishable artifacts, specifically image files for diagrams and Markdown files for textual documentation, writing them to a specified output directory.

## Key Files

- `src/arch_explainer/publish/render_images.py`
- `src/arch_explainer/publish/writer.py`

## Dependencies

- shutil
- subprocess
- tempfile
- pathlib
- re
- arch_explainer.models

## Public API

### `MermaidCliNotAvailable`

- **Type:** `class`
- **Signature:** `class MermaidCliNotAvailable(RuntimeError):`
- **File:** `src/arch_explainer/publish/render_images.py`

Raised when npx/node isn't on PATH — caller decides whether to skip image rendering or fail the whole pipeline over it.

### `render_diagram_image`

- **Type:** `function`
- **Signature:** `def render_diagram_image(diagram: Diagram, output_dir: Path, fmt: str = "png") -> Path:`
- **File:** `src/arch_explainer/publish/render_images.py`

Renders one Diagram's Mermaid source to `output_dir/{diagram.id}.{fmt}`.

### `render_diagram_images`

- **Type:** `function`
- **Signature:** `def render_diagram_images(diagrams: list[Diagram], output_dir: Path, fmt: str = "png", log=print) -> list[Path]:`
- **File:** `src/arch_explainer/publish/render_images.py`

Renders every diagram to an image file, skipping (not failing the whole pipeline on) any single diagram that errors — one bad diagram shouldn't block the rest of Publish from finishing.

### `slugify`

- **Type:** `function`
- **Signature:** `def slugify(name: str) -> str:`
- **File:** `src/arch_explainer/publish/writer.py`

Turns a module/diagram name into a filesystem- and URL-safe slug.

### `render_module_markdown`

- **Type:** `function`
- **Signature:** `def render_module_markdown(module: ModuleDoc) -> str:`
- **File:** `src/arch_explainer/publish/writer.py`

Generates a Markdown string representation for a given ModuleDoc.

### `render_diagram_markdown`

- **Type:** `function`
- **Signature:** `def render_diagram_markdown(diagram: Diagram) -> str:`
- **File:** `src/arch_explainer/publish/writer.py`

Generates a Markdown string representation for a given Diagram, including its Mermaid source.

### `render_overview_markdown`

- **Type:** `function`
- **Signature:** `def render_overview_markdown(doc: ArchitectureDoc) -> str:`
- **File:** `src/arch_explainer/publish/writer.py`

Generates the main Markdown overview document for the entire ArchitectureDoc, including links to modules and diagrams.

### `write_docs_to_directory`

- **Type:** `function`
- **Signature:** `def write_docs_to_directory(doc: ArchitectureDoc, output_dir: str | Path) -> list[Path]:`
- **File:** `src/arch_explainer/publish/writer.py`

Writes the full doc set (index + one file per module + one per diagram) under `output_dir`. Returns every file written, so a caller that wants to commit back to a repo (Step 7) knows exactly what to `git add` — this function itself never touches git.
