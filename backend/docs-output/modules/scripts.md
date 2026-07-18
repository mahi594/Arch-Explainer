# scripts

**Purpose:** To provide operational and development utilities: `migrate_vector_dimensions.py` handles database schema changes for embeddings, while `run_pipeline.py` serves as the main execution entry point for the architecture explanation process, facilitating local development, testing, and demonstration of the core logic.

**Description:** This module contains utility scripts for managing the `arch_explainer` application. It includes a one-off database migration script for resizing vector embedding dimensions and the primary end-to-end pipeline runner for processing codebases and generating documentation.

## Key Files

- `scripts/migrate_vector_dimensions.py`
- `scripts/run_pipeline.py`

## Dependencies

- os
- sys
- pathlib
- argparse
- hashlib
- dotenv
- psycopg
- arch_explainer.diagram.generator
- arch_explainer.ingest.graph_extractor
- arch_explainer.ingest.parser
- arch_explainer.models
- arch_explainer.publish.render_images
- arch_explainer.publish.writer
- arch_explainer.understand.summarizer
- arch_explainer.index.embedder

## Public API

### `main`

- **Type:** `function`
- **Signature:** `def main() -> None`
- **File:** `scripts/migrate_vector_dimensions.py`

Entry point for the vector dimension migration script. It loads environment variables, validates command-line arguments for the new vector dimensions, connects to the PostgreSQL database, truncates the `embeddings` table, and alters the `vector` column to the specified new dimensions.

### `EXCLUDED_DIRS`

- **Type:** `variable`
- **Signature:** `EXCLUDED_DIRS = {...}`
- **File:** `scripts/run_pipeline.py`

A set of directory names (e.g., `.git`, `__pycache__`, `node_modules`) that should be ignored when discovering Python files within a repository.

### `discover_python_files`

- **Type:** `function`
- **Signature:** `def discover_python_files(root: Path) -> list[Path]`
- **File:** `scripts/run_pipeline.py`

Recursively walks the given `root` directory to find all Python (`.py`) files, explicitly skipping common noise directories defined in `EXCLUDED_DIRS`.

### `ingest_directory`

- **Type:** `function`
- **Signature:** `def ingest_directory(repo_path: Path, files: list[Path]) -> list[CodeChunk]`
- **File:** `scripts/run_pipeline.py`

Parses the content of each file in the `files` list into `CodeChunk` objects. File paths within the chunks are made relative to `repo_path`.

### `annotate_subpackages`

- **Type:** `function`
- **Signature:** `def annotate_subpackages(modules: list["ModuleDoc"]) -> None`
- **File:** `scripts/run_pipeline.py`

Modifies the descriptions of `ModuleDoc` objects to include a list of their immediate child modules (subpackages), based on their directory structure. This enhances the generated documentation without requiring additional LLM calls.

### `run_pipeline`

- **Type:** `function`
- **Signature:** `def run_pipeline(repo_path: Path, owner: str, repo: str, output_dir: Path, embedder, summarizer, store, commit_sha: str = "local", sequence_entry_points: list[str] | None = None, render_images: bool = True, log=print) -> ArchitectureDoc`
- **File:** `scripts/run_pipeline.py`

The core orchestration function that executes the entire architecture explanation pipeline: Connect, Ingest, Index, Understand, Diagram, and Publish. It takes pre-configured `embedder`, `summarizer`, and `store` objects to allow for testability and flexibility.

### `main`

- **Type:** `function`
- **Signature:** `def main() -> None`
- **File:** `scripts/run_pipeline.py`

The command-line entry point for `run_pipeline.py`. It parses arguments such as repository path, owner, repo name, output directory, and embedding provider, then initializes necessary components and calls `run_pipeline`.
