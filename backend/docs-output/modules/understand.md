# understand

**Purpose:** To automate the generation of high-level software documentation (module summaries, architecture overviews) from parsed code (`CodeChunk`s). It leverages AI to interpret and synthesize information, while robustly handling common LLM interaction challenges such as transient network errors, output validation, and response caching to ensure reliability and cost-effectiveness.

**Description:** The `understand` module is responsible for transforming raw code chunks into structured, human-readable documentation and an overall architectural overview using large language models (LLMs). It orchestrates the summarization process, handles LLM interaction complexities, and manages data persistence for efficiency.

## Key Files

- `src/arch_explainer/understand/summarizer.py`

## Dependencies

- arch_explainer.models
- pydantic
- google.genai
- sqlite3
- hashlib
- json
- time
- collections
- pathlib
- typing

## Public API

### `group_chunks_into_modules`

- **Type:** `function`
- **Signature:** `def group_chunks_into_modules(chunks: list[CodeChunk]) -> dict[str, list[CodeChunk]]`
- **File:** `src/arch_explainer/understand/summarizer.py`

Groups a flat list of `CodeChunk` objects into logical modules based on their immediate parent directory. This is a deterministic step prior to LLM summarization.

### `create_summarizer`

- **Type:** `function`
- **Signature:** `def create_summarizer(api_key: str, model: str = CHAT_MODEL, cache_path: str | Path | None = DEFAULT_CACHE_PATH) -> GeminiSummarizer`
- **File:** `src/arch_explainer/understand/summarizer.py`

A factory function to instantiate and configure a `GeminiSummarizer`. It sets up the LLM client, applies retry logic for transient errors, and integrates a disk-based cache for responses.

### `GeminiSummarizer`

- **Type:** `class`
- **Signature:** `class GeminiSummarizer(...)`
- **File:** `src/arch_explainer/understand/summarizer.py`

The core class responsible for interacting with the Gemini LLM to generate documentation. It encapsulates the logic for prompt construction, LLM invocation, JSON parsing, Pydantic validation, and validation-error-based retries.

### `summarize_module`

- **Type:** `method`
- **Signature:** `def summarize_module(self, module_name: str, chunks: list[CodeChunk]) -> ModuleDoc`
- **File:** `src/arch_explainer/understand/summarizer.py`

Generates a detailed `ModuleDoc` (including description, purpose, key files, dependencies, and public API) for a given set of `CodeChunk`s belonging to a specific module.

### `summarize_architecture_overview`

- **Type:** `method`
- **Signature:** `def summarize_architecture_overview(self, repo_owner: str, repo_name: str, modules: list[ModuleDoc]) -> str`
- **File:** `src/arch_explainer/understand/summarizer.py`

Generates a 2-3 paragraph plain-language overview of the entire codebase's architecture, describing its style and how individual modules fit together, based on a list of previously generated `ModuleDoc`s.
