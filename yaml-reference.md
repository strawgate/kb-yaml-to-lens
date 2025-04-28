# Kibana Dashboard YAML Summary Reference

This document provides a reference for the YAML schema used to define Kibana dashboards in a simplified, human-readable format. This YAML serves as an intermediate representation that can be compiled into the full Kibana dashboard JSON.

## Top-Level `dashboard` Object

The root of the YAML file is the `dashboard` object.

```yaml
dashboard:
  id: string            # (Optional) Unique identifier for the dashboard.
  title: string         # (Required) The title of the dashboard.
  description: string   # (Optional) A description for the dashboard. Defaults to "".
  query: object         # (Optional) A query string to filter the dashboard data. Defaults to an empty KQL query.
    kql: string         # (Required if query type is kql) KQL query string.
    lucene: string      # (Required if query type is lucene) Lucene query string.
  filters: list         # (Optional) A list of filters to apply to the dashboard. Can be empty.
    - field: string     # (Required) Field to filter on.
      # Choose one of the following filter types:
      equals: any       # (Required for phrase filter) Value for a phrase filter.
      in: list          # (Required for phrases filter) List of values for a phrases filter.
      exists: boolean   # (Required for exists filter) Indicates if the field must exist.
      gte: any          # (Optional for range filter) Greater than or equal to value.
      gt: any           # (Optional for range filter) Greater than value.
      lte: any          # (Optional for range filter) Less than or equal to value.
      lt: any           # (Optional for range filter) Less than value.
    - not: object       # (Optional) Negates the following filter.
        # Nested filter object (phrase, phrases, or range)
  controls: list        # (Optional) A list of control panels for the dashboard. Can be empty.
    - type: string      # (Required) Type of the control. Valid types: optionsList, rangeSlider.
      id: string        # (Optional) Unique identifier for the control.
      label: string     # (Optional) Display label for the control.
      width: string     # (Optional) Width of the control (small, medium, large). Defaults to "medium".
      data_view: string # (Required) Index pattern for the control.
      field: string     # (Required) Field name for the control.
      # optionsList specific:
      search_technique: string # (Optional) Search technique (e.g., 'prefix').
      sort: object      # (Optional) Sort configuration for optionsList.
        by: string      # (Required) Field to sort by.
        direction: string # (Required) Sort direction ('asc' or 'desc').
      # rangeSlider specific:
      step: number      # (Optional) Step value for the slider.
  panels: list          # (Required) A list of panel objects defining the dashboard content. Can be empty for an empty dashboard.
```

## `panel` Object

Each item in the `panels` list is a `panel` object.

```yaml
- panel:
    id: string            # (Optional) Unique identifier for the panel.
    title: string         # (Required) The title displayed on the panel. Can be empty.
    description: string   # (Optional) A description for the panel. Defaults to "".
    type: string          # (Required) The type of panel. Valid types: search, map, lens, markdown, links.
    grid: object          # (Required) Defines the panel's position and size on the dashboard grid.
      x: integer          # (Required) Horizontal starting position (0-based).
      y: integer          # (Required) Vertical starting position (0-based).
      w: integer          # (Required) Width of the panel in grid units.
      h: integer          # (Required) Height of the panel in grid units.
    hide_title: boolean   # (Optional) Whether to hide the panel title. Defaults to false.
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

### `links` Panel

Used to display a list of links.

```yaml
- panel:
    title: string         # Title for the links panel.
    type: links
    grid: { x: 0, y: 0, w: 48, h: 2 }
    layout: string        # (Optional) Layout of the links (horizontal, vertical). Defaults to "horizontal".
    links: list           # (Required) List of link objects.
      - label: string     # (Optional) Display text for the link.
        # Choose one of the following link types:
        dashboard: string # (Optional) ID of dashboard or other object for dashboardLink.
        url: string       # (Optional) URL for urlLink.
```

### `lens` Panel

Used for various chart types created with Kibana Lens.

```yaml
- panel:
    id: string            # (Optional) Unique identifier for the panel.
    title: string         # Title for the Lens panel.
    type: lens
    chart: object         # (Required) Nested chart definition.
      id: string          # (Optional) Unique identifier for the chart.
      type: string        # (Required) Visualization type. Valid values: bar, area, line, table, pie, metric.
      # --- Visualization Type Specific Fields Below ---
      # Common for bar, area, line:
      mode: string        # (Optional, for bar, area) Stacking mode (stacked, unstacked, percentage). Defaults to "unstacked".
      dimensions: list    # (Required) Defines the dimensions (e.g., X-axis, Break down by). Min length 1 for bar, area, line. Max length 1 for pie.
        - id: string      # (Optional) Unique identifier for the dimension.
          field: string   # (Required) Field name.
          type: string    # (Required) Aggregation type (e.g., date_histogram, terms, histogram).
          label: string   # (Optional) Display label for the dimension. Defaults to field name.
          interval: string # (Optional, for date_histogram or histogram) Time or number interval.
          size: integer   # (Optional, for terms) Number of terms to show.
          sort: object    # (Optional, for terms) Sort configuration.
            by: string    # (Required) Field to sort by.
            direction: string # (Required) Sort direction ('asc' or 'desc').
          other_bucket: boolean # (Optional, for terms) Show 'Other' bucket.
          missing_bucket: boolean # (Optional, for terms) Show 'Missing' bucket.
          include: list   # (Optional, for terms) Include terms matching these values/regex.
          exclude: list   # (Optional, for terms) Exclude terms matching these values/regex.
          include_is_regex: boolean # (Optional, for terms) Treat include values as regex.
          exclude_is_regex: boolean # (Optional, for terms) Treat exclude values as regex.
      metrics: list       # (Required) Defines the values (e.g., Y-axis). Min length 1 for bar, area, line. Max length 1 for pie, metric.
        - id: string      # (Optional) Unique identifier for the metric.
          type: string    # (Required) Aggregation type (e.g., count, max, average, unique_count, formula, last_value).
          label: string   # (Optional) Display label for the metric. Defaults to standard label (e.g., "Count").
          field: string   # (Optional, required for most types except count) Field name. Use '___records___' for count.
          # --- Formula specific ---
          formula: string # (Optional, for type: formula) The formula string (e.g., "counter_rate(max(field.name))").
          # --- Last Value specific ---
          sort_field: string # (Optional, for last_value) Field to determine the "last" value (e.g., @timestamp).
          filter: string  # (Optional, for last_value) KQL filter applied before taking the last value.
      # table specific:
      columns: list       # (Required for table) Defines the table columns. Order matters.
        - id: string      # (Optional) Unique identifier for the column.
          field: string   # (Required for dimension/metric columns) Field name. Use '___records___' for count.
          type: string    # (Required) Aggregation type (e.g., terms, count, last_value, max, average).
          label: string   # (Optional) Display label for the column.
          # --- Terms specific ---
          size: integer   # (Optional, for terms) Number of terms to show.
          sort: object    # (Optional, for terms) Sort configuration.
            by: string    # (Required) Field to sort by.
            direction: string # (Required) Sort direction ('asc' or 'desc').
          # --- Last Value specific ---
          sort_field: string # (Optional, for last_value) Field to determine the "last" value (e.g., @timestamp).
          filter: string  # (Optional, for last_value) KQL filter applied before taking the last value.
      # metric specific:
      palette: object     # (Optional, for metric) Defines color stops based on value.
        type: custom      # (Required if palette is present) Currently only 'custom' is supported.
        stops: list       # (Required if palette is present) List of color stops.
          - color: string # (Required) Hex color code (e.g., "#cc5642").
            stop: number  # (Required) Threshold value for this color. Use `null` for the base/default color (lowest threshold). Order matters.
      # Common chart formatting:
      axis: object        # (Optional) Axis formatting options.
        bottom: object    # (Optional) Bottom axis formatting.
          title: string   # (Optional) Axis title. Set to null to hide.
          scale: string   # (Optional) Axis scale type (linear, log, square, sqrt).
          gridlines: boolean # (Optional) Show gridlines.
          tick_labels: boolean # (Optional) Show tick labels.
          orientation: string # (Optional) Axis label orientation (horizontal, vertical, rotated).
          min: any        # (Optional) Minimum value ("auto" or number).
          max: any        # (Optional) Maximum value ("auto" or number).
          show_current_time_marker: boolean # (Optional) Show current time marker.
        left: object      # (Optional) Left axis formatting.
          title: string   # (Optional) Axis title. Set to null to hide.
          scale: string   # (Optional) Axis scale type (linear, log, square, sqrt).
          gridlines: boolean # (Optional) Show gridlines.
          tick_labels: boolean # (Optional) Show tick labels.
          orientation: string # (Optional) Axis label orientation (horizontal, vertical, rotated).
          min: any        # (Optional) Minimum value ("auto" or number).
          max: any        # (Optional) Maximum value ("auto" or number).
        right: object     # (Optional) Right axis formatting.
          title: string   # (Optional) Axis title. Set to null to hide.
          scale: string   # (Optional) Axis scale type (linear, log, square, sqrt).
          gridlines: boolean # (Optional) Show gridlines.
          tick_labels: boolean # (Optional) Show tick labels.
          orientation: string # (Optional) Axis label orientation (horizontal, vertical, rotated).
          min: any        # (Optional) Minimum value ("auto" or number).
          max: any        # (Optional) Maximum value ("auto" or number).
          metrics: list   # (Optional) List of metrics to display on the right axis.
      legend: object      # (Optional) Legend formatting options.
        is_visible: boolean # (Optional) Show legend. Defaults to true.
        position: string  # (Optional) Legend position (right, left, top, bottom). Defaults to "right".
      appearance: object  # (Optional) Chart appearance options.
        value_labels: string # (Optional) Show value labels (hide, show).
        fitting_function: string # (Optional) Fitting function (Linear).
        emphasize_fitting: boolean # (Optional) Emphasize the fitting function.
        curve_type: string # (Optional) Curve type (linear, cardinal, catmull-rom, natural, step, step-after, step-before, monotone-x).
        fill_opacity: number # (Optional) Fill opacity for area charts.
        min_bar_height: number # (Optional) Minimum bar height for bar charts.
        hide_endzones: boolean # (Optional) Hide endzones for date_histogram.
    index_pattern: string # (Required) Index pattern used by the Lens visualization.
    query: string         # (Optional) Panel-specific KQL query. Defaults to "".
    filters: list         # (Optional) Panel-specific filters applied *in addition* to any global dashboard filters.
      - field: string     # (Required) Field to filter on.
        type: string      # (Required) Filter type (e.g., phrase, phrases, range).
        value: any        # (Required) Value(s) for the filter (string for phrase, list of strings for phrases).
        operator: string  # (Required) Filter operator (equals, contains, startsWith, endsWith).
        negate: boolean   # (Optional) Whether to negate the filter. Defaults to false.
```

## Common Data Structures

*   **`grid`**: Defines panel layout (`x`, `y`, `w`, `h`). All integer values.
*   **`style` (for map layers)**: Defines visual properties like `type` (string), `size` (integer), `color` (string hex code).
*   **`palette` (for metric viz)**: Defines color thresholds using `type: custom` and a list of `stops` with `color` (string hex code) and `stop` (number or null).
*   **`dimension` / `metric` / `column`**: These objects define the data aggregations. They share common fields like `id` (optional string), `field` (string), `type` (string), `label` (string), and type-specific parameters like `interval` (string), `size` (integer), `sort` (object), `formula` (string), `sort_field` (string), `filter` (string KQL), `other_bucket` (boolean), `missing_bucket` (boolean), `include` (list), `exclude` (list), `include_is_regex` (boolean), `exclude_is_regex` (boolean).
*   **`sort`**: Defines sorting for terms aggregations (`by` string, `direction` string 'asc' or 'desc').
*   **Filters**:
    *   **Dashboard Filters**: Applied globally. Can be `exists` (field, exists boolean), `phrase` (field, equals any), `phrases` (field, in list), `range` (field, gte/gt/lte/lt any), or `negation` (not object containing another filter).
    *   **Panel Filters**: Applied only to a specific panel. Defined by `field` (string), `type` (string: phrase, phrases, range), `value` (any), `operator` (string: equals, contains, startsWith, endsWith), `negate` (optional boolean).
*   **Queries**:
    *   **Dashboard Query**: Applied globally. Can be `kql` (string) or `lucene` (string).
    *   **Panel Query**: Applied only to a specific panel. A simple KQL string.
*   **Controls**:
    *   **`optionsList`**: (id, type "optionsList", width, label, data_view, field, search_technique, sort object).
    *   **`rangeSlider`**: (id, type "rangeSlider", width, label, data_view, field, step number).
*   **`axis`**: Defines chart axis formatting. Can have `bottom`, `left`, and optional `right` nested objects. Includes fields for `title`, `scale`, `gridlines`, `tick_labels`, `orientation`, `min`, `max`. `bottom` also has `show_current_time_marker`. `right` also has a list of `metrics` to display on that axis.
*   **`legend`**: Defines chart legend formatting. Includes fields for `is_visible` (boolean) and `position` (string).
*   **`appearance`**: Defines chart appearance formatting. Includes fields for `value_labels` (string), `fitting_function` (string), `emphasize_fitting` (boolean), `curve_type` (string), `fill_opacity` (number), `min_bar_height` (number), `hide_endzones` (boolean).

```mermaid
graph TD
    Dashboard --> DTitle{title}
    Dashboard --> DDescription{description}
    Dashboard --> DPanels[panels]
    Dashboard --> DId{id}
    Dashboard --> DQuery{query}
    Dashboard --> DFilters{filters}
    Dashboard --> DControls{controls}

    DPanels --> Panel

    Panel --> PTitle{title}
    Panel --> PType{type}
    Panel --> PGrid{grid: {x, y, w, h}}
    Panel --> PId{id}
    Panel --> PDescription{description}
    Panel --> PHideTitle{hide_title}
    Panel --> TypeSpecific{Type Specific Config}

    TypeSpecific -- type=search --> SearchPanel[search]
    SearchPanel --> SavedSearchID{saved_search_id}

    TypeSpecific -- type=markdown --> MarkdownPanel[markdown]
    MarkdownPanel --> Content{content}

    TypeSpecific -- type=map --> MapPanel[map]
    MapPanel --> Layers[...]
    Layers --> LayerType{type}
    Layers --> LayerLabel{label}
    Layers --> LayerConfig{...config}
    LayerConfig --> IndexPatternMap{index_pattern}
    LayerConfig --> GeoField{geo_field}
    LayerConfig --> Style{style: {type, size, color}}
    LayerConfig --> TooltipFields{tooltip_fields}

    TypeSpecific -- type=links --> LinksPanel[links]
    LinksPanel --> Layout{layout}
    LinksPanel --> Links[links]
    Links --> Link{link}
    Link --> LinkLabel{label}
    Link --> DashboardLink{dashboard}
    Link --> UrlLink{url}


    TypeSpecific -- type=lens --> LensPanel[lens]
    LensPanel --> Chart{chart}
    LensPanel --> IndexPatternLens{index_pattern}
    LensPanel --> QueryLens{query}
    LensPanel --> FiltersLens{filters}
    LensPanel --> Axis{axis}
    LensPanel --> Legend{legend}
    LensPanel --> Appearance{appearance}

    Chart --> VizType{visualization}
    Chart --> VizSpecific{Viz Specific Config}
    Chart --> ChartId{id}

    VizSpecific -- type=bar/area/line --> XY[line, bar, area]
    XY --> DimensionsXY[dimensions]
    XY --> MetricsXY[metrics]
    XY --> Mode{mode}

    VizSpecific -- type=table --> Table[table]
    Table --> Columns[columns]

    VizSpecific -- type=pie --> Pie[pie]
    Pie --> DimensionsPie[dimensions (Slice By)]
    Pie --> MetricsPie[metrics (Size By)]

    VizSpecific -- type=metric --> Metric[metric]
    Metric --> MetricsMetric[metrics]
    Metric --> Palette{palette}

    DimensionsXY --> Dimension
    MetricsXY --> MetricObj[metric]
    Columns --> Column
    DimensionsPie --> Dimension
    MetricsPie --> MetricObj
    MetricsMetric --> MetricObj

    subgraph Common Aggregation Objects
        Dimension --> DimId{id}
        Dimension --> DimField{field}
        Dimension --> DimType{type}
        Dimension --> DimLabel{label}
        Dimension --> DimInterval{interval}
        Dimension --> DimSize{size}
        Dimension --> DimSort[sort]
        Dimension --> DimOtherBucket{other_bucket}
        Dimension --> DimMissingBucket{missing_bucket}
        Dimension --> DimInclude{include}
        Dimension --> DimExclude{exclude}
        Dimension --> DimIncludeRegex{include_is_regex}
        Dimension --> DimExcludeRegex{exclude_is_regex}

        MetricObj --> MetId{id}
        MetricObj --> MetType{type}
        MetricObj --> MetLabel{label}
        MetricObj --> MetField{field}
        MetricObj --> MetFormula{formula}
        MetricObj --> MetSortField{sort_field}
        MetricObj --> MetFilter{filter}

        Column --> ColId{id}
        Column --> ColField{field}
        Column --> ColType{type}
        Column --> ColLabel{label}
        Column --> ColSize{size}
        Column --> ColSort[sort]
        Column --> ColSortField{sort_field}
        Column --> ColFilter{filter}
    end

    subgraph Filters
        FiltersLens --> PanelFilter[Panel Filter]
        PanelFilter --> PanelFilterField{field}
        PanelFilter --> PanelFilterType{type}
        PanelFilter --> PanelFilterValue{value}
        PanelFilter --> PanelFilterOperator{operator}
        PanelFilter --> PanelFilterNegate{negate}

        DFilters --> DashboardFilter[Dashboard Filter]
        DashboardFilter --> DashboardFilterField{field}
        DashboardFilter --> DashboardFilterTypes{types}

        DashboardFilterTypes --> ExistsFilter[ExistsFilter]
        ExistsFilter --> ExistsField{field}
        ExistsFilter --> ExistsExists{exists}

        DashboardFilterTypes --> PhraseFilter[PhraseFilter]
        PhraseFilter --> PhraseField{field}
        PhraseFilter --> PhraseEquals{equals}

        DashboardFilterTypes --> PhrasesFilter[PhrasesFilter]
        PhrasesFilter --> PhrasesField{field}
        PhrasesFilter --> PhrasesInList{in_list}

        DashboardFilterTypes --> RangeFilter[RangeFilter]
        RangeFilter --> RangeField{field}
        RangeFilter --> RangeGte{gte}
        RangeFilter --> RangeLte{lte}
        RangeFilter --> RangeLt{lt}
        RangeFilter --> RangeGt{gt}

        DashboardFilterTypes --> NegationFilter[NegationFilter]
        NegationFilter --> NegationNot{not_filter}
        NegationNot --> DashboardFilterTypes
    end

    subgraph Queries
        DQuery --> KqlQuery[KqlQuery]
        KqlQuery --> Kql{kql}

        DQuery --> LuceneQuery[LuceneQuery]
        LuceneQuery --> Lucene{lucene}
    end

    subgraph Controls
        DControls --> OptionsListControl[optionsList]
        OptionsListControl --> OptionsId{id}
        OptionsListControl --> OptionsType{type}
        OptionsListControl --> OptionsWidth{width}
        OptionsListControl --> OptionsLabel{label}
        OptionsListControl --> OptionsDataView{data_view}
        OptionsListControl --> OptionsField{field}
        OptionsListControl --> OptionsSearchTechnique{search_technique}
        OptionsListControl --> OptionsSort[sort]

        DControls --> RangeSliderControl[rangeSlider]
        RangeSliderControl --> RangeId{id}
        RangeSliderControl --> RangeType{type}
        RangeSliderControl --> RangeWidth{width}
        RangeSliderControl --> RangeLabel{label}
        RangeSliderControl --> RangeDataView{data_view}
        RangeSliderControl --> RangeField{field}
        RangeSliderControl --> RangeStep{step}
    end

    subgraph Other Common Structures
        Grid{grid: {x, y, w, h}}
        Style{style: {type, size, color}}
        Palette --> PaletteType{type}
        Palette --> PaletteStops{stops}
        Sort --> SortBy{by}
        Sort --> SortDirection{direction}
        Axis --> AxisBottom{bottom}
        Axis --> AxisLeft{left}
        Axis --> AxisRight{right}
        AxisBottom --> AxisBottomShowMarker{show_current_time_marker}
        AxisLeft
        AxisRight --> AxisRightMetrics{metrics}
        Legend --> LegendVisible{is_visible}
        Legend --> LegendPosition{position}
        Appearance --> AppearanceValueLabels{value_labels}
        Appearance --> AppearanceFittingFunction{fitting_function}
        Appearance --> AppearanceEmphasizeFitting{emphasize_fitting}
        Appearance --> AppearanceCurveType{curve_type}
        Appearance --> AppearanceFillOpacity{fill_opacity}
        Appearance --> AppearanceMinBarHeight{min_bar_height}
        Appearance --> AppearanceHideEndzones{hide_endzones}
    end

    DimSort --> Sort
    ColSort --> Sort
    OptionsSort --> Sort
    AxisRightMetrics --> MetricObj