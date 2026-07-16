# arch_explainer.models

**Purpose:** To define the canonical data structures and contracts used across all stages of the Architecture Explainer pipeline. It ensures data consistency and interoperability between different processing steps, acting as the foundational schema for the entire system, and is built first to prevent downstream rework.

**Description:** Shared data models for Architecture Explainer. This is the contract every pipeline step (ingest -> index -> understand -> diagram -> publish) reads and writes.

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
- **Signature:** `class ChunkType(str, Enum):`
- **File:** `src/arch_explainer/models.py`

What kind of code unit a chunk represents. Deliberately Python-shaped for v1 (no 'interface', no 'export') — we'll extend this when a second language is added rather than guessing at generic categories now.

### `CodeChunk`

- **Type:** `class`
- **Signature:** `class CodeChunk(BaseModel):`
- **File:** `src/arch_explainer/models.py`

A single unit of parsed source code, ready to be embedded.

### `Embedding`

- **Type:** `class`
- **Signature:** `class Embedding(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `RepoContext`

- **Type:** `class`
- **Signature:** `class RepoContext(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `FileChange`

- **Type:** `class`
- **Signature:** `class FileChange(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `IngestionJob`

- **Type:** `class`
- **Signature:** `class IngestionJob(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `PublicApiItem`

- **Type:** `class`
- **Signature:** `class PublicApiItem(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `ModuleDoc`

- **Type:** `class`
- **Signature:** `class ModuleDoc(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `ModuleRelationship`

- **Type:** `class`
- **Signature:** `class ModuleRelationship(BaseModel):`
- **File:** `src/arch_explainer/models.py`

An edge between two modules — the diagram step turns these into arrows.

### `Diagram`

- **Type:** `class`
- **Signature:** `class Diagram(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `ArchitectureDoc`

- **Type:** `class`
- **Signature:** `class ArchitectureDoc(BaseModel):`
- **File:** `src/arch_explainer/models.py`



### `VectorSearchResult`

- **Type:** `class`
- **Signature:** `class VectorSearchResult(BaseModel):`
- **File:** `src/arch_explainer/models.py`
