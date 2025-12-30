# Base Panel Configuration

All panel types used within a dashboard (e.g., Markdown, Lens charts, Search panels) share a common set of base configuration fields. These fields define fundamental properties like the panel's title, its position and size on the dashboard grid, and an optional description.

When defining a panel in your YAML, you will specify its `type` (e.g., `markdown`, `lens_metric`) and then include these base fields alongside type-specific configurations.

## A Poem for the Dashboard Builders

_For those who lay the foundation for every panel:_

```text
Every panel needs a base:
A title, grid, and proper place.
From x and y, the starting spot,
To width and height—you plot the plot.

The id is yours, or auto-made,
Descriptions help when things must be weighed.
hide_title when you'd rather not—
The base provides what others forgot.

Whether metric, pie, or chart XY,
Markdown prose or links nearby,
They all inherit from this floor:
The BasePanel, forevermore.

So here's to grids that organize,
To coordinates that plot the prize.
The humble base, unsexy but true—
No panel works without you.
```

---

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
dashboards:
-
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

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------ | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `id` | `string` | A unique identifier for the panel. If not provided, one will be generated during compilation. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Can be an empty string if you wish for no visible title. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title (even if defined) will be hidden. | `false` (title is shown) | No |
| `description` | `string` | A brief description of the panel's content or purpose. This is often shown on hover or in panel information. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size on the dashboard grid. See [Grid Object Configuration](#grid-object-configuration-grid). | N/A | Yes |

**Note on `type`**: The `type` field (e.g., `type: markdown`, `type: lens_metric`) is **required** for every panel definition in your YAML. However, it is not part of the `BasePanel` model itself but is a discriminator field defined in each specific panel type's configuration (e.g., `MarkdownPanel`, `LensPanel`). It tells the compiler which specific panel configuration to use.

### Grid Object Configuration (`grid`)

The `grid` object is required for every panel and defines its placement and dimensions on the dashboard. The dashboard uses a 48-column grid, and `w` and `h` are unitless and relative to this grid system.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------------------------------ | -------------- | -------- |
| `x` | `integer` | The horizontal starting position of the panel on the grid (0-based index). | N/A | Yes |
| `y` | `integer` | The vertical starting position of the panel on the grid (0-based index). | N/A | Yes |
| `w` | `integer` | The width of the panel in grid units. | N/A | Yes |
| `h` | `integer` | The height of the panel in grid units. | N/A | Yes |

**Example of `grid` usage:**

```yaml
# ...
# panels:
#   - type: markdown
#     title: "Top Left Panel"
#     grid:
#       x: 0  # Starts at the far left
#       y: 0  # Starts at the very top
#       w: 24 # Occupies 24 out of 48 columns (half width)
#       h: 5  # Height of 5 grid units
#     content: "..."
#   - type: lens_metric
#     title: "Top Right Panel"
#     grid:
#       x: 24 # Starts at the 25th column (0-indexed)
#       y: 0  # Starts at the very top
#       w: 24 # Occupies the remaining 24 columns
#       h: 5  # Same height
#     # ... lens configuration ...
```

## Panel Types (Specific Configurations)

The `BasePanel` fields are common to all panel types. For details on the specific configuration fields available for each panel `type`, refer to their individual documentation pages:

* [Markdown Panel](./markdown.md)
* [Links Panel](./links.md)
* [Search Panel](./search.md)
* [Image Panel](./image.md)
* [XY Chart Panel](./xy.md)
* [Pie Chart Panel](./pie.md)
* [Metric Panel](./metric.md)
* [Tagcloud Panel](./tagcloud.md)
* [Lens Panel](./lens.md)
* [ESQL Panel](./esql.md)

## Color Mapping Configuration

Many chart panel types (Pie, XY, Metric) support color customization through the `color` field. This allows you to control how colors are assigned to different data values or categories in your visualizations.

### ColorMapping Object

| YAML Key | Data Type | Description | Default | Required |
| -------- | --------- | ----------- | ------- | -------- |
| `palette` | `string` | The color palette ID to use for unassigned colors. | `'eui_amsterdam_color_blind'` | No |
| `assignments` | `list[ColorAssignment]` | Manual color assignments to specific data values. | `[]` | No |

#### Available Color Palettes

The `palette` field accepts the following palette IDs:

* `'eui_amsterdam_color_blind'` - Color-blind safe palette (default, recommended)
* `'default'` - Standard EUI palette
* `'kibana_palette'` or `'legacy'` - Legacy Kibana colors
* `'elastic_brand'` - Elastic brand colors
* `'gray'` - Grayscale palette

#### ColorAssignment Object

| YAML Key | Data Type | Description | Required |
| -------- | --------- | ----------- | -------- |
| `value` | `string` | Single data value to assign this color to. | No* |
| `values` | `list[str]` | List of data values to assign this color to. | No* |
| `color` | `string` | Hex color code (e.g., '#FF0000'). | Yes |

\* At least one of `value` or `values` must be provided.

### Color Mapping Examples

#### Example 1: Using a Different Palette

```yaml
dashboards:
  - name: "Sales Dashboard"
    panels:
      - title: "Revenue by Region"
        grid: { x: 0, y: 0, w: 6, h: 6 }
        lens:
          type: pie
          data_view: "logs-*"
          slice_by:
            - field: "region"
              type: values
          metric:
            aggregation: sum
            field: revenue
          color:
            palette: 'elastic_brand'  # Use Elastic brand colors
```

#### Example 2: Manual Color Assignments

```yaml
dashboards:
  - name: "Status Monitoring"
    panels:
      - title: "Request Status Distribution"
        grid: { x: 0, y: 0, w: 6, h: 6 }
        lens:
          type: pie
          data_view: "logs-*"
          slice_by:
            - field: "http.response.status_code"
              type: values
          metric:
            aggregation: count
          color:
            palette: 'eui_amsterdam_color_blind'
            assignments:
              - values: ['200', '201', '204']
                color: '#00BF6F'  # Green for success
              - values: ['404']
                color: '#FFA500'  # Orange for not found
              - values: ['500', '502', '503']
                color: '#BD271E'  # Red for errors
```

## Related Documentation

* [Dashboard Configuration](../dashboard/dashboard.md)
