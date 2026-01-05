# Base Panel Configuration

All panel types used within a dashboard (e.g., Markdown, Lens charts, Search panels) share a common set of base configuration fields. These fields define fundamental properties like the panel's title, its position and size on the dashboard grid, and an optional description.

When defining a panel in your YAML, you must specify the configuration block for that specific panel type (e.g., `markdown`, `lens`) which serves as the key to identify the panel type.

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
# - markdown:  # Specific panel type key
#     content: "System is **operational**."
#   title: "Status Overview"
#   grid:
#     x: 0
#     y: 0
#     w: 6
#     h: 4
#   # ... other fields ...

# For a complete dashboard structure:
dashboards:
- name: "Example Dashboard"
  panels:
    - markdown:
        content: "System is **operational**." # MarkdownPanel specific config
      title: "Status Overview"
      description: "A quick look at system status." # BasePanel field
      hide_title: false                             # BasePanel field
      grid:                                         # BasePanel field
        x: 0
        y: 0
        w: 6
        h: 4
```

## Full Configuration Options

### Base Panel Fields

These fields are available for all panel types and are inherited from the `BasePanel` configuration.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------ | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `id` | `string` | A unique identifier for the panel. If not provided, one may be generated during compilation. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Can be an empty string if you wish for no visible title. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title (even if defined) will be hidden. | `false` (title is shown) | No |
| `description` | `string` | A brief description of the panel's content or purpose. This is often shown on hover or in panel information. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size on the dashboard grid. See [Grid Object Configuration](#grid-object-configuration-grid) below. | N/A | Yes |

**Note on Panel Types**: Each panel must have exactly one key identifying its type (e.g., `markdown`, `lens`, `search`, `links`, `image`, `esql`). This key contains the type-specific configuration.

### Grid Object Configuration (`grid`)

The `grid` object is required for every panel and defines its placement and dimensions on the dashboard. The dashboard uses a 48-column grid, and `w` and `h` are unitless and relative to this grid system.

Both shorthand and verbose parameter names are supported for improved readability. You can mix and match both forms in the same configuration.

| YAML Key | Verbose Alternative | Data Type | Description | Kibana Default | Required |
| -------- | ------------------- | --------- | ------------------------------------------------------------------------ | -------------- | -------- |
| `x` | `from_left` | `integer` | The horizontal starting position of the panel on the grid (0-based index). | N/A | Yes |
| `y` | `from_top` | `integer` | The vertical starting position of the panel on the grid (0-based index). | N/A | Yes |
| `w` | `width` | `integer` | The width of the panel in grid units. | N/A | Yes |
| `h` | `height` | `integer` | The height of the panel in grid units. | N/A | Yes |

**Example of `grid` usage:**

```yaml
# Shorthand syntax (concise)
panels:
  - markdown:
      content: "..."
    title: "Top Left Panel"
    grid:
      x: 0  # Starts at the far left
      y: 0  # Starts at the very top
      w: 24 # Occupies 24 out of 48 columns (half width)
      h: 5  # Height of 5 grid units

  # Verbose syntax (explicit)
  - lens:
      type: metric
      # ... lens configuration ...
    title: "Top Right Panel"
    grid:
      from_left: 24  # Starts at the 25th column (0-indexed)
      from_top: 0    # Starts at the very top
      width: 24      # Occupies the remaining 24 columns
      height: 5      # Same height

  # Mixed syntax (both forms work together)
  - markdown:
      content: "..."
    title: "Bottom Panel"
    grid:
      x: 0        # Shorthand for horizontal position
      from_top: 5 # Verbose for vertical position
      width: 48   # Verbose for full width
      h: 10       # Shorthand for height
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

> **Quick Reference**: Want to customize chart colors? See [Color Mapping Examples](#color-mapping-examples) below for palette selection, or the [Custom Color Assignments](../advanced/color-assignments.md) guide for manual color assignments.

Many chart panel types (Pie, XY, Metric) support color customization through the `color` field. You can select from built-in color palettes or manually assign specific colors to data values.

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

#### ColorAssignment Object (Advanced)

Manual color assignments are an advanced feature. For an introduction and examples, see the [Custom Color Assignments](../advanced/color-assignments.md) guide.

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
          metrics:
            - aggregation: sum
              field: revenue
          color:
            palette: 'elastic_brand'  # Use Elastic brand colors
```

#### Example 2: Manual Color Assignments (Advanced)

For a detailed introduction to color assignments, see the [Custom Color Assignments](../advanced/color-assignments.md) guide.

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
          metrics:
            - aggregation: count
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
