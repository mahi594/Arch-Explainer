# ingest.parser

**Purpose:** To reliably break down Python source code into meaningful, granular chunks (e.g., functions, classes, imports, top-level constants) for subsequent processing like indexing or explanation. It prioritizes `ast` for accurate parsing but includes a robust fallback mechanism for syntactically invalid files to ensure continuous operation.

**Description:** Parses Python source files into structured `CodeChunk` objects using the `ast` module.

## Key Files

- `src/arch_explainer/ingest/parser.py`

## Dependencies

- arch_explainer.models
- ast
- hashlib

## Public API

### `parse_file`

- **Type:** `function`
- **Signature:** `def parse_file(file_path: str, content: str) -> list[CodeChunk]`
- **File:** `src/arch_explainer/ingest/parser.py`

Parses a single Python file into a list of `CodeChunk` objects. It guarantees to return at least one chunk (a whole-file chunk) even if the file contains syntax errors, preventing downstream systems from needing to handle empty chunk lists.
