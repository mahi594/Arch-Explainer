# diagram

**Purpose:** To generate various types of architectural diagrams (e.g., module dependencies, class relationships, call graphs, sequence diagrams) from validated, structured input data, rather than relying on free-form LLM generation. This approach ties diagram accuracy directly to the underlying module documentation.

**Description:** Transforms structured module documentation into Mermaid diagrams, ensuring deterministic and accurate visual representations of codebase architecture.

## Key Files

- `src/arch_explainer/diagram/generator.py`

## Dependencies

- re
- pathlib
- arch_explainer.models
- arch_explainer.ingest.graph_extractor

## Public API

### `extract_relationships`

- **Type:** `function`
- **Signature:** `def extract_relationships(modules: list[ModuleDoc]) -> list[ModuleRelationship]`
- **File:** `src/arch_explainer/diagram/generator.py`

Turns each module's `dependencies` list into typed edges, classifying them as 'imports' (internal) or 'uses' (external).

### `generate_architecture_diagram`

- **Type:** `function`
- **Signature:** `def generate_architecture_diagram(modules: list[ModuleDoc], relationships: list[ModuleRelationship]) -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid diagram showing the full architecture, including internal modules and their external library dependencies. Standard library dependencies are collapsed into a single 'Python stdlib' node.

### `generate_dependency_diagram`

- **Type:** `function`
- **Signature:** `def generate_dependency_diagram(modules: list[ModuleDoc], relationships: list[ModuleRelationship]) -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid diagram focused solely on how modules within the repository depend on each other, excluding external dependencies.

### `generate_diagrams`

- **Type:** `function`
- **Signature:** `def generate_diagrams(modules: list[ModuleDoc]) -> list[Diagram]`
- **File:** `src/arch_explainer/diagram/generator.py`

A convenience entrypoint for the pipeline, extracting relationships and building all primary diagram types (architecture and dependency) in a single call.

### `generate_class_diagram`

- **Type:** `function`
- **Signature:** `def generate_class_diagram(classes: list["ClassRelationship"], title: str = "Class Relationships", diagram_id: str = "classes") -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid classDiagram illustrating inheritance (`<|--`) and composition (`*--`) relationships between classes. Only classes involved in at least one relationship are drawn.

### `generate_call_graph`

- **Type:** `function`
- **Signature:** `def generate_call_graph(calls: list["CallEdge"], title: str = "Function Call Graph", diagram_id: str = "calls", cross_module_only: bool = False) -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid graph TD representing resolved function call edges within the repository. Can be configured to show only cross-module calls for a higher-level view.

### `generate_sequence_diagram`

- **Type:** `function`
- **Signature:** `def generate_sequence_diagram(calls: list["CallEdge"], entry_point: str, max_depth: int = 4) -> Diagram`
- **File:** `src/arch_explainer/diagram/generator.py`

Generates a Mermaid sequenceDiagram, tracing a breadth-first call flow starting from a specified `entry_point` up to a `max_depth`.

### `generate_class_and_call_diagrams`

- **Type:** `function`
- **Signature:** `def generate_class_and_call_diagrams(classes: list["ClassRelationship"], calls: list["CallEdge"], sequence_entry_points: list[str] | None = None) -> list[Diagram]`
- **File:** `src/arch_explainer/diagram/generator.py`

Builds a comprehensive set of diagrams, including whole-repo class and call graphs, per-module class and call graphs, and sequence diagrams for specified entry points.
