# Dashboard Compiler Architecture

This document describes the architecture of the dashboard compiler, which converts a simplified YAML representation of Kibana dashboards into the complex Kibana dashboard JSON format.

## Goal

The primary goal is to provide a human-readable and maintainable way to define Kibana dashboards using YAML, abstracting away the complexities of the native JSON structure.

## Design

The compiler is designed using a layered approach with distinct components responsible for different stages of the conversion process.

1. **YAML Loading and Parsing:**
    - The process begins by loading the YAML configuration file.
    - The `PyYAML` library is used to parse the YAML content into a Python dictionary.

2. **Pydantic Model Representation:**
    - The codebase uses a three-layer pattern with separate models for input configuration and output views:
      - **Config Models** (`**/config.py`): Define the YAML schema structure using Pydantic, handling validation and ensuring the parsed YAML conforms to the defined schema. These models use a `BaseCfgModel` base class.
      - **View Models** (`**/view.py`): Define the Kibana JSON output structure using Pydantic. These models use a `BaseVwModel` base class and include custom serialization logic.
      - **Compile Functions** (`**/compile.py`): Transform config models into view models, handling the specific formatting and mapping required for each component.
    - Each major component of a dashboard (Dashboard, Panel, Grid, etc.) and its variations (different panel types, Lens visualizations, dimensions, metrics, etc.) follows this pattern.
    - A custom validator in the base `Panel` class is used to dynamically instantiate the correct panel subclass based on the `type` field in the YAML data.

3. **Compilation Process:**
    - Compile functions in `compile.py` files take config model instances and transform them into view model instances.
    - These functions handle the specific formatting and nesting required for each element (panels, visualizations, layers, etc.).
    - The top-level dashboard compilation orchestrates the compilation of all components (panels, controls, filters, queries) and assembles the final Kibana JSON structure.
    - View models use Pydantic's `model_dump_json()` method to serialize to JSON.

4. **ID and Reference Management (Future Enhancement):**
    - The Kibana dashboard JSON relies heavily on unique IDs and references between components.
    - A future enhancement will involve implementing a system for generating unique IDs and managing these references during the compilation process to ensure the generated dashboards are valid and functional in Kibana.

5. **Error Handling (Future Enhancement):**
    - Robust error handling will be added to catch and report issues during YAML parsing, data validation, and JSON compilation.

## Components

The codebase is organized into packages:

**Core Package (`packages/kb-dashboard-core/src/kb_dashboard_core/`):**

- **`dashboard_compiler.py`:** Main entry point containing the core compilation orchestration functions (`load`, `render`, `dump`).
- **`dashboard/`:** Top-level dashboard compilation with `config.py`, `view.py`, and `compile.py`.
- **`panels/`:** Panel compilation with subdirectories for each panel type (markdown, links, images, search, charts).
- **`panels/charts/`:** Chart-specific compilation with subdirectories for different chart types (metric, pie, xy) and components (lens/esql metrics, dimensions, columns).
- **`controls/`:** Control group compilation for dashboard interactivity.
- **`filters/`:** Filter compilation supporting various filter types.
- **`queries/`:** Query compilation for KQL, Lucene, and ES|QL.

**CLI Package (`packages/kb-dashboard-cli/src/dashboard_compiler/`):**

- **`cli.py`:** Command-line interface for compiling dashboards and uploading to Kibana.
- **`lsp/`:** Language Server Protocol implementation for VS Code extension.
- **`sample_data/`:** Sample data loading utilities.
- **`tools/`:** CLI tooling utilities.

**CLI Package Tests (`packages/kb-dashboard-cli/tests/`):**

- Test files including snapshot tests to verify compiler output against expected JSON.

## Data Flow

1. YAML file is read.
2. YAML content is parsed into a Python dictionary.
3. The dictionary is validated and converted into a hierarchy of Pydantic config model objects.
4. Compile functions transform the config model hierarchy into view model objects.
5. The compile functions are called recursively on nested objects to build the view model structure.
6. View models are serialized to JSON using Pydantic's `model_dump_json()` method.
7. A Kibana-compatible NDJSON file is generated.

```mermaid
graph TD
    A[YAML File] --> B{Load & Parse YAML}
    B --> C[Python Dictionary]
    C --> D{Pydantic Validation}
    D --> E[Config Model Hierarchy]
    E --> F{Compile Functions}
    F --> G[View Model Hierarchy]
    G --> H{model_dump_json}
    H --> I[Kibana JSON/NDJSON]
