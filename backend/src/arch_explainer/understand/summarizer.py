"""Turns indexed CodeChunks into plain-language ModuleDocs and an overall
architecture overview, using Gemini.

This is the plan doc's step 4: "An LLM reviews related chunks and writes
plain-language explanations of what each part does and how pieces connect."

Two concerns are kept deliberately separate:
- module grouping (deterministic, no LLM, fully unit-testable)
- summarization (calls Gemini, testable via an injected fake generate_fn
  so prompt-building / retry / validation logic never needs network access)
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Callable, Type, TypeVar

from pydantic import BaseModel, ValidationError

from arch_explainer.models import CodeChunk, ModuleDoc

CHAT_MODEL = "models/gemini-1.5-pro"
MAX_VALIDATION_RETRIES = 2
MAX_CONTENT_CHARS_PER_CHUNK = 1500

# Takes a prompt string, returns the raw text response.
GenerateFn = Callable[[str], str]

T = TypeVar("T", bound=BaseModel)


def group_chunks_into_modules(chunks: list[CodeChunk]) -> dict[str, list[CodeChunk]]:
    """Groups chunks by their top-level source directory.

    Deliberately simple for v1: `src/auth/login.py` and `src/auth/tokens.py`
    both land in module "auth". Files directly under the root go to "root".
    This is a heuristic, not a perfect module-boundary detector — per the
    plan doc, a good first draft beats an over-engineered attempt at a
    perfect one.
    """
    groups: dict[str, list[CodeChunk]] = defaultdict(list)
    for chunk in chunks:
        parts = chunk.file_path.strip("/").split("/")
        module_name = parts[0] if len(parts) > 1 else "root"
        groups[module_name].append(chunk)
    return dict(groups)


def _format_chunks_for_prompt(chunks: list[CodeChunk]) -> str:
    sections = []
    for c in chunks:
        content = c.content[:MAX_CONTENT_CHARS_PER_CHUNK]
        name_part = f" {c.name}" if c.name else ""
        header = f"### {c.file_path}:{c.start_line}-{c.end_line} ({c.type.value}{name_part})"
        sections.append(f"{header}\n```python\n{content}\n```")
    return "\n\n".join(sections)


MODULE_DOC_JSON_SHAPE = """{
  "name": "module name",
  "description": "what this module does",
  "purpose": "why it exists, its responsibility",
  "key_files": ["file1.py", "file2.py"],
  "dependencies": ["other_module_or_external_lib"],
  "public_api": [
    {
      "name": "exported_thing",
      "type": "function|class|variable",
      "signature": "def exported_thing(x: int) -> str",
      "description": "what it does",
      "file_path": "path/to/file.py"
    }
  ]
}"""


def build_module_prompt(module_name: str, chunks: list[CodeChunk]) -> str:
    key_files = sorted({c.file_path for c in chunks})
    code = _format_chunks_for_prompt(chunks)
    file_list = "\n".join(f"- {f}" for f in key_files)

    return f"""You are an expert software architect documenting a codebase for new engineers.

Analyze the module "{module_name}", made up of these files:
{file_list}

## Code
{code}

Return ONLY valid JSON matching this exact shape, no markdown fences, no explanation:
{MODULE_DOC_JSON_SHAPE}

Focus on:
1. What this module is responsible for (its purpose, not a line-by-line description)
2. Its genuinely public surface — skip private helpers (leading underscore) unless load-bearing
3. What it depends on, internal or external
"""


def build_architecture_overview_prompt(repo_owner: str, repo_name: str, modules: list[ModuleDoc]) -> str:
    module_summaries = "\n".join(f"- **{m.name}**: {m.description}" for m in modules)

    return f"""You are an expert software architect writing the introduction to a codebase's architecture documentation.

Repository: {repo_owner}/{repo_name}

## Modules
{module_summaries}

Write a 2-3 paragraph overview of this system: what it does, its overall architecture
style (e.g. layered, modular monolith, pipeline), and how the modules above fit together.

Return ONLY the overview text. No JSON, no markdown headers, no preamble.
"""


class GeminiSummarizer:
    """Generates ModuleDocs and an architecture overview via Gemini.

    JSON validation failures trigger a retry where the error is fed back
    into the prompt, asking the model to fix its own output — this
    recovers from the common case of near-valid JSON (trailing comma,
    wrong key name) without failing the whole pipeline run.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = CHAT_MODEL,
        generate_fn: GenerateFn | None = None,
    ):
        if generate_fn is None and not api_key:
            raise ValueError("Either api_key or generate_fn must be provided")
        self.model_name = model
        self._generate_fn = generate_fn or _default_generate_fn(api_key, model)  # type: ignore[arg-type]

    def summarize_module(self, module_name: str, chunks: list[CodeChunk]) -> ModuleDoc:
        prompt = build_module_prompt(module_name, chunks)
        return self._generate_validated(prompt, ModuleDoc, context=f"module '{module_name}'")

    def summarize_architecture_overview(self, repo_owner: str, repo_name: str, modules: list[ModuleDoc]) -> str:
        prompt = build_architecture_overview_prompt(repo_owner, repo_name, modules)
        return self._generate_fn(prompt).strip()

    def _generate_validated(self, prompt: str, model_cls: Type[T], context: str) -> T:
        last_error: Exception | None = None
        current_prompt = prompt

        for attempt in range(MAX_VALIDATION_RETRIES + 1):
            raw = self._generate_fn(current_prompt)
            cleaned = _strip_markdown_fences(raw)
            try:
                data = json.loads(cleaned)
                return model_cls.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                if attempt < MAX_VALIDATION_RETRIES:
                    current_prompt = (
                        f"{prompt}\n\nYour previous response failed validation with this error:\n{e}\n\n"
                        f"Your previous response was:\n{raw}\n\n"
                        f"Return corrected JSON only, matching the required shape exactly."
                    )

        raise RuntimeError(
            f"Gemini returned invalid JSON for {context} after {MAX_VALIDATION_RETRIES + 1} attempts"
        ) from last_error


def _strip_markdown_fences(text: str) -> str:
    """Models frequently wrap JSON in ```json ... ``` despite instructions
    not to — strip it rather than failing validation over formatting.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def _default_generate_fn(api_key: str, model: str) -> GenerateFn:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    client = genai.GenerativeModel(model)

    def generate(prompt: str) -> str:
        response = client.generate_content(
            prompt, generation_config={"temperature": 0.3, "max_output_tokens": 8192}
        )
        return response.text

    return generate


def create_summarizer(api_key: str, model: str = CHAT_MODEL) -> GeminiSummarizer:
    return GeminiSummarizer(api_key=api_key, model=model)