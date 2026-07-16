# tests

**Purpose:** To ensure the correctness, reliability, and expected behavior of the architecture explanation pipeline. This includes verifying individual component logic (e.g., parsing, embedding, summarization, diagram generation, documentation writing) as well as end-to-end integration of the entire process, including interactions with external systems like a PostgreSQL vector store.

**Description:** Contains unit and integration tests for the `arch_explainer` application's various components.

## Key Files

- `tests/test_diagram.py`
- `tests/test_embedder.py`
- `tests/test_parser.py`
- `tests/test_run_pipeline.py`
- `tests/test_store.py`
- `tests/test_store_integration.py`
- `tests/test_summarizer.py`
- `tests/test_writer.py`

## Dependencies

- pytest
- pathlib
- json
- os
- sys
- arch_explainer.diagram.generator
- arch_explainer.models
- arch_explainer.index.embedder
- arch_explainer.ingest.parser
- run_pipeline
- arch_explainer.index.store
- arch_explainer.understand.summarizer
- arch_explainer.publish.writer

## Public API

### `test_classifies_internal_dependency_as_imports`

- **Type:** `function`
- **Signature:** `def test_classifies_internal_dependency_as_imports():`
- **File:** `tests/test_diagram.py`

Verifies that `extract_relationships` correctly identifies internal module dependencies as 'imports'.

### `test_embed_chunks_batches_requests`

- **Type:** `function`
- **Signature:** `def test_embed_chunks_batches_requests():`
- **File:** `tests/test_embedder.py`

Ensures the `GeminiEmbedder` batches embedding requests efficiently to the underlying API.

### `test_extracts_class_and_methods_with_correct_parent`

- **Type:** `function`
- **Signature:** `def test_extracts_class_and_methods_with_correct_parent():`
- **File:** `tests/test_parser.py`

Confirms that `parse_file` correctly identifies classes and their methods, assigning the correct parent IDs.

### `test_run_pipeline_runs_all_six_steps_in_order`

- **Type:** `function`
- **Signature:** `def test_run_pipeline_runs_all_six_steps_in_order(tmp_path):`
- **File:** `tests/test_run_pipeline.py`

An integration test verifying that the `run_pipeline` function executes all its sub-steps (discovery, ingestion, embedding, summarization, storage, writing) in the correct sequence and produces expected outputs.

### `test_schema_sql_is_idempotent_ddl`

- **Type:** `function`
- **Signature:** `def test_schema_sql_is_idempotent_ddl():`
- **File:** `tests/test_store.py`

Checks that the generated SQL schema for the vector store uses 'IF NOT EXISTS' clauses, making it safe to run multiple times.

### `test_store_and_search_round_trip`

- **Type:** `function`
- **Signature:** `def test_store_and_search_round_trip(store):`
- **File:** `tests/test_store_integration.py`

An integration test that stores a chunk and its vector in a real `PgVectorStore` and then successfully retrieves it via a similarity search.

### `test_groups_chunks_by_top_level_directory`

- **Type:** `function`
- **Signature:** `def test_groups_chunks_by_top_level_directory():`
- **File:** `tests/test_summarizer.py`

Verifies that `group_chunks_into_modules` correctly organizes code chunks into logical modules based on their file paths.

### `test_writes_index_module_and_diagram_files`

- **Type:** `function`
- **Signature:** `def test_writes_index_module_and_diagram_files(tmp_path):`
- **File:** `tests/test_writer.py`

Ensures that `write_docs_to_directory` correctly creates the `index.md`, module-specific Markdown files, and diagram-specific Markdown files in the specified output directory.
