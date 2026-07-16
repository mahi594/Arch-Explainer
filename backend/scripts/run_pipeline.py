"""Runs the full pipeline end-to-end against a local folder of Python files.

    python scripts/run_pipeline.py <path-to-code> --owner acme --repo widgets

Deliberately does not touch git or GitHub at all. Per the plan doc, the
Connect step (cloning a remote repo) is just a thin wrapper that hands
this exact same pipeline a local folder path once it's cloned — so
proving the pipeline works here means Step 7 (github_app) only has to
worry about "how do I get files onto disk and commit output back", not
the pipeline logic itself.

`run_pipeline()` takes already-constructed embedder/summarizer/store
objects rather than building them from env vars internally — this is what
makes it testable with fakes, no network or database required to verify
the orchestration logic (does each step run, in order, with the right
data handed to the next one).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

from arch_explainer.diagram.generator import generate_diagrams
from arch_explainer.ingest.parser import parse_file
from arch_explainer.models import ArchitectureDoc, CodeChunk, RepoContext
from arch_explainer.publish.writer import write_docs_to_directory
from arch_explainer.understand.summarizer import group_chunks_into_modules

EXCLUDED_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".pytest_cache", "dist", "build", ".mypy_cache", "docs-output",
}


def discover_python_files(root: Path) -> list[Path]:
    """Walks `root`, returning every .py file, skipping common noise directories."""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(Path(dirpath) / filename)
    return sorted(files)


def ingest_directory(repo_path: Path, files: list[Path]) -> list[CodeChunk]:
    """Parses every discovered file into CodeChunks, using paths relative
    to repo_path (so chunk file_paths match what's in the actual repo,
    not an absolute local filesystem path).
    """
    all_chunks: list[CodeChunk] = []
    for file_path in files:
        rel_path = file_path.relative_to(repo_path).as_posix()
        content = file_path.read_text(encoding="utf-8", errors="replace")
        all_chunks.extend(parse_file(rel_path, content))
    return all_chunks


def run_pipeline(
    repo_path: Path,
    owner: str,
    repo: str,
    output_dir: Path,
    embedder,
    summarizer,
    store,
    commit_sha: str = "local",
    log=print,
) -> ArchitectureDoc:
    """Runs Ingest -> Index -> Understand -> Diagram -> Publish, in order.

    `embedder` needs `.embed_chunks(chunks) -> list[Embedding]` and `.dimensions`.
    `summarizer` needs `.summarize_module(name, chunks) -> ModuleDoc` and
        `.summarize_architecture_overview(owner, repo, modules) -> str`.
    `store` needs `.store_chunks(chunks, vectors_by_id)`. Pass `store=None`
        to skip storage entirely (useful for a quick doc-only dry run).
    """
    log("[1/6] Connect — using local path %s" % repo_path)

    log("[2/6] Ingest — parsing Python files...")
    files = discover_python_files(repo_path)
    if not files:
        raise ValueError(f"No .py files found under {repo_path}")
    all_chunks = ingest_directory(repo_path, files)
    log(f"        {len(files)} files -> {len(all_chunks)} chunks")

    log("[3/6] Index — embedding chunks...")
    embeddings = embedder.embed_chunks(all_chunks)
    vector_by_chunk_id = {e.chunk_id: e.vector for e in embeddings}
    log(f"        {len(embeddings)} embeddings generated")

    if store is not None:
        store.store_chunks(all_chunks, vector_by_chunk_id, model=embedder.model)
        log("        stored in vector database")

    log("[4/6] Understand — summarizing modules...")
    module_groups = group_chunks_into_modules(all_chunks)
    modules = []
    for module_name, chunks in sorted(module_groups.items()):
        log(f"        summarizing '{module_name}' ({len(chunks)} chunks)")
        modules.append(summarizer.summarize_module(module_name, chunks))
    overview = summarizer.summarize_architecture_overview(owner, repo, modules)

    log("[5/6] Diagram — generating Mermaid diagrams...")
    diagrams = generate_diagrams(modules)
    log(f"        {len(diagrams)} diagrams generated")

    log("[6/6] Publish — writing docs...")
    doc_id = f"arch-{owner}-{repo}-{hashlib.sha1(commit_sha.encode()).hexdigest()[:8]}"
    doc = ArchitectureDoc(
        id=doc_id,
        repo_context=RepoContext(owner=owner, repo=repo),
        commit_sha=commit_sha,
        overview=overview,
        modules=modules,
        diagrams=diagrams,
    )
    written = write_docs_to_directory(doc, output_dir)
    for path in written:
        log(f"        wrote {path}")

    return doc


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()

    arg_parser = argparse.ArgumentParser(
        description="Run the Architecture Explainer pipeline against a local folder."
    )
    arg_parser.add_argument("repo_path", type=Path, help="Path to the local folder of Python code")
    arg_parser.add_argument("--owner", default="local", help="Repo owner name, used in generated docs")
    arg_parser.add_argument("--repo", default=None, help="Repo name (defaults to the folder name)")
    arg_parser.add_argument("--output", type=Path, default=Path("./docs-output"), help="Where to write docs")
    arg_parser.add_argument(
        "--skip-storage", action="store_true", help="Skip writing to Postgres (docs-only dry run)"
    )
    arg_parser.add_argument(
        "--embedder-provider",
        choices=["local", "gemini"],
        default=os.environ.get("EMBEDDER_PROVIDER", "local"),
        help="Embedding backend: 'local' (sentence-transformers, free, default) or 'gemini' (API, costs quota)",
    )
    args = arg_parser.parse_args()

    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        sys.exit("GEMINI_API_KEY is not set. Copy .env.example to .env and fill it in.")

    from arch_explainer.index.embedder import create_embedder
    from arch_explainer.understand.summarizer import GeminiSummarizer

    embedder = create_embedder(provider=args.embedder_provider, api_key=gemini_api_key)
    summarizer = GeminiSummarizer(api_key=gemini_api_key)

    store = None
    if not args.skip_storage:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            sys.exit("DATABASE_URL is not set (or pass --skip-storage to run without a database).")
        from arch_explainer.index.store import PgVectorStore

        store = PgVectorStore(database_url, dimensions=embedder.dimensions)
        store.initialize()

    repo_name = args.repo or args.repo_path.resolve().name

    doc = run_pipeline(
        repo_path=args.repo_path,
        owner=args.owner,
        repo=repo_name,
        output_dir=args.output,
        embedder=embedder,
        summarizer=summarizer,
        store=store,
    )

    if store is not None:
        store.close()

    print(f"\nDone. {len(doc.modules)} modules documented, {len(doc.diagrams)} diagrams generated.")
    print(f"Open {args.output / 'index.md'} to view.")


if __name__ == "__main__":
    main()