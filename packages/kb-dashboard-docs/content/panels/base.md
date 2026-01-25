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
dashboards:
- name: "Example Dashboard"
  panels:
    - markdown:
        content: "System is **operational**." # MarkdownPanel specific config
      title: "Status Overview"
      description: "A quick look at system status." # BasePanel field
      hide_title: false                             # BasePanel field
      size:                                         # BasePanel field (recommended)
        w: quarter  # or numeric value like 12
        h: 8
      position:                                     # BasePanel field (optional)
        x: 0
        y: 0
```

**Note:** See [Auto-Layout Guide](./auto-layout.md) for details on automatic panel positioning.

## Full Configuration Options

### Base Panel Fields

These fields are available for all panel types and are inherited from the `BasePanel` configuration.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------ | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `id` | `string` | A unique identifier for the panel. If not provided, one may be generated during compilation. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Can be an empty string if you wish for no visible title. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title (even if defined) will be hidden. | `false` (title is shown) | No |
| `description` | `string` | A brief description of the panel's content or purpose. This is often shown on hover or in panel information. | `""` (empty string, if `None`) | No |
| `size` | `Size` object | Defines the panel's width and height. See [Size Object Configuration](#size-object-configuration-size) below. | `w: 12, h: 8` | No |
| `position` | `Position` object | **Optional:** Defines the panel's x/y coordinates. Omit for automatic positioning. See [Position Object Configuration](#position-object-configuration-position) below. | Auto-calculated | No |

**Note on Panel Types**: Each panel must have exactly one key identifying its type (e.g., `markdown`, `lens`, `search`, `links`, `image`, `esql`). This key contains the type-specific configuration.

**Note on Auto-Layout**: For automatic panel positioning without manual coordinate calculation, use the `size` field and omit the `position` field. See the [Auto-Layout Guide](./auto-layout.md) for details.

### Size Object Configuration (`size`)

The `size` object defines the panel's width and height on the dashboard grid. This is the **recommended** approach for new dashboards.

Both shorthand and verbose parameter names are supported for improved readability.

| YAML Key | Verbose Alternative | Data Type | Description | Default | Required |
| -------- | ------------------- | --------- | ------------------------------------------------------------ | ------- | -------- |
| `w` | `width` | `integer` or `SemanticWidth` | The width of the panel. Accepts semantic values (`whole`, `half`, `third`, `quarter`, `sixth`, `eighth`) or numeric values (1-48). | `12` (quarter) | No |
| `h` | `height` | `integer` | The height of the panel in grid units. | `8` | No |

**Semantic Width Values:**

| Value | Grid Units | Description |
| ----- | ---------- | ----------- |
| `whole` | 48 | Full dashboard width |
| `half` | 24 | Half width |
| `third` | 16 | One-third width |
| `quarter` | 12 | Quarter width |
| `sixth` | 8 | One-sixth width |
| `eighth` | 6 | One-eighth width |

**Example:**

```yaml
size:
  w: quarter  # Semantic value
  h: 8

# Or with numeric value:
size:
  width: 24   # Numeric value
  height: 12
```

### Position Object Configuration (`position`)

The `position` object defines the panel's x/y coordinates on the dashboard grid. This field is **optional** - when omitted, the panel will be automatically positioned using the dashboard's layout algorithm.

| YAML Key | Verbose Alternative | Data Type | Description | Default | Required |
| -------- | ------------------- | --------- | ------------------------------------------------------------ | ------- | -------- |
| `x` | `from_left` | `integer` or `None` | The horizontal starting position (0-based, 0-48). If `None`, position is auto-calculated. | `None` | No |
| `y` | `from_top` | `integer` or `None` | The vertical starting position (0-based). If `None`, position is auto-calculated. | `None` | No |

**Example with fixed position:**

```yaml
position:
  x: 0
  y: 0

# Or verbose:
position:
  from_left: 24
  from_top: 10
```

**Example with auto-positioning (omit position entirely):**

```yaml
# No position field - will be auto-positioned
size:
  w: quarter
  h: 8
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

::: dashboard_compiler.panels.charts.base.config.ColorMapping
    options:
      show_root_heading: false
      heading_level: 4

### ColorAssignment Object

Manual color assignments are an advanced feature. For an introduction and examples, see the [Custom Color Assignments](../advanced/color-assignments.md) guide.

::: dashboard_compiler.panels.charts.base.config.ColorAssignment
    options:
      show_root_heading: false
      heading_level: 4

### Color Mapping Examples

#### Example 1: Using a Different Palette

```yaml
dashboards:
  - name: "Sales Dashboard"
    panels:
      - title: "Revenue by Region"
        size: { w: 6, h: 6 }
        lens:
          type: pie
          data_view: "logs-*"
          dimensions:
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
        size: { w: 6, h: 6 }
        lens:
          type: pie
          data_view: "logs-*"
          dimensions:
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
