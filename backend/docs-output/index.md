# mahi594/arch-explainer — Architecture

> Auto-generated from commit `local` on 2026-07-15

The `arch-explainer` system is an automated architecture documentation generator, designed to transform raw codebases into comprehensive, human-readable architectural overviews, structured module documentation, and visual diagrams. Its core purpose is to demystify complex code by leveraging advanced parsing, vector indexing, and large language models (LLMs) to extract, understand, and articulate a system's design. The system operates primarily as a sophisticated data processing pipeline, where each stage progressively refines and enriches the understanding of the codebase.

This pipeline architecture is clearly defined by a series of sequential steps, orchestrated around shared data models (`arch_explainer.models`) that serve as contracts between stages. The journey begins with the `ingest.parser` module, which meticulously dissects Python source files into granular `CodeChunk` objects. These chunks are then fed into the `index` module, responsible for generating and managing vector embeddings, enabling efficient semantic search and retrieval. The heart of the explanation process resides in the `understand` module, which employs LLMs to transform these indexed code chunks into structured `ModuleDoc` and an overarching `ArchitectureDoc`.

Finally, the processed architectural insights are made tangible through the `diagram` module, which renders visual representations using Mermaid, and the `publish` module, which generates detailed Markdown documentation. External interaction is facilitated by the `api` module, exposing endpoints for clients or services to trigger the explanation process or retrieve generated artifacts. Additionally, the `github_app` module provides a dedicated integration layer for seamless interaction with GitHub repositories, potentially initiating the pipeline upon code changes, while `scripts` offers local execution and maintenance utilities.

## Modules

- [api](modules/api.md) — This module is intended to define and expose the application's public API endpoints. It serves as the external interface for clients or other services to interact with the application's functionality.
- [arch_explainer.models](modules/arch-explainer-models.md) — Shared data models for Architecture Explainer. This is the contract every pipeline step (ingest -> index -> understand -> diagram -> publish) reads and writes.
- [diagram](modules/diagram.md) — Turns structured `ModuleDoc` data into Mermaid diagrams.
- [github_app](modules/github-app.md) — This module is designed to encapsulate all logic related to integrating with GitHub as a GitHub App. Based on its name, it would typically handle webhook reception, authentication, and interaction with the GitHub API to perform actions or respond to events.
- [index](modules/index.md) — This module is responsible for the entire lifecycle of creating, caching, storing, and retrieving vector embeddings for `CodeChunk` objects. It provides flexible options for embedding generation (local or cloud-based) and robust persistence and search capabilities using a PostgreSQL database with the `pgvector` extension.
- [ingest.parser](modules/ingest-parser.md) — Parses Python source files into structured `CodeChunk` objects using the `ast` module.
- [publish](modules/publish.md) — This module is responsible for rendering an `ArchitectureDoc` object into a set of Markdown files and writing them to a specified directory on disk.
- [root](modules/root.md) — A standalone diagnostic script for testing PostgreSQL database connectivity and identifying potential bottlenecks or issues at different layers (bare connection vs. connection pool).
- [scripts](modules/scripts.md) — This module contains standalone utility scripts for the `arch_explainer` project, primarily focused on executing the core architecture explanation pipeline locally and performing database maintenance tasks.
- [tests](modules/tests.md) — Contains unit and integration tests for the `arch_explainer` application's various components.
- [understand](modules/understand.md) — The `understand` module is responsible for transforming raw code chunks into structured, human-readable documentation and an overall architectural overview using large language models (LLMs). It orchestrates the summarization process, handles LLM interaction complexities, and manages data persistence for efficiency.

## Diagrams

- [System Architecture](diagrams/architecture.md)
- [Module Dependencies](diagrams/dependencies.md)
