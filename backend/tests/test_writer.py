from arch_explainer.models import ArchitectureDoc, Diagram, ModuleDoc, PublicApiItem, RepoContext
from arch_explainer.publish.writer import (
    render_diagram_markdown,
    render_module_markdown,
    render_overview_markdown,
    slugify,
    write_docs_to_directory,
)


def make_module(name="auth", **overrides):
    defaults = dict(
        name=name, description="Handles login", purpose="Centralize authentication",
        key_files=["auth/login.py"], dependencies=["bcrypt"],
        public_api=[
            PublicApiItem(
                name="login", type="function", signature="def login() -> bool",
                description="Authenticates a user", file_path="auth/login.py",
            )
        ],
    )
    defaults.update(overrides)
    return ModuleDoc(**defaults)


def make_diagram(id="architecture"):
    return Diagram(
        id=id, type="architecture", title="System Architecture",
        mermaid="graph TD\n  a --> b", description="High-level view",
    )


def make_doc(modules=None, diagrams=None, overview="This system manages orders."):
    return ArchitectureDoc(
        id="arch-1",
        repo_context=RepoContext(owner="acme", repo="widgets"),
        commit_sha="abc123def456",
        overview=overview,
        modules=modules if modules is not None else [make_module()],
        diagrams=diagrams if diagrams is not None else [make_diagram()],
    )


# ---- slugify ----

def test_slugify_lowercases_and_replaces_spaces():
    assert slugify("My Module") == "my-module"


def test_slugify_strips_special_characters():
    assert slugify("auth/login!!") == "auth-login"


def test_slugify_empty_string_has_fallback():
    assert slugify("") == "untitled"


# ---- render_module_markdown ----

def test_module_markdown_includes_all_sections():
    md = render_module_markdown(make_module())
    assert "# auth" in md
    assert "**Purpose:** Centralize authentication" in md
    assert "auth/login.py" in md
    assert "bcrypt" in md
    assert "### `login`" in md


def test_module_markdown_omits_empty_optional_sections():
    module = make_module(key_files=[], dependencies=[], public_api=[], purpose="")
    md = render_module_markdown(module)
    assert "## Key Files" not in md
    assert "## Dependencies" not in md
    assert "## Public API" not in md
    assert "**Purpose:**" not in md


# ---- render_diagram_markdown ----

def test_diagram_markdown_wraps_mermaid_in_code_fence():
    md = render_diagram_markdown(make_diagram())
    assert "```mermaid" in md
    assert "graph TD" in md
    assert md.strip().endswith("```")


# ---- render_overview_markdown ----

def test_overview_markdown_includes_repo_and_commit():
    doc = make_doc()
    md = render_overview_markdown(doc)
    assert "acme/widgets" in md
    assert "abc123de" in md  # short SHA
    assert "This system manages orders." in md


def test_overview_markdown_links_to_each_module_and_diagram():
    doc = make_doc()
    md = render_overview_markdown(doc)
    assert "[auth](modules/auth.md)" in md
    assert "[System Architecture](diagrams/architecture.md)" in md


def test_overview_markdown_omits_diagrams_section_when_none():
    doc = make_doc(diagrams=[])
    md = render_overview_markdown(doc)
    assert "## Diagrams" not in md


# ---- write_docs_to_directory ----

def test_writes_index_module_and_diagram_files(tmp_path):
    doc = make_doc()
    written = write_docs_to_directory(doc, tmp_path)

    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "modules" / "auth.md").exists()
    assert (tmp_path / "diagrams" / "architecture.md").exists()
    assert len(written) == 3


def test_writes_only_index_when_no_modules_or_diagrams(tmp_path):
    doc = make_doc(modules=[], diagrams=[])
    written = write_docs_to_directory(doc, tmp_path)

    assert (tmp_path / "index.md").exists()
    assert not (tmp_path / "modules").exists()
    assert not (tmp_path / "diagrams").exists()
    assert len(written) == 1


def test_writing_twice_overwrites_instead_of_duplicating(tmp_path):
    doc = make_doc()
    write_docs_to_directory(doc, tmp_path)
    write_docs_to_directory(doc, tmp_path)

    module_files = list((tmp_path / "modules").glob("*.md"))
    assert len(module_files) == 1


def test_creates_output_directory_if_it_does_not_exist(tmp_path):
    nested = tmp_path / "does" / "not" / "exist" / "yet"
    write_docs_to_directory(make_doc(), nested)
    assert (nested / "index.md").exists()


def test_returned_paths_are_the_actual_files_written(tmp_path):
    written = write_docs_to_directory(make_doc(), tmp_path)
    for path in written:
        assert path.exists()
        assert path.read_text(encoding="utf-8")  # non-empty