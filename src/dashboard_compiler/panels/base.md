# Base Panel Configuration

All panel types used within a dashboard (e.g., Markdown, Lens charts, Search panels) share a common set of base configuration fields. These fields define fundamental properties like the panel's title, its position and size on the dashboard grid, and an optional description.

When defining a panel in your YAML, you will specify its `type` (e.g., `markdown`, `lens_metric`) and then include these base fields alongside type-specific configurations.

## Minimal Example (Illustrating Base Fields within a Specific Panel Type)

This example shows how base panel fields are used within a `markdown` panel:

```yaml
# Within a dashboard's 'panels' list:
# - type: markdown  # Specific panel type
#   title: "Status Overview"
#   grid:
#     x: 0
#     y: 0
#     w: 6
#     h: 4
#   # ... other markdown-specific fields ...

# For a complete dashboard structure:
dashboard:
  name: "Example Dashboard"
  panels:
    - type: markdown # This 'type' field is part of the MarkdownPanel model, not BasePanel
      title: "Status Overview"
      description: "A quick look at system status." # BasePanel field
      hide_title: false                             # BasePanel field
      grid:                                         # BasePanel field
        x: 0
        y: 0
        w: 6
        h: 4
      # --- MarkdownPanel specific fields would go here ---
      content: "System is **operational**."
```

## Full Configuration Options

### Base Panel Fields

These fields are available for all panel types and are inherited from the `BasePanel` configuration.

| YAML Key     | Data Type | Description                                                                                                | Kibana Default                  | Required |
| ------------ | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `id`         | `string`  | A unique identifier for the panel. If not provided, one will be generated during compilation.              | Generated ID                    | No       |
| `title`      | `string`  | The title displayed on the panel header. Can be an empty string if you wish for no visible title.          | `""` (empty string)             | No       |
| `hide_title` | `boolean` | If `true`, the panel title (even if defined) will be hidden.                                               | `false` (title is shown)        | No       |
| `description`| `string`  | A brief description of the panel's content or purpose. This is often shown on hover or in panel information. | `""` (empty string, if `None`)  | No       |
| `grid`       | `Grid` object | Defines the panel's position and size on the dashboard grid. See [Grid Object Configuration](#grid-object-configuration). | N/A                             | Yes      |

**Note on `type`**: The `type` field (e.g., `type: markdown`, `type: lens_metric`) is **required** for every panel definition in your YAML. However, it is not part of the `BasePanel` model itself but is a discriminator field defined in each specific panel type's configuration (e.g., `MarkdownPanel`, `LensPanel`). It tells the compiler which specific panel configuration to use.

### Grid Object Configuration (`grid`)

The `grid` object is required for every panel and defines its placement and dimensions on the dashboard. The dashboard is typically a 12-column grid, but `w` and `h` are unitless and relative to this grid system.

| YAML Key | Data Type | Description                                                              | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------------------------------ | -------------- | -------- |
| `x`      | `integer` | The horizontal starting position of the panel on the grid (0-based index). | N/A            | Yes      |
| `y`      | `integer` | The vertical starting position of the panel on the grid (0-based index).   | N/A            | Yes      |
| `w`      | `integer` | The width of the panel in grid units.                                    | N/A            | Yes      |
| `h`      | `integer` | The height of the panel in grid units.                                   | N/A            | Yes      |

**Example of `grid` usage:**
```yaml
# ...
# panels:
#   - type: markdown
#     title: "Top Left Panel"
#     grid:
#       x: 0  # Starts at the far left
#       y: 0  # Starts at the very top
#       w: 6  # Occupies 6 out of 12 columns (half width)
#       h: 5  # Height of 5 grid units
#     content: "..."
#   - type: lens_metric
#     title: "Top Right Panel"
#     grid:
#       x: 6  # Starts at the 7th column (0-indexed)
#       y: 0  # Starts at the very top
#       w: 6  # Occupies the remaining 6 columns
#       h: 5  # Same height
#     # ... lens configuration ...
```

## Panel Types (Specific Configurations)

The `BasePanel` fields are common to all panel types. For details on the specific configuration fields available for each panel `type`, refer to their individual documentation pages:

*   [Markdown Panel](./markdown/markdown.md)
*   [Links Panel](./links/links.md)
*   [Search Panel](./search/search.md) (*Documentation to be created/updated*)
*   **Charts:**
    *   [Lens Panel (for various chart types like bar, line, area, pie, metric, table)](./charts/lens/lens.md)
    *   [ESQL Panel (for ESQL-driven visualizations)](./charts/esql/esql.md) (*Documentation to be created/updated*)
    *   (*Other chart types like Vega, Timelion, TSVB might be added here if supported*)

## Related Documentation

*   [Dashboard Configuration](../dashboard/dashboard.md)