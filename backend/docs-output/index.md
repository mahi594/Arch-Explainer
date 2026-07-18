# mahi594/arch-explainer — Architecture

> Auto-generated from commit `local` on 2026-07-18

The `arch-explainer` system is an automated architecture documentation generator designed for Python codebases. Its primary function is to process raw source code, extract structural and semantic information, and then leverage large language models (LLMs) to produce comprehensive, human-readable documentation and visual diagrams of the codebase's architecture. This aims to provide developers with up-to-date and accurate insights into a system's design without manual effort, streamlining the understanding and maintenance of complex software systems.

Architecturally, the system operates as a robust processing pipeline, exhibiting characteristics of a modular monolith where distinct stages are tightly integrated. The workflow is orchestrated by the `scripts` module, initiating with the `ingest` module parsing source code into meaningful chunks and extracting critical architectural relationships like inheritance and call graphs. These processed chunks are then passed to the `index` module, which transforms them into numerical vector embeddings and stores them in a PostgreSQL database for efficient retrieval and similarity search.

Following ingestion and indexing, the `understand` module leverages an LLM (Gemini) to generate detailed module documentation and an overall architectural summary from the structured code data. Concurrently, the `diagram` module takes this structured documentation and deterministically transforms it into visual Mermaid diagrams. Finally, the `publish` module consolidates all generated textual and visual artifacts, transforming them into publishable formats like Markdown and image files, and writes them to a specified output directory, completing the documentation cycle. The `api` module provides an interface for interacting with or triggering this powerful documentation generation workflow.

## Modules

- [api](modules/api.md) — This module is intended to define the public API endpoints for the application. Typically, it would contain the definitions for HTTP routes, handling incoming requests and delegating to business logic.
- [arch_explainer](modules/arch-explainer.md) — Shared data models for the Architecture Explainer pipeline.

This package also contains the following subpackages:
- **api**: This module is intended to define the public API endpoints for the application. Typically, it would contain the definitions for HTTP routes, handling incoming requests and delegating to business logic.
- **diagram**: Transforms structured module documentation into Mermaid diagrams, ensuring deterministic and accurate visual representations of codebase architecture.
- **github_app**: This module currently contains no code.
- **index**: This module is responsible for transforming code chunks into numerical vector embeddings and storing them in a searchable database. It supports both local (sentence-transformers) and cloud-based (Gemini API) embedding providers, includes caching mechanisms to optimize performance and cost, and provides a PostgreSQL-based vector store for persistence and similarity search.
- **ingest**: The `ingest` module is responsible for processing raw Python source code files to extract structured information. It performs two primary functions: splitting code into meaningful 'chunks' for subsequent embedding and analysis, and deterministically extracting architectural relationships such as class inheritance, composition, and function call graphs.
- **publish**: This module is responsible for taking structured architecture documentation (represented by `ArchitectureDoc` and its sub-components) and transforming it into publishable artifacts, specifically image files for diagrams and Markdown files for textual documentation, writing them to a specified output directory.
- **understand**: This module is responsible for generating human-readable documentation for code modules and an overall architecture overview. It takes structured `CodeChunk` data, groups them into logical modules, and then uses a large language model (LLM), specifically Gemini, to produce `ModuleDoc` objects and a high-level architectural summary.
- [diagram](modules/diagram.md) — Transforms structured module documentation into Mermaid diagrams, ensuring deterministic and accurate visual representations of codebase architecture.
- [github_app](modules/github-app.md) — This module currently contains no code.
- [index](modules/index.md) — This module is responsible for transforming code chunks into numerical vector embeddings and storing them in a searchable database. It supports both local (sentence-transformers) and cloud-based (Gemini API) embedding providers, includes caching mechanisms to optimize performance and cost, and provides a PostgreSQL-based vector store for persistence and similarity search.
- [ingest](modules/ingest.md) — The `ingest` module is responsible for processing raw Python source code files to extract structured information. It performs two primary functions: splitting code into meaningful 'chunks' for subsequent embedding and analysis, and deterministically extracting architectural relationships such as class inheritance, composition, and function call graphs.
- [publish](modules/publish.md) — This module is responsible for taking structured architecture documentation (represented by `ArchitectureDoc` and its sub-components) and transforming it into publishable artifacts, specifically image files for diagrams and Markdown files for textual documentation, writing them to a specified output directory.
- [root](modules/root.md) — A standalone diagnostic script designed to identify and isolate issues with database connections, specifically targeting potential hangs or slowness in either the bare `psycopg` driver or the `psycopg_pool` connection management layer.
- [scripts](modules/scripts.md) — This module contains utility scripts for managing the `arch_explainer` application. It includes a one-off database migration script for resizing vector embedding dimensions and the primary end-to-end pipeline runner for processing codebases and generating documentation.
- [tests](modules/tests.md) — The `tests` module contains a comprehensive suite of unit and integration tests designed to ensure the reliability and correctness of the `arch_explainer` application. It covers all major components of the architecture explanation pipeline, from code parsing and embedding to summarization, diagram generation, data storage, and documentation output.
- [understand](modules/understand.md) — This module is responsible for generating human-readable documentation for code modules and an overall architecture overview. It takes structured `CodeChunk` data, groups them into logical modules, and then uses a large language model (LLM), specifically Gemini, to produce `ModuleDoc` objects and a high-level architectural summary.

## Diagrams

- [System Architecture](diagrams/architecture.md)
- [Module Dependencies](diagrams/dependencies.md)
- [Class Relationships (whole repo)](diagrams/classes_all.md)
- [Function Call Graph (whole repo, cross-module only)](diagrams/calls_all.md)
- [Class Relationships: arch_explainer](diagrams/classes_arch_explainer.md)
- [Function Call Graph: diagram](diagrams/calls_diagram.md)
- [Class Relationships: index](diagrams/classes_index.md)
- [Function Call Graph: index](diagrams/calls_index.md)
- [Class Relationships: ingest](diagrams/classes_ingest.md)
- [Function Call Graph: ingest](diagrams/calls_ingest.md)
- [Class Relationships: publish](diagrams/classes_publish.md)
- [Function Call Graph: publish](diagrams/calls_publish.md)
- [Function Call Graph: scripts](diagrams/calls_scripts.md)
- [Class Relationships: tests](diagrams/classes_tests.md)
- [Function Call Graph: tests](diagrams/calls_tests.md)
- [Class Relationships: understand](diagrams/classes_understand.md)
- [Function Call Graph: understand](diagrams/calls_understand.md)
- [Call Sequence: run_pipeline](diagrams/sequence_run_pipeline.md)
