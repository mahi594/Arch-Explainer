from arch_explainer.diagram.generator import (
    _sanitize_id,
    extract_relationships,
    generate_architecture_diagram,
    generate_dependency_diagram,
    generate_diagrams,
)
from arch_explainer.models import ModuleDoc


def make_module(name, dependencies=None):
    return ModuleDoc(
        name=name, description=f"{name} module", purpose="", key_files=[],
        dependencies=dependencies or [], public_api=[],
    )


# ---- extract_relationships ----

def test_classifies_internal_dependency_as_imports():
    modules = [make_module("auth", dependencies=["billing"]), make_module("billing")]
    rels = extract_relationships(modules)
    assert len(rels) == 1
    assert rels[0].type == "imports"
    assert rels[0].from_module == "auth"
    assert rels[0].to_module == "billing"


def test_classifies_external_dependency_as_uses():
    modules = [make_module("auth", dependencies=["bcrypt"])]
    rels = extract_relationships(modules)
    assert len(rels) == 1
    assert rels[0].type == "uses"
    assert rels[0].to_module == "bcrypt"


def test_internal_match_is_case_insensitive():
    modules = [make_module("Auth", dependencies=["BILLING"]), make_module("Billing")]
    rels = extract_relationships(modules)
    assert rels[0].type == "imports"
    assert rels[0].to_module == "Billing"  # preserves the *target's* canonical casing


def test_skips_self_reference():
    modules = [make_module("auth", dependencies=["auth"])]
    rels = extract_relationships(modules)
    assert rels == []


def test_skips_empty_dependency_strings():
    modules = [make_module("auth", dependencies=["", "  "])]
    rels = extract_relationships(modules)
    assert rels == []


def test_no_modules_no_relationships():
    assert extract_relationships([]) == []


# ---- _sanitize_id ----

def test_sanitize_id_produces_valid_mermaid_id():
    assert _sanitize_id("my module!!") == "my_module"
    assert _sanitize_id("auth") == "auth"
    assert _sanitize_id("") == "node"


# ---- generate_architecture_diagram ----

def test_architecture_diagram_includes_all_module_nodes():
    modules = [make_module("auth"), make_module("billing")]
    diagram = generate_architecture_diagram(modules, [])
    assert 'auth["auth"]' in diagram.mermaid
    assert 'billing["billing"]' in diagram.mermaid


def test_architecture_diagram_includes_external_nodes_and_edges():
    modules = [make_module("auth", dependencies=["bcrypt"])]
    rels = extract_relationships(modules)
    diagram = generate_architecture_diagram(modules, rels)
    assert "ext_bcrypt" in diagram.mermaid
    assert "-->|uses|" in diagram.mermaid


def test_architecture_diagram_is_valid_mermaid_graph_td():
    modules = [make_module("auth")]
    diagram = generate_architecture_diagram(modules, [])
    assert diagram.mermaid.startswith("graph TD")


def test_architecture_diagram_handles_empty_modules():
    diagram = generate_architecture_diagram([], [])
    assert diagram.mermaid == "graph TD"


# ---- generate_dependency_diagram ----

def test_dependency_diagram_excludes_external_edges():
    modules = [make_module("auth", dependencies=["bcrypt", "billing"]), make_module("billing")]
    rels = extract_relationships(modules)
    diagram = generate_dependency_diagram(modules, rels)
    assert "bcrypt" not in diagram.mermaid
    assert "auth --> billing" in diagram.mermaid


def test_dependency_diagram_is_graph_lr():
    diagram = generate_dependency_diagram([make_module("auth")], [])
    assert diagram.mermaid.startswith("graph LR")


# ---- generate_diagrams (the pipeline entrypoint) ----

def test_generate_diagrams_returns_both_diagram_types():
    modules = [make_module("auth", dependencies=["billing"]), make_module("billing")]
    diagrams = generate_diagrams(modules)
    ids = {d.id for d in diagrams}
    assert ids == {"architecture", "dependencies"}


def test_generate_diagrams_handles_no_modules_without_crashing():
    diagrams = generate_diagrams([])
    assert len(diagrams) == 2