# ingest

**Purpose:** This module exists to transform raw Python source code into structured data (CodeChunk objects, ClassRelationship objects, CallEdge objects). This structured data forms the foundational input for downstream steps in the architecture explainer pipeline, enabling the generation of accurate architectural diagrams and documentation based on the actual code structure, rather than relying on speculative LLM interpretations.

**Description:** The `ingest` module is responsible for processing raw Python source code files to extract structured information. It performs two primary functions: splitting code into meaningful 'chunks' for subsequent embedding and analysis, and deterministically extracting architectural relationships such as class inheritance, composition, and function call graphs.

## Key Files

- `src/arch_explainer/ingest/graph_extractor.py`
- `src/arch_explainer/ingest/parser.py`

## Dependencies

- ast
- collections
- dataclasses
- hashlib
- arch_explainer.models

## Public API

### `ClassRelationship`

- **Type:** `class`
- **Signature:** `class ClassRelationship`
- **File:** `src/arch_explainer/ingest/graph_extractor.py`

Dataclass representing a class and its inheritance/composition relationships, including its name, file path, base classes, and composed-of types.

### `CallEdge`

- **Type:** `class`
- **Signature:** `class CallEdge`
- **File:** `src/arch_explainer/ingest/graph_extractor.py`

Dataclass representing a function or method call, detailing the caller, the raw callee name as written in code, the file path, line number, and the resolved callee's file path.

### `extract_graph`

- **Type:** `function`
- **Signature:** `def extract_graph(file_path: str, content: str) -> tuple[list[ClassRelationship], list[CallEdge], list[str]]`
- **File:** `src/arch_explainer/ingest/graph_extractor.py`

Parses a single Python file's content using AST to extract class relationships, raw function call edges, and a list of all top-level functions and methods defined within that file. Returns empty lists if parsing fails.

### `resolve_and_filter_calls`

- **Type:** `function`
- **Signature:** `def resolve_and_filter_calls(calls: list[CallEdge], defined_callables: list[str], defined_locations: dict[str, str] | None = None) -> list[CallEdge]`
- **File:** `src/arch_explainer/ingest/graph_extractor.py`

Filters a list of raw call edges, keeping only those that resolve to callables actually defined within the repository. It uses a last-segment matching heuristic for resolution and can stamp resolved edges with their target's file path.

### `module_of`

- **Type:** `function`
- **Signature:** `def module_of(file_path: str) -> str`
- **File:** `src/arch_explainer/ingest/graph_extractor.py`

Determines the logical module name for a given file path, typically its immediate parent directory, or 'root' for files directly under the repository root.

### `extract_repo_graph`

- **Type:** `function`
- **Signature:** `def extract_repo_graph(files: dict[str, str]) -> tuple[list[ClassRelationship], list[CallEdge]]`
- **File:** `src/arch_explainer/ingest/graph_extractor.py`

Processes an entire repository (represented as a mapping of file paths to content) to extract all class relationships and then resolves all function call edges across the entire codebase.

### `parse_file`

- **Type:** `function`
- **Signature:** `def parse_file(file_path: str, content: str) -> list[CodeChunk]`
- **File:** `src/arch_explainer/ingest/parser.py`

Parses a single Python file into a list of `CodeChunk` objects. It uses AST for structured chunking (functions, classes, imports, top-level constants) and falls back to fixed-window chunking for files that fail to parse.
