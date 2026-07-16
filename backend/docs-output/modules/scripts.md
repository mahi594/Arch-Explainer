# scripts

**Purpose:** To provide direct, executable entry points for developers to run the full code analysis pipeline against local codebases, test pipeline components, and manage database schema changes related to vector embeddings. It serves as a demonstration of the pipeline's capabilities and a tool for operational tasks.

**Description:** This module contains standalone utility scripts for the `arch_explainer` project, primarily focused on executing the core architecture explanation pipeline locally and performing database maintenance tasks.

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
- arch_explainer.ingest.parser
- arch_explainer.models
- arch_explainer.publish.writer
- arch_explainer.understand.summarizer
- arch_explainer.index.embedder

## Public API

### `main`

- **Type:** `function`
- **Signature:** `def main() -> None`
- **File:** `scripts/migrate_vector_dimensions.py`

Entry point for the `migrate_vector_dimensions.py` script. It parses command-line arguments for new vector dimensions, loads environment variables, connects to the database, truncates the `embeddings` table, and alters the `vector` column to the specified new dimensions.

### `discover_python_files`

- **Type:** `function`
- **Signature:** `def discover_python_files(root: Path) -> list[Path]`
- **File:** `scripts/run_pipeline.py`

Recursively finds all Python files within a given root directory, excluding common development and build artifacts like `.git`, `__pycache__`, `venv`, etc.

### `ingest_directory`

- **Type:** `function`
- **Signature:** `def ingest_directory(repo_path: Path, files: list[Path]) -> list[CodeChunk]`
- **File:** `scripts/run_pipeline.py`

Parses a list of Python files into `CodeChunk` objects. The file paths within the `CodeChunk` objects are made relative to the provided `repo_path`.

### `run_pipeline`

- **Type:** `function`
- **Signature:** `def run_pipeline(repo_path: Path, owner: str, repo: str, output_dir: Path, embedder, summarizer, store, commit_sha: str = "local", log=print) -> ArchitectureDoc`
- **File:** `scripts/run_pipeline.py`

Executes the full architecture explanation pipeline (Ingest, Index, Understand, Diagram, Publish) against a local repository path. It requires already-constructed embedder, summarizer, and store objects for testability and flexibility.

### `main`

- **Type:** `function`
- **Signature:** `def main() -> None`
- **File:** `scripts/run_pipeline.py`

Entry point for the `run_pipeline.py` script. It parses command-line arguments for the repository path, owner, repo name, output directory, and embedding provider, then initializes the necessary components (embedder, summarizer) and calls `run_pipeline` to execute the full process.
