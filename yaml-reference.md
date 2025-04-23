# Kibana Dashboard YAML Summary Reference

This document provides a reference for the YAML schema used to define Kibana dashboards in a simplified, human-readable format. This YAML serves as an intermediate representation that can be compiled into the full Kibana dashboard JSON.

## Top-Level `dashboard` Object

The root of the YAML file is the `dashboard` object.

```yaml
dashboard:
  title: string         # (Required) The title of the dashboard.
  description: string   # (Optional) A description for the dashboard. Defaults to "".
  panels: list          # (Required) A list of panel objects defining the dashboard content. Can be empty for an empty dashboard.
```

## `panel` Object

Each item in the `panels` list is a `panel` object.

```yaml
- panel:
    title: string         # (Required) The title displayed on the panel. Can be empty.
    type: string          # (Required) The type of panel. Valid types: search, map, lens, markdown.
    grid: object          # (Required) Defines the panel's position and size on the dashboard grid.
      x: integer          # (Required) Horizontal starting position (0-based).
      y: integer          # (Required) Vertical starting position (0-based).
      w: integer          # (Required) Width of the panel in grid units.
      h: integer          # (Required) Height of the panel in grid units.
    # --- Panel Type Specific Fields Below ---
```

## Panel Types

### `search` Panel

Used to embed a saved Kibana search.

```yaml
- panel:
    title: string         # Title is often derived from the saved search itself.
    type: search
    grid: { x: 0, y: 0, w: 24, h: 15 }
    saved_search_id: string # (Required) The ID of the Kibana saved search object.
```

### `markdown` Panel

Used to display markdown content. Corresponds to the Kibana "Text" visualization.

```yaml
- panel:
    title: string         # Optional title for the markdown panel.
    type: markdown        # Maps to Kibana visualization type 'markdown'.
    grid: { x: 0, y: 0, w: 24, h: 15 }
    content: string       # (Required) The markdown content to display. Use YAML multi-line string syntax (e.g., |) for readability.
```

### `map` Panel

Used to display geographical data.

```yaml
- panel:
    title: string         # Title for the map panel.
    type: map
    grid: { x: 0, y: 0, w: 24, h: 15 }
    layers: list          # (Required) List of map layers. Typically includes a base layer and data layers.
      - type: string      # (Required) Type of the layer (e.g., vector_tile, geojson_vector).
        label: string     # (Optional) Label for the layer.
        # --- Layer Type Specific Fields Below ---
        # Example for geojson_vector:
        index_pattern: string # (Required for data layers) Index pattern to use.
        query: string     # (Optional) KQL query specific to this layer.
        geo_field: string # (Required for geo layers) Field containing geo data (e.g., source.geo.location).
        style: object     # (Optional) Styling options.
          type: string    # (e.g., circle, marker) Symbol type.
          size: integer   # (e.g., 6) Symbol size.
          color: string   # (e.g., "#54B399") Symbol color (hex).
        tooltip_fields: list # (Optional) List of fields (strings) to show in the tooltip.
```
*Note: The base map layer (`vector_tile`) details are often omitted in the summary YAML.*

### `lens` Panel

Used for various chart types created with Kibana Lens.

```yaml
- panel:
    title: string         # Title for the Lens panel.
    type: lens
    visualization: string # (Required) The type of Lens visualization (e.g., line, table, pie, bar_stacked, metric). Maps to Kibana's lnsXY, lnsDatatable, lnsPie, lnsMetric, etc.
    grid: { x: 0, y: 0, w: 24, h: 15 }
    index_pattern: string # (Required) Index pattern used by the Lens visualization.
    query: string         # (Optional) KQL query specific to this panel. Defaults to "".
    filters: list         # (Optional) Panel-specific filters applied *in addition* to any global dashboard filters.
      - field: string     # (Required) Field to filter on.
        type: string      # (Required) Filter type (e.g., phrase, phrases).
        value: any        # (Required) Value(s) for the filter (string for phrase, list of strings for phrases).
        negate: boolean   # (Optional) Whether to negate the filter. Defaults to false.
    # --- Visualization Type Specific Fields Below ---
```

#### Lens Visualization Types

##### `line` / `bar_stacked` / `area` (lnsXY)

These share a similar structure defining dimensions (X-axis, Break down by) and metrics (Y-axis).

```yaml
    # (Continued from lens panel)
    dimensions: list      # (Required) Defines the axes (usually x-axis or split/breakdown dimensions).
      - field: string     # (Required) Field name.
        type: string      # (Required) Aggregation type (e.g., date_histogram, terms).
        label: string     # (Optional) Display label for the dimension. Defaults to field name.
        interval: string  # (Optional, for date_histogram) Time interval (e.g., auto, 1h, 1d). Defaults to 'auto'.
        size: integer     # (Optional, for terms) Number of terms to show.
        order_by_metric: string # (Optional, for terms) Label of the metric to sort the terms by.
        order_direction: string # (Optional, for terms) Sort direction: 'asc' or 'desc'. Defaults to 'desc'.
    metrics: list         # (Required) Defines the values (usually y-axis).
      - type: string      # (Required) Aggregation type (e.g., count, max, average, unique_count, formula, last_value).
        label: string     # (Optional) Display label for the metric. Defaults to standard label (e.g., "Count").
        field: string     # (Optional, required for most types except count) Field name. Use '___records___' for count.
        # --- Formula specific ---
        formula: string   # (Optional, for type: formula) The formula string (e.g., "counter_rate(max(field.name))").
        # --- Last Value specific ---
        sort_field: string # (Optional, for last_value) Field to determine the "last" value (e.g., @timestamp).
        filter: string    # (Optional, for last_value) KQL filter applied before taking the last value.
```

##### `table` (lnsDatatable)

Defines columns which can be dimensions or metrics.

```yaml
    # (Continued from lens panel)
    columns: list         # (Required) Defines the table columns. Order matters.
      - field: string     # (Required for dimension/metric columns) Field name. Use '___records___' for count.
        type: string      # (Required) Aggregation type (e.g., terms, count, last_value, max, average).
        label: string     # (Optional) Display label for the column.
        # --- Terms specific ---
        size: integer     # (Optional, for terms) Number of terms to show.
        order_by_metric: string # (Optional, for terms) Label of the metric column to sort this term column by.
        order_direction: string # (Optional, for terms) Sort direction: 'asc' or 'desc'. Defaults to 'desc'.
        # --- Last Value specific ---
        sort_field: string # (Optional, for last_value) Field to determine the "last" value (e.g., @timestamp).
        filter: string    # (Optional, for last_value) KQL filter applied before taking the last value.
```

##### `pie` (lnsPie)

Defines "Slice by" (dimension) and "Size by" (metric).

```yaml
    # (Continued from lens panel)
    dimensions: list      # (Required) Defines the "Slice by" dimension. Usually one 'terms' aggregation.
      - field: string     # (Required) Field name.
        type: terms       # (Required) Must be 'terms'.
        label: string     # (Optional) Display label.
        size: integer     # (Optional) Number of slices.
        order_by_metric: string # (Optional) Label of the metric to sort slices by.
        order_direction: string # (Optional) 'asc' or 'desc'. Defaults to 'desc'.
    metrics: list         # (Required) Defines the "Size by" metric. Usually one metric.
      - type: string      # (Required) Aggregation type (e.g., count, sum).
        label: string     # (Optional) Display label.
        field: string     # (Optional, required for most types except count) Field name. Use '___records___' for count.
```

##### `metric` (lnsMetric)

Displays a single metric value, potentially with color thresholds.

```yaml
    # (Continued from lens panel)
    metrics: list         # (Required) Defines the metric to display. Usually one.
      - type: string      # (Required) Aggregation type (e.g., count, unique_count, last_value).
        label: string     # (Optional) Display label.
        field: string     # (Optional, required for most types except count) Field name. Use '___records___' for count.
    # Optional color palette for thresholding
    palette: object       # (Optional) Defines color stops based on value.
      type: custom        # (Required if palette is present) Currently only 'custom' is supported.
      stops: list         # (Required if palette is present) List of color stops.
        - color: string   # (Required) Hex color code (e.g., "#cc5642").
          stop: number    # (Required) Threshold value for this color. Use `null` for the base/default color (lowest threshold). Order matters.
```

## Common Data Structures

*   **`grid`**: Defines panel layout (`x`, `y`, `w`, `h`). All integer values.
*   **`style` (for map layers)**: Defines visual properties like `type` (string), `size` (integer), `color` (string hex code).
*   **`palette` (for metric viz)**: Defines color thresholds using `type: custom` and a list of `stops` with `color` (string hex code) and `stop` (number or null).
*   **`dimension` / `metric` / `column`**: These objects define the data aggregations. They share common fields like `field` (string), `type` (string), `label` (string), and type-specific parameters like `interval` (string), `size` (integer), `order_by_metric` (string), `order_direction` (string), `formula` (string), `sort_field` (string), `filter` (string KQL).

```mermaid
graph TD
    Dashboard --> Title{Title}
    Dashboard --> Description{Description}
    Dashboard --> Panels[...]

    subgraph Panel Types
        SearchPanel[search]
        MarkdownPanel[markdown]
        MapPanel[map]
        LensPanel[lens]
    end

    Panels --> Panel
    Panel --> PTitle{title}
    Panel --> PType{type}
    Panel --> Grid{grid: {x, y, w, h}}
    Panel --> TypeSpecific{Type Specific Config}

    TypeSpecific -- type=search --> SearchPanel
    SearchPanel --> SavedSearchID{saved_search_id}

    TypeSpecific -- type=markdown --> MarkdownPanel
    MarkdownPanel --> Content{content}

    TypeSpecific -- type=map --> MapPanel
    MapPanel --> Layers[...]
    Layers --> LayerType{type}
    Layers --> LayerLabel{label}
    Layers --> LayerConfig{...config}
    LayerConfig --> IndexPatternMap{index_pattern}
    LayerConfig --> GeoField{geo_field}
    LayerConfig --> Style{style: {type, size, color}}
    LayerConfig --> TooltipFields{tooltip_fields}

    TypeSpecific -- type=lens --> LensPanel
    LensPanel --> VizType{visualization}
    LensPanel --> IndexPatternLens{index_pattern}
    LensPanel --> QueryLens{query}
    LensPanel --> FiltersLens{filters: [{field, type, value, negate}]}
    LensPanel --> VizSpecific{Viz Specific Config}

    subgraph Lens Visualizations
        XY[line, bar_stacked, area]
        Table[table]
        Pie[pie]
        Metric[metric]
    end

    VizSpecific -- viz=line/bar_stacked/area --> XY
    XY --> Dimensions[...]
    XY --> Metrics[...]

    VizSpecific -- viz=table --> Table
    Table --> Columns[...]

    VizSpecific -- viz=pie --> Pie
    Pie --> PieDimensions[dimensions (Slice By)]
    Pie --> PieMetrics[metrics (Size By)]

    VizSpecific -- viz=metric --> Metric
    Metric --> MetricMetric[metrics]
    Metric --> MetricPalette[palette: {type: custom, stops: [...]}]

    subgraph Common Aggregation Objects
        Dimension --> DimField{field}
        Dimension --> DimType{type}
        Dimension --> DimLabel{label}
        Dimension --> DimParams{...params (interval, size, etc)}

        Metric --> MetType{type}
        Metric --> MetLabel{label}
        Metric --> MetField{field}
        Metric --> MetParams{...params (formula, etc)}

        Column --> ColField{field}
        Column --> ColType{type}
        Column --> ColLabel{label}
        Column --> ColParams{...params (size, order_by_metric, etc)}
    end

    XY --> Dimension
    XY --> Metric
    Table --> Column
    Pie --> Dimension
    Pie --> Metric
    Metric --> Metric
```