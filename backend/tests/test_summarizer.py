import json

import pytest

from arch_explainer.models import ChunkType, CodeChunk
from arch_explainer.understand.summarizer import (
    GeminiSummarizer,
    build_architecture_overview_prompt,
    build_module_prompt,
    group_chunks_into_modules,
)


def make_chunk(file_path, name="f", chunk_type=ChunkType.FUNCTION, content="def f(): pass"):
    return CodeChunk(
        id=f"{file_path}:{name}", file_path=file_path, start_line=1, end_line=1,
        content=content, type=chunk_type, name=name,
    )


VALID_MODULE_JSON = json.dumps({
    "name": "auth",
    "description": "Handles login and session management",
    "purpose": "Centralizes authentication logic",
    "key_files": ["auth/login.py"],
    "dependencies": ["bcrypt"],
    "public_api": [
        {
            "name": "login",
            "type": "function",
            "signature": "def login(username: str, password: str) -> bool",
            "description": "Authenticates a user",
            "file_path": "auth/login.py",
        }
    ],
})


# ---- group_chunks_into_modules (pure logic, no LLM) ----

def test_groups_chunks_by_top_level_directory():
    chunks = [
        make_chunk("auth/login.py"),
        make_chunk("auth/tokens.py"),
        make_chunk("billing/invoice.py"),
    ]
    groups = group_chunks_into_modules(chunks)
    assert set(groups.keys()) == {"auth", "billing"}
    assert len(groups["auth"]) == 2
    assert len(groups["billing"]) == 1


def test_root_level_files_grouped_under_root():
    chunks = [make_chunk("main.py"), make_chunk("config.py")]
    groups = group_chunks_into_modules(chunks)
    assert set(groups.keys()) == {"root"}
    assert len(groups["root"]) == 2


def test_mixed_root_and_subdirectory_files():
    chunks = [make_chunk("main.py"), make_chunk("auth/login.py")]
    groups = group_chunks_into_modules(chunks)
    assert set(groups.keys()) == {"root", "auth"}


def test_deeply_nested_files_group_by_immediate_parent_not_top_level():
    # A src/<package>/<submodule>/file.py layout should split by submodule,
    # not collapse into one giant module named after the top-level package.
    chunks = [
        make_chunk("src/arch_explainer/diagram/generator.py"),
        make_chunk("src/arch_explainer/ingest/parser.py"),
        make_chunk("src/arch_explainer/ingest/git.py"),
    ]
    groups = group_chunks_into_modules(chunks)
    assert set(groups.keys()) == {"diagram", "ingest"}
    assert len(groups["ingest"]) == 2


# ---- prompt building (pure string logic) ----

def test_module_prompt_includes_module_name_and_files():
    chunks = [make_chunk("auth/login.py", name="login")]
    prompt = build_module_prompt("auth", chunks)
    assert "auth" in prompt
    assert "auth/login.py" in prompt
    assert "def f(): pass" in prompt


def test_architecture_overview_prompt_includes_module_descriptions():
    from arch_explainer.models import ModuleDoc
    modules = [ModuleDoc(name="auth", description="Handles login", purpose="", key_files=[], dependencies=[], public_api=[])]
    prompt = build_architecture_overview_prompt("acme", "widgets", modules)
    assert "acme/widgets" in prompt
    assert "auth" in prompt
    assert "Handles login" in prompt


# ---- GeminiSummarizer (LLM-calling, tested via fake generate_fn) ----

def test_summarize_module_happy_path():
    summarizer = GeminiSummarizer(generate_fn=lambda prompt: VALID_MODULE_JSON)
    doc = summarizer.summarize_module("auth", [make_chunk("auth/login.py")])

    assert doc.name == "auth"
    assert doc.public_api[0].name == "login"


def test_summarize_module_strips_markdown_fences():
    fenced = f"```json\n{VALID_MODULE_JSON}\n```"
    summarizer = GeminiSummarizer(generate_fn=lambda prompt: fenced)
    doc = summarizer.summarize_module("auth", [make_chunk("auth/login.py")])
    assert doc.name == "auth"


def test_summarize_module_retries_on_invalid_json_then_succeeds():
    calls = {"n": 0}

    def flaky_generate(prompt):
        calls["n"] += 1
        if calls["n"] == 1:
            return "{not valid json"
        return VALID_MODULE_JSON

    summarizer = GeminiSummarizer(generate_fn=flaky_generate)
    doc = summarizer.summarize_module("auth", [make_chunk("auth/login.py")])

    assert calls["n"] == 2
    assert doc.name == "auth"
    # the retry prompt should include the original error for the model to self-correct
    assert "failed validation" not in build_module_prompt("auth", [])  # sanity: base prompt is clean


def test_summarize_module_retry_prompt_includes_validation_error():
    seen_prompts = []

    def flaky_generate(prompt):
        seen_prompts.append(prompt)
        if len(seen_prompts) == 1:
            return "{not valid json"
        return VALID_MODULE_JSON

    summarizer = GeminiSummarizer(generate_fn=flaky_generate)
    summarizer.summarize_module("auth", [make_chunk("auth/login.py")])

    assert len(seen_prompts) == 2
    assert "failed validation" in seen_prompts[1]


def test_summarize_module_raises_after_exhausting_retries():
    summarizer = GeminiSummarizer(generate_fn=lambda prompt: "not json at all")

    with pytest.raises(RuntimeError, match="invalid JSON"):
        summarizer.summarize_module("auth", [make_chunk("auth/login.py")])


def test_summarize_module_raises_on_schema_mismatch():
    # Valid JSON, but missing required fields (e.g. "description")
    incomplete = json.dumps({"name": "auth"})
    summarizer = GeminiSummarizer(generate_fn=lambda prompt: incomplete)

    with pytest.raises(RuntimeError, match="invalid JSON"):
        summarizer.summarize_module("auth", [make_chunk("auth/login.py")])


def test_summarize_architecture_overview_returns_plain_text():
    from arch_explainer.models import ModuleDoc
    modules = [ModuleDoc(name="auth", description="Handles login", purpose="", key_files=[], dependencies=[], public_api=[])]
    summarizer = GeminiSummarizer(generate_fn=lambda prompt: "  This system handles authentication.  ")

    overview = summarizer.summarize_architecture_overview("acme", "widgets", modules)

    assert overview == "This system handles authentication."


def test_requires_api_key_or_generate_fn():
    with pytest.raises(ValueError):
        GeminiSummarizer()