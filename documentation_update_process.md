# Process for Updating YAML Configuration Markdown Documentation

This document outlines the process used to generate and update the markdown documentation files that serve as a reference for the YAML configuration of the `dashboard_compiler` project. The goal is to ensure comprehensive, accurate, and consistently structured documentation based on the Pydantic models.

## I. Guiding Principles & Strategy

1. **Pydantic Models as Source of Truth**: The `config.py` files within each component directory, containing Pydantic models, are the definitive source for all configuration options, their types, defaults, and requirements.
2. **Standard Markdown File Structure**: Each component's primary markdown documentation file (e.g., `controls/config.md`, `panels/markdown/markdown.md`) should adhere to a consistent structure:
    * **Introduction/Overview**: A brief explanation of the component and its purpose.
    * **Minimal Configuration Example(s)**: The simplest valid YAML snippet(s) to use the component or its main features.
    * **Example(s) with Common/More Complex Options**: Illustrative YAML snippets showcasing typical usage with a broader set of options.
    * **"Full Configuration Options" Table(s)**: Detailed tables for each relevant Pydantic model, outlining all its fields.
    * **Links to Related Documentation**: Cross-references to other relevant markdown files (e.g., base configurations, sub-components).
3. **"Full Configuration Options" Table Format**: These tables should consistently use the following columns:
    * `YAML Key`: The exact key name to be used in the YAML configuration. This should reflect any Pydantic field aliases (`alias='...'`).
    * `Data Type`: The expected data type (e.g., `string`, `integer`, `boolean`, `list of objects`, specific Enum values).
    * `Description`: A clear explanation of the field's purpose, derived from Pydantic model docstrings or `Field(description=...)`.
    * `Default`: The default value if the field is optional. Indicated as `None`, an empty list `[]`, a specific value (e.g., `true`, `horizontal`), or `N/A` if the field is required or has no default.
    * `Required`: `Yes` or `No`. Determined by the Pydantic model (e.g., presence of `...` as a default, no default value, or explicit marking).
4. **YAML Examples**:
    * **Clarity and Correctness**: Examples should be valid, easy to understand, and demonstrate key functionalities.
    * **No Unnecessary Wrappers**: Avoid generic wrappers in YAML examples if the Pydantic models define list items as directly typed objects (e.g., a list of `PanelType` objects rather than a list of generic `panel:` wrappers each containing a typed object). The structure should mirror how the Pydantic models expect the data.
5. **Cross-Referencing**:
    * Link to base configurations (e.g., `BasePanel` documentation from specific panel type docs).
    * Link to sub-component documentation where complex fields are defined in separate models/files.

## II. Step-by-Step Process for Documenting/Updating a Component

This process is applied to each main component directory (e.g., `controls/`, `dashboard/`, `filters/`, `panels/`, `queries/`) and their relevant sub-components.

Use the Filesystem Operations MCP to read all config.py, compile.py, and markdown files in the dashboard_compiler directory.

1. **Identify Target Component & Directory**:
    * Determine the component to be documented (e.g., "Controls", "Markdown Panel").
    * Locate its primary directory (e.g., `dashboard_compiler/controls/`, `dashboard_compiler/panels/markdown/`).

2. **Locate Key Source Files**:
    * **`config.py`**: The Python file containing the Pydantic model definitions for the component. This is the primary source of truth.
    * **Existing `.md` file**: The current markdown documentation file for the component (if one exists). This will be reviewed and updated.

3. **Analyze Pydantic Models (from `config.py`)**:
    * For each Pydantic class relevant to the component:
        * List all fields.
        * Identify the data type of each field (including Literals, Unions, Enums, nested Pydantic models).
        * Note the default value (or if it's required – often indicated by `...` or no default).
        * Extract the description (from the field's docstring, `Field(description=...)`, or the class docstring).
        * Note any field aliases (e.g., `Field(..., alias='in')`). The YAML key in the documentation should use the alias.
    * Identify any helper Enums or type aliases used by the models.

4. **Review compile.py**:
    * Almost none of the pydantic models have default values, as they are the config language. The default values are defined in the `compile.py` file. And so when we descript the default value, we want to describe it as "Kibana Default".

5. **Review Existing Markdown File (if applicable)**:
    * Compare the information in the existing markdown against the details extracted from the Pydantic models.
    * Identify discrepancies, outdated information, missing fields, or incorrect examples.
    * Note areas needing restructuring to fit the standard format.

6. **Draft or Update the Markdown Content**:

    * **File Naming**: Typically `config.md` for general components or `[component_name].md` for specific sub-types (e.g., `markdown.md` for the Markdown panel).

    * **a. Introduction/Overview**:
        * Write a concise paragraph explaining what the component is and its primary role in the dashboard configuration.

    * **b. Minimal Configuration Example(s)**:
        * Provide the simplest possible valid YAML snippet that demonstrates the core usage of the component or its key features.
        * Include comments if necessary to explain choices.

    * **c. Example(s) with Common/More Complex Options**:
        * Create one or more YAML snippets showcasing a more typical or advanced configuration, using a wider range of optional fields.

    * **d. "Full Configuration Options" Table(s)**:
        * For each Pydantic model identified in Step 3, create a dedicated table.
        * Use the standard columns: `YAML Key`, `Data Type`, `Description`, `Kibana Default`, `Required`.
        * Populate the table using the information gathered from the Pydantic models.
        * **Inherited Fields**: If a model inherits from a base model (e.g., `BasePanel`), we do not indicate this in the table. For completeness and ease of use, we list the inherited fields directly in the table of the derived model.
        * **Nested Objects**: If a field's data type is another Pydantic model (e.g., a `grid` field being a `Grid` object), the table should state the type and link to the section/document where that nested object is detailed.

    * **e. Sub-Sections for Complex Types (if applicable)**:
        * If a component involves multiple distinct sub-types (e.g., `LensPanel` can have a `chart` that is a `LensMetricChart` or `LensPieChart`), dedicate clear sub-sections to each.
        * Within these sub-sections, repeat the process of providing examples and "Full Configuration Options" tables for those specific sub-types.
        * For very complex, deeply nested structures (like Lens chart metrics and dimensions), create further nested sub-sections to maintain clarity. This may involve documenting models imported from other `config.py` files (e.g., from `metrics/config.py` or `dimensions/config.py`).

    * **f. Related Documentation**:
        * Add a "Related Documentation" section at the end.
        * Include markdown links to parent configurations (e.g., `BasePanel.md`), child/nested configurations, or other relevant components.

7. **Iterative Refinement for Complex Components (e.g., Charts)**:
    * For highly nested configurations like those found in `panels/charts/`, the process involves:
        1. Documenting the top-level panel (e.g., `LensPanel` in `lens.md`).
        2. Identifying the types for its complex fields (e.g., `LensChartTypes` for the `chart` field).
        3. Reading the `config.py` files that define these complex types (e.g., `visualizations/config.py`, then `metric/config.py` and `pie/config.py`).
        4. Recursively documenting these nested types as sub-sections within the main panel's markdown file. This includes detailing their own fields, which might again be complex types (e.g., `LensMetricTypes`, `LensDimensionTypes`).
        5. This requires careful navigation through the Pydantic model imports to trace all dependencies.

8. **Final Review**:
    * Read through the generated/updated markdown file.
    * Verify accuracy against the Pydantic models.
    * Check for clarity, consistency in formatting, and completeness.
    * Test any markdown links to ensure they point to the correct locations.

By following this structured approach, the documentation should remain synchronized with the application's configuration capabilities and provide a clear, reliable reference for users.
