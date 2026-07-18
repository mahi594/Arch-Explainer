"""Turns indexed CodeChunks into plain-language ModuleDocs and an overall
architecture overview, using Gemini.

This is the plan doc's step 4: "An LLM reviews related chunks and writes
plain-language explanations of what each part does and how pieces connect."

Two concerns are kept deliberately separate:
- module grouping (deterministic, no LLM, fully unit-testable)
- summarization (calls Gemini, testable via an injected fake generate_fn
  so prompt-building / retry / validation logic never needs network access)

A third concern lives at the network boundary, wrapped around the real
Gemini call only (never around an injected test fake): transient-error
retry with backoff, and a disk cache keyed by (model, prompt) so a run
interrupted by a 503/429 partway through Understand can be re-run without
re-paying for modules that already summarized successfully.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from collections import defaultdict
from pathlib import Path
from typing import Callable, Type, TypeVar

from pydantic import BaseModel, ValidationError

from arch_explainer.models import CodeChunk, ModuleDoc

CHAT_MODEL = "gemini-2.5-flash"  # stable GA model; gemini-1.5-pro (the original choice) was fully shut down in 2026
MAX_VALIDATION_RETRIES = 2
MAX_CONTENT_CHARS_PER_CHUNK = 1500
MAX_TRANSIENT_RETRIES = 4  # separate from MAX_VALIDATION_RETRIES: this is for 5xx/network errors, not bad JSON
DEFAULT_CACHE_PATH = ".cache/summaries.db"

# Takes a prompt string, returns the raw text response.
GenerateFn = Callable[[str], str]

T = TypeVar("T", bound=BaseModel)


def group_chunks_into_modules(chunks: list[CodeChunk]) -> dict[str, list[CodeChunk]]:
    """Groups chunks by their immediate parent directory.

    `arch_explainer/diagram/generator.py` and `arch_explainer/diagram/utils.py`
    both land in module "diagram" — the directory actually containing the
    file, not the top-level package name. Using the top-level directory
    instead would collapse an entire `src/mypackage/*` layout (the common
    case for real Python projects, including this one) into a single
    giant module, which defeats the point of grouping at all. Files
    directly under the repo root (no subdirectory) go to "root". This is
    a heuristic, not a perfect module-boundary detector — per the plan
    doc, a good first draft beats an over-engineered attempt at a
    perfect one.
    """
    groups: dict[str, list[CodeChunk]] = defaultdict(list)
    for chunk in chunks:
        parts = chunk.file_path.strip("/").split("/")
        module_name = parts[-2] if len(parts) > 1 else "root"
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

For dependencies specifically: only list something if you can actually see it
imported or referenced in the code shown above. Do not guess or infer a
dependency based on what a module with this name would typically need — if
the code shown doesn't reveal enough, leave the dependency list minimal or
empty rather than speculating. Never annotate a dependency with a guess like
"(inferred for X)" — dependency names must be exact, bare import names only.
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


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------


class SummaryCache:
    """Persists prompt -> raw model output on disk, so re-running the
    pipeline after a transient failure (e.g. a 503 partway through
    Understand) skips every module that already summarized successfully
    instead of re-spending Gemini calls on them.

    Keyed on a hash of (model, prompt): a module's prompt is fully
    deterministic given its chunks, so unchanged code is always a cache
    hit; changed code produces a different prompt/key and re-summarizes.
    JSON-validation retry prompts (which embed the previous error message)
    are a different string each time, so only first-attempt successes get
    cached — that's the common case and the one worth optimizing for.
    """

    def __init__(self, path: str | Path = DEFAULT_CACHE_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS summaries (
                cache_key TEXT PRIMARY KEY,
                model TEXT NOT NULL,
                response TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    @staticmethod
    def _key(prompt: str, model: str) -> str:
        return hashlib.sha256(f"{model}::{prompt}".encode("utf-8")).hexdigest()

    def get(self, prompt: str, model: str) -> str | None:
        row = self._conn.execute(
            "SELECT response FROM summaries WHERE cache_key = ?",
            (self._key(prompt, model),),
        ).fetchone()
        return row[0] if row else None

    def set(self, prompt: str, model: str, response: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO summaries (cache_key, model, response) VALUES (?, ?, ?)",
            (self._key(prompt, model), model, response),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def with_cache(generate_fn: GenerateFn, cache: SummaryCache, model: str) -> GenerateFn:
    """Wraps a GenerateFn so a cache-hit prompt never touches the network."""

    def cached_generate(prompt: str) -> str:
        cached = cache.get(prompt, model)
        if cached is not None:
            return cached
        response = generate_fn(prompt)
        cache.set(prompt, model, response)
        return response

    return cached_generate


def with_retry(generate_fn: GenerateFn, max_retries: int = MAX_TRANSIENT_RETRIES) -> GenerateFn:
    """Retries transient failures (5xx server errors, rate limiting, network
    blips) with exponential backoff.

    Deliberately separate from — and applied *before* — `_generate_validated`'s
    JSON-validation retry loop. This matters: a past version of this codebase
    had a bug where the raw generate_fn call sat outside any try/except in a
    retry loop, so exceptions like a rate-limit error bypassed retries
    entirely and killed the whole run. Wrapping here means
    `_generate_validated` never has to know transport errors exist — it only
    ever sees a successful raw string, or a final, truly-exhausted exception.
    """

    def retrying_generate(prompt: str) -> str:
        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return generate_fn(prompt)
            except Exception as e:  # noqa: BLE001 - deliberately broad, re-raised below
                last_error = e
                if attempt < max_retries:
                    time.sleep(min(60, 2**attempt))
        raise RuntimeError(f"Gemini call failed after {max_retries + 1} attempts") from last_error

    return retrying_generate


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
        cache_path: str | Path | None = DEFAULT_CACHE_PATH,
    ):
        if generate_fn is None and not api_key:
            raise ValueError("Either api_key or generate_fn must be provided")
        self.model_name = model
        # cache_path only applies when we're building the real network call below —
        # an injected generate_fn (tests, or a caller with its own wrapping) is used as-is.
        self._generate_fn = generate_fn or _default_generate_fn(api_key, model, cache_path)  # type: ignore[arg-type]

    def summarize_module(self, module_name: str, chunks: list[CodeChunk]) -> ModuleDoc:
        prompt = build_module_prompt(module_name, chunks)
        doc = self._generate_validated(prompt, ModuleDoc, context=f"module '{module_name}'")
        # Override whatever name the model chose (e.g. "arch_explainer.models")
        # with the actual deterministic grouping key (e.g. "arch_explainer").
        # Diagram generation matches modules to each other by this name, so it
        # needs to be grounded in real repo structure, not a freeform LLM choice
        # that can vary in phrasing between modules and break that matching.
        doc.name = module_name
        return doc

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


def _default_generate_fn(
    api_key: str,
    model: str,
    cache_path: str | Path | None = DEFAULT_CACHE_PATH,
) -> GenerateFn:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    def generate(prompt: str) -> str:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=8192),
        )
        return response.text

    wrapped = with_retry(generate)
    if cache_path:
        wrapped = with_cache(wrapped, SummaryCache(cache_path), model)
    return wrapped


def create_summarizer(
    api_key: str,
    model: str = CHAT_MODEL,
    cache_path: str | Path | None = DEFAULT_CACHE_PATH,
) -> GeminiSummarizer:
    return GeminiSummarizer(api_key=api_key, model=model, cache_path=cache_path)