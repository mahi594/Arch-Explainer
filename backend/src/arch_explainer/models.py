"""Shared data models for Architecture Explainer.

This is the contract every pipeline step (ingest -> index -> understand ->
diagram -> publish) reads and writes. It's built first, before any other
module, because getting this shape wrong means reworking everything
downstream.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChunkType(str, Enum):
    """What kind of code unit a chunk represents.

    Deliberately Python-shaped for v1 (no 'interface', no 'export') — we'll
    extend this when a second language is added rather than guessing at
    generic categories now.
    """

    FILE = "file"
    MODULE = "module"  # fixed-window fallback chunk, used when a file fails to parse
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"
    VARIABLE = "variable"


class CodeChunk(BaseModel):
    """A single unit of parsed source code, ready to be embedded."""

    id: str
    file_path: str
    language: str = "python"
    start_line: int
    end_line: int
    content: str
    type: ChunkType
    name: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Embedding(BaseModel):
    chunk_id: str
    vector: list[float]
    model: str
    dimensions: int


class RepoContext(BaseModel):
    owner: str
    repo: str
    default_branch: str = "main"
    installation_id: Optional[int] = None


class FileChange(BaseModel):
    path: str
    status: str  # added | modified | removed | renamed
    previous_path: Optional[str] = None
    content: Optional[str] = None


class IngestionJob(BaseModel):
    id: str
    repo_context: RepoContext
    commit_sha: str
    changes: list[FileChange] = Field(default_factory=list)
    status: str = "pending"  # pending | processing | completed | failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PublicApiItem(BaseModel):
    name: str
    type: str  # function | class | variable
    signature: str
    description: str
    file_path: str


class ModuleDoc(BaseModel):
    name: str
    description: str
    purpose: str
    key_files: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    public_api: list[PublicApiItem] = Field(default_factory=list)


class ModuleRelationship(BaseModel):
    """An edge between two modules — the diagram step turns these into arrows."""

    from_module: str
    to_module: str
    type: str  # imports | uses
    description: str = ""


class Diagram(BaseModel):
    id: str
    type: str  # architecture | dependency | sequence | component
    title: str
    mermaid: str
    description: str


class ArchitectureDoc(BaseModel):
    id: str
    repo_context: RepoContext
    commit_sha: str
    overview: str
    modules: list[ModuleDoc] = Field(default_factory=list)
    diagrams: list[Diagram] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class VectorSearchResult(BaseModel):
    chunk: CodeChunk
    score: float