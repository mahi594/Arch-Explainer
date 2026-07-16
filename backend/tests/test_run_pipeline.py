from pathlib import Path

import pytest

from arch_explainer.models import Embedding, ModuleDoc

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_pipeline import discover_python_files, ingest_directory, run_pipeline  # noqa: E402


class FakeEmbedder:
    dimensions = 4

    def __init__(self):
        self.calls = []

    def embed_chunks(self, chunks):
        self.calls.append(list(chunks))
        return [Embedding(chunk_id=c.id, vector=[0.1] * 4, model="fake", dimensions=4) for c in chunks]


class FakeSummarizer:
    def __init__(self):
        self.summarized_modules = []

    def summarize_module(self, module_name, chunks):
        self.summarized_modules.append(module_name)
        return ModuleDoc(
            name=module_name, description=f"desc for {module_name}", purpose="",
            key_files=sorted({c.file_path for c in chunks}), dependencies=[], public_api=[],
        )

    def summarize_architecture_overview(self, owner, repo, modules):
        return f"{owner}/{repo} overview with {len(modules)} modules"


class FakeStore:
    def __init__(self):
        self.stored = None

    def store_chunks(self, chunks, vectors_by_id):
        self.stored = (list(chunks), dict(vectors_by_id))


def write_sample_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "sample_repo"
    (repo / "auth").mkdir(parents=True)
    (repo / "billing").mkdir()
    (repo / "auth" / "login.py").write_text("def login():\n    return True\n")
    (repo / "billing" / "invoice.py").write_text("def create_invoice():\n    pass\n")
    (repo / "README.md").write_text("# not python, should be ignored\n")
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "junk.py").write_text("# should be excluded\n")
    return repo


# ---- discover_python_files ----

def test_discover_finds_python_files_recursively(tmp_path):
    repo = write_sample_repo(tmp_path)
    files = discover_python_files(repo)
    names = {f.name for f in files}
    assert names == {"login.py", "invoice.py"}


def test_discover_excludes_pycache(tmp_path):
    repo = write_sample_repo(tmp_path)
    files = discover_python_files(repo)
    assert not any("junk.py" in str(f) for f in files)


def test_discover_returns_empty_list_for_no_python_files(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "notes.txt").write_text("hello")
    assert discover_python_files(empty) == []


# ---- ingest_directory ----

def test_ingest_directory_produces_relative_file_paths(tmp_path):
    repo = write_sample_repo(tmp_path)
    files = discover_python_files(repo)
    chunks = ingest_directory(repo, files)
    file_paths = {c.file_path for c in chunks}
    assert "auth/login.py" in file_paths
    assert "billing/invoice.py" in file_paths
    # must not contain the absolute tmp_path prefix
    assert not any(str(tmp_path) in fp for fp in file_paths)


# ---- run_pipeline (full orchestration, with fakes) ----

def test_run_pipeline_runs_all_six_steps_in_order(tmp_path):
    repo = write_sample_repo(tmp_path)
    output_dir = tmp_path / "docs-output"
    embedder, summarizer, store = FakeEmbedder(), FakeSummarizer(), FakeStore()

    doc = run_pipeline(
        repo_path=repo, owner="acme", repo="widgets", output_dir=output_dir,
        embedder=embedder, summarizer=summarizer, store=store,
        commit_sha="abc123", log=lambda *a, **k: None,
    )

    assert set(summarizer.summarized_modules) == {"auth", "billing"}
    assert store.stored is not None
    assert (output_dir / "index.md").exists()
    assert (output_dir / "modules" / "auth.md").exists()
    assert (output_dir / "modules" / "billing.md").exists()
    assert doc.overview == "acme/widgets overview with 2 modules"


def test_run_pipeline_skips_storage_when_store_is_none(tmp_path):
    repo = write_sample_repo(tmp_path)
    doc = run_pipeline(
        repo_path=repo, owner="acme", repo="widgets", output_dir=tmp_path / "out",
        embedder=FakeEmbedder(), summarizer=FakeSummarizer(), store=None,
        log=lambda *a, **k: None,
    )
    assert len(doc.modules) == 2  # ran fine without a store at all


def test_run_pipeline_raises_on_empty_repo(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValueError, match="No .py files"):
        run_pipeline(
            repo_path=empty, owner="acme", repo="widgets", output_dir=tmp_path / "out",
            embedder=FakeEmbedder(), summarizer=FakeSummarizer(), store=None,
            log=lambda *a, **k: None,
        )


def test_run_pipeline_generates_diagrams(tmp_path):
    repo = write_sample_repo(tmp_path)
    doc = run_pipeline(
        repo_path=repo, owner="acme", repo="widgets", output_dir=tmp_path / "out",
        embedder=FakeEmbedder(), summarizer=FakeSummarizer(), store=None,
        log=lambda *a, **k: None,
    )
    diagram_ids = {d.id for d in doc.diagrams}
    assert diagram_ids == {"architecture", "dependencies"}