# arch_explainer

**Purpose:** To define the canonical data structures and contracts used by all pipeline steps (ingest, index, understand, diagram, publish), ensuring consistency and facilitating data flow throughout the system. Getting these shapes correct is critical as they form the foundation for all downstream processing.

**Description:** Shared data models for the Architecture Explainer pipeline.

This package also contains the following subpackages:
- **api**: This module is intended to define the public API endpoints for the application. Typically, it would contain the definitions for HTTP routes, handling incoming requests and delegating to business logic.
- **diagram**: Transforms structured module documentation into Mermaid diagrams, ensuring deterministic and accurate visual representations of codebase architecture.
- **github_app**: This module currently contains no code.
- **index**: This module is responsible for transforming code chunks into numerical vector embeddings and storing them in a searchable database. It supports both local (sentence-transformers) and cloud-based (Gemini API) embedding providers, includes caching mechanisms to optimize performance and cost, and provides a PostgreSQL-based vector store for persistence and similarity search.
- **ingest**: The `ingest` module is responsible for processing raw Python source code files to extract structured information. It performs two primary functions: splitting code into meaningful 'chunks' for subsequent embedding and analysis, and deterministically extracting architectural relationships such as class inheritance, composition, and function call graphs.
- **publish**: This module is responsible for taking structured architecture documentation (represented by `ArchitectureDoc` and its sub-components) and transforming it into publishable artifacts, specifically image files for diagrams and Markdown files for textual documentation, writing them to a specified output directory.
- **understand**: This module is responsible for generating human-readable documentation for code modules and an overall architecture overview. It takes structured `CodeChunk` data, groups them into logical modules, and then uses a large language model (LLM), specifically Gemini, to produce `ModuleDoc` objects and a high-level architectural summary.

## Key Files

- `src/arch_explainer/models.py`

## Dependencies

- datetime
- enum
- typing
- pydantic

## Public API

### `ChunkType`

- **Type:** `class`
- **Signature:** `class ChunkType(str, Enum)`
- **File:** `src/arch_explainer/models.py`

An enumeration representing the kind of code unit a `CodeChunk` represents (e.g., file, class, function). It is deliberately Python-shaped for v1, with plans to extend for other languages.

### `CodeChunk`

- **Type:** `class`
- **Signature:** `class CodeChunk(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model representing a single unit of parsed source code, ready to be embedded. It includes details like ID, file path, language, line numbers, content, type, name, parent, and metadata.

### `Embedding`

- **Type:** `class`
- **Signature:** `class Embedding(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model holding a vector embedding for a specific `CodeChunk`, including the model used and its dimensions.

### `RepoContext`

- **Type:** `class`
- **Signature:** `class RepoContext(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model defining the context of a repository, including its owner, name, default branch, and an optional GitHub installation ID.

### `FileChange`

- **Type:** `class`
- **Signature:** `class FileChange(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model representing a change to a file within a repository, detailing its path, status (added, modified, removed, renamed), previous path (if renamed), and optional content.

### `IngestionJob`

- **Type:** `class`
- **Signature:** `class IngestionJob(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model representing a job for ingesting repository changes. It tracks the job's ID, associated repository context, commit SHA, file changes, status, and creation/update timestamps.

### `PublicApiItem`

- **Type:** `class`
- **Signature:** `class PublicApiItem(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model describing a single item (function, class, or variable) exposed as part of a module's public API, including its name, type, signature, description, and file path.

### `ModuleDoc`

- **Type:** `class`
- **Signature:** `class ModuleDoc(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model containing comprehensive documentation for a specific software module, including its name, description, purpose, key files, dependencies, and public API items.

### `ModuleRelationship`

- **Type:** `class`
- **Signature:** `class ModuleRelationship(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model representing an edge or relationship between two modules, specifying the 'from' and 'to' modules, the type of relationship (e.g., imports, uses), and a description. These are used by the diagram step.

### `Diagram`

- **Type:** `class`
- **Signature:** `class Diagram(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model representing a generated diagram, including its ID, type (e.g., architecture, dependency), title, Mermaid code representation, and a description.

### `ArchitectureDoc`

- **Type:** `class`
- **Signature:** `class ArchitectureDoc(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model encapsulating the complete architecture documentation for a repository at a specific commit, including an overview, a list of `ModuleDoc` instances, and generated `Diagram`s.

### `VectorSearchResult`

- **Type:** `class`
- **Signature:** `class VectorSearchResult(BaseModel)`
- **File:** `src/arch_explainer/models.py`

A Pydantic model combining a `CodeChunk` with a relevance score, typically used to represent a result from a vector similarity search.
