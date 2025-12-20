# Dashboard Compiler Architecture

This document describes the architecture of the dashboard compiler, which converts a simplified YAML representation of Kibana dashboards into the complex Kibana dashboard JSON format.

## Goal

The primary goal is to provide a human-readable and maintainable way to define Kibana dashboards using YAML, abstracting away the complexities of the native JSON structure.

## Design

The compiler is designed using a layered approach with distinct components responsible for different stages of the conversion process.

1.  **YAML Loading and Parsing:**
    - The process begins by loading the YAML configuration file.
    - The `PyYAML` library is used to parse the YAML content into a Python dictionary.

2.  **Pydantic Model Representation:**
    - Pydantic models are used to represent the structure and data types of the YAML schema.
    - Each major component of a dashboard (Dashboard, Panel, Grid, etc.) and its variations (different panel types, Lens visualizations, dimensions, metrics, etc.) is mapped to a corresponding Pydantic class.
    - Pydantic handles data validation, ensuring the parsed YAML conforms to the defined schema.
    - A custom validator in the base `Panel` class is used to dynamically instantiate the correct panel subclass based on the `type` field in the YAML data.

3.  **JSON Compilation:**
    - Each Pydantic model includes a `to_json()` method responsible for converting the model's data into the corresponding part of the Kibana dashboard JSON structure.
    - The `to_json()` methods handle the specific formatting and nesting required for each element (panels, visualizations, layers, etc.).
    - The top-level `Dashboard` model's `to_json()` method orchestrates the compilation of its panels and assembles the final JSON string.

4.  **ID and Reference Management (Future Enhancement):**
    - The Kibana dashboard JSON relies heavily on unique IDs and references between components.
    - A future enhancement will involve implementing a system for generating unique IDs and managing these references during the compilation process to ensure the generated dashboards are valid and functional in Kibana.

5.  **Error Handling (Future Enhancement):**
    - Robust error handling will be added to catch and report issues during YAML parsing, data validation, and JSON compilation.

## Components

- **`models.py`:** Contains the Pydantic model definitions for the YAML schema and the `to_json()` methods for converting models to JSON fragments.
- **`compiler.py`:** Contains the main compilation logic, including loading and parsing YAML, validating with Pydantic models, and triggering the JSON generation.
- **`test/`:** Directory for test files to verify the compiler's output against expected JSON.

## Data Flow

1.  YAML file is read.
2.  YAML content is parsed into a Python dictionary.
3.  The dictionary is validated and converted into a hierarchy of Pydantic objects.
4.  The `to_json()` method is called on the root `Dashboard` object.
5.  `to_json()` methods recursively called on nested objects to build the JSON structure.
6.  A JSON string is generated.

```mermaid
graph TD
    A[YAML File] --> B{Load & Parse YAML}
    B --> C[Python Dictionary]
    C --> D{Pydantic Validation & Model Creation}
    D --> E[Pydantic Object Hierarchy]
    E --> F{Call to_json()}
    F --> G[JSON String]