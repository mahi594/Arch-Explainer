# understand

**Purpose:** Its primary purpose is to bridge the gap between raw code chunks and comprehensive, plain-language documentation, making the codebase more accessible to new engineers. It handles the complexities of LLM interaction, including prompt engineering, JSON validation, transient error retries, and caching of LLM responses to optimize performance and resilience.

**Description:** This module is responsible for generating human-readable documentation for code modules and an overall architecture overview. It takes structured `CodeChunk` data, groups them into logical modules, and then uses a large language model (LLM), specifically Gemini, to produce `ModuleDoc` objects and a high-level architectural summary.

## Key Files

- `src/arch_explainer/understand/summarizer.py`

## Dependencies

- hashlib
- json
- sqlite3
- time
- collections
- pathlib
- typing
- pydantic
- google.genai
- arch_explainer.models

## Public API

### `group_chunks_into_modules`

- **Type:** `function`
- **Signature:** `def group_chunks_into_modules(chunks: list[CodeChunk]) -> dict[str, list[CodeChunk]]`
- **File:** `src/arch_explainer/understand/summarizer.py`

Groups code chunks by their immediate parent directory to form logical modules. This is a deterministic grouping heuristic, treating the parent directory name as the module name.

### `build_module_prompt`

- **Type:** `function`
- **Signature:** `def build_module_prompt(module_name: str, chunks: list[CodeChunk]) -> str`
- **File:** `src/arch_explainer/understand/summarizer.py`

Constructs the detailed prompt for the LLM to summarize a specific code module, including its key files and formatted code content.

### `build_architecture_overview_prompt`

- **Type:** `function`
- **Signature:** `def build_architecture_overview_prompt(repo_owner: str, repo_name: str, modules: list[ModuleDoc]) -> str`
- **File:** `src/arch_explainer/understand/summarizer.py`

Constructs the prompt for the LLM to generate a high-level architecture overview, based on the descriptions of individual modules.

### `GeminiSummarizer`

- **Type:** `class`
- **Signature:** `class GeminiSummarizer`
- **File:** `src/arch_explainer/understand/summarizer.py`

The core class responsible for orchestrating LLM-based summarization. It handles prompt generation, LLM calls, JSON validation, and retries for invalid output, abstracting away the underlying LLM interaction details.

### `summarize_module`

- **Type:** `function`
- **Signature:** `def summarize_module(self, module_name: str, chunks: list[CodeChunk]) -> ModuleDoc`
- **File:** `src/arch_explainer/understand/summarizer.py`

Summarizes a list of code chunks belonging to a specific module into a structured `ModuleDoc` object using the configured LLM. It ensures the module name is consistent with the deterministic grouping.

### `summarize_architecture_overview`

- **Type:** `function`
- **Signature:** `def summarize_architecture_overview(self, repo_owner: str, repo_name: str, modules: list[ModuleDoc]) -> str`
- **File:** `src/arch_explainer/understand/summarizer.py`

Generates a plain-language architectural overview of the entire codebase based on the provided list of `ModuleDoc` objects.

### `create_summarizer`

- **Type:** `function`
- **Signature:** `def create_summarizer(api_key: str, model: str = CHAT_MODEL, cache_path: str | Path | None = DEFAULT_CACHE_PATH) -> GeminiSummarizer`
- **File:** `src/arch_explainer/understand/summarizer.py`

A factory function to create and configure a `GeminiSummarizer` instance. It sets up the LLM client, applies default retry logic for transient network errors, and integrates a disk-based cache for LLM responses.
