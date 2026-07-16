# diagram

**Purpose:** To deterministically generate accurate Mermaid diagrams (architecture and dependency) from validated structured `ModuleDoc` output, ensuring diagram accuracy tracks module documentation accuracy directly rather than introducing new errors.

**Description:** Turns structured `ModuleDoc` data into Mermaid diagrams.

## Key Files

- `src/arch_explainer/diagram/generator.py`

## Dependencies

- re
- arch_explainer.models

## Public API

### `extract_relationships`

- **Type:** `function`
- **Signature:** `def extract_relationships(modules: list[ModuleDoc]) -> list[ModuleRelationship]`
- **File:** `src/arch_explainer/diagram/generator.py`

Turns each module's `dependencies` list into typed edges. A dependency is classified 'imports' if it matches another module in this same repo (case-insensitive name match), otherwise 'uses' (an external library). This is a heuristic, not perfect resolution — dependency names come from the LLM's own summary, so exact matches aren't guaranteed — but it's a reasonable first draft per the plan doc.

### `generate_architecture_diagram`

- **Type:** `function`
- **Signature:** `def generate_architecture_diagram(modules: list[ModuleDoc], relationships: list[ModuleRelationship]) -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid diagram representing the full system architecture, including internal modules and the key external libraries they depend on.

### `generate_dependency_diagram`

- **Type:** `function`
- **Signature:** `def generate_dependency_diagram(modules: list[ModuleDoc], relationships: list[ModuleRelationship]) -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid diagram showing an internal-only view of how modules within this repository depend on each other, excluding external dependencies.

### `generate_diagrams`

- **Type:** `function`
- **Signature:** `def generate_diagrams(modules: list[ModuleDoc]) -> list[Diagram]`
- **File:** `src/arch_explainer/diagram/generator.py`

A convenience entrypoint used by the pipeline that first extracts relationships from the provided modules and then generates all currently supported diagram types (architecture and dependency) in one call.
