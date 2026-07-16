# publish

**Purpose:** To provide a decoupled and environment-agnostic mechanism for persisting architecture documentation in a human-readable and version-control-friendly Markdown format. It acts as the final output stage for the `arch_explainer` tool, ensuring the documentation can be integrated into various workflows (e.g., standalone site, repository commit) without internal knowledge of the deployment context.

**Description:** This module is responsible for rendering an `ArchitectureDoc` object into a set of Markdown files and writing them to a specified directory on disk.

## Key Files

- `src/arch_explainer/publish/writer.py`

## Dependencies

- re
- pathlib
- arch_explainer.models

## Public API

### `slugify`

- **Type:** `function`
- **Signature:** `def slugify(name: str) -> str`
- **File:** `src/arch_explainer/publish/writer.py`

Turns a module or diagram name into a filesystem- and URL-safe slug, suitable for use in file paths or URLs.

### `write_docs_to_directory`

- **Type:** `function`
- **Signature:** `def write_docs_to_directory(doc: ArchitectureDoc, output_dir: str | Path) -> list[Path]`
- **File:** `src/arch_explainer/publish/writer.py`

Writes the complete set of architecture documentation (an index file, one file per module, and one file per diagram) to the specified `output_dir`. It returns a list of all `Path` objects for the files that were written, allowing the caller to manage these files further (e.g., for version control operations like `git add`). This function explicitly avoids any knowledge of version control systems or specific repository hosts.
