\n---\n\n<!-- Source: src/dashboard_compiler/dashboard/dashboard.md -->\n\n# Dashboard Configuration

The `dashboards` array is the root element in your YAML configuration file. Each dashboard defines the overall structure, content, and global settings for a Kibana dashboard.

## Minimal Configuration Example

A minimal dashboard requires a `name` and at least one panel.

```yaml
dashboards:
  -
    name: "Simple Log Dashboard"
    panels:
      - type: markdown
        content: "Welcome to the dashboard!"
        grid:
          x: 0
          y: 0
          w: 6
          h: 3
```

## Complex Configuration Example

This example showcases a dashboard with various settings, a default data view, a global query, filters, controls, and multiple panels.

```yaml
dashboards:
  -
    name: "Comprehensive Application Overview"
    id: "app-overview-001"
    description: "An overview of application performance and logs, with interactive filtering."
    data_view: "production-logs-*" # Default data view for all items unless overridden
    settings:
      margins: true
      titles: true
      sync:
        cursor: true
        tooltips: true
        colors: false # Use distinct color palettes per panel
      controls:
        label_position: "above"
        chain_controls: true
    query:
      kql: "NOT response_code:500" # Global KQL query
    filters:
      - field: "geo.country_iso_code"
        equals: "US"
      - field: "service.environment"
        in_list: ["production", "staging"]
    controls:
      - type: options
        label: "Filter by Region"
        data_view: "user-sessions-*"
        field: "user.geo.region_name"
        width: "medium"
    panels:
      - type: markdown
        content: "### Key Performance Indicators"
        grid: { x: 0, y: 0, w: 12, h: 2 }
      - type: lens
        title: "Total Requests"
        data_view: "apm-traces-*"
        chart:
          type: metric
          metrics:
            - type: count
        grid: { x: 0, y: 2, w: 4, h: 4 }
      - type: lens
        title: "Requests by Response Code"
        data_view: "apm-traces-*"
        chart:
          type: bar
          x_axis:
            field: "http.response.status_code"
          metrics:
            - type: count
        grid: { x: 4, y: 2, w: 8, h: 4 }
```

## Full Configuration Options

### Dashboard Object

The main object defining the dashboard.

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `name`        | `string`                                   | The title of the dashboard displayed in Kibana.                                                            | N/A              | Yes      |
| `id`          | `string`                                   | An optional unique identifier for the dashboard. If not provided, one will be generated based on the name. | Generated ID     | No       |
| `description` | `string`                                   | A brief description of the dashboard's purpose or content.                                                 | `""` (empty string) | No       |
| `settings`    | `DashboardSettings` object                 | Global settings for the dashboard. See [Dashboard Settings](#dashboard-settings).                          | See defaults below | No       |
| `data_view`   | `string`                                   | The default data view (index pattern) ID or title used by items in this dashboard unless overridden.       | `None`           | No       |
| `query`       | `Query` object                             | A global query (KQL or Lucene) applied to the dashboard. See [Queries Documentation](../queries/config.md). | `None`           | No       |
| `filters`     | `list of Filter objects`                   | A list of global filters applied to the dashboard. See [Filters Documentation](../filters/config.md).      | `[]` (empty list)| No       |
| `controls`    | `list of Control objects`                  | A list of control panels for the dashboard. See [Controls Documentation](../controls/config.md).           | `[]` (empty list)| No       |
| `panels`      | `list of Panel objects`                    | A list of panels defining the content and layout. See [Panels Documentation](../panels/base.md).           | `[]` (empty list)| Yes      |

### Dashboard Settings (`settings`)

Global settings for the dashboard, configured under the `dashboard.settings` path.

| YAML Key   | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ---------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `margins`  | `boolean`                                  | Whether to put space (margins) between panels in the dashboard.                                            | `true`           | No       |
| `sync`     | `DashboardSyncSettings` object             | Configures synchronization of cursor, tooltips, and colors across panels. See [Dashboard Sync Settings](#dashboard-sync-settings). | See defaults below | No       |
| `controls` | `ControlSettings` object                   | Global settings for controls on the dashboard. See [Controls Documentation](../controls/config.md#control-settings). | See defaults in Controls docs | No       |
| `titles`   | `boolean`                                  | Whether to display the titles in the panel headers.                                                        | `true`           | No       |

### Dashboard Sync Settings (`settings.sync`)

Configure whether cursor, tooltips, and colors should synchronize across panels.

| YAML Key   | Data Type | Description                                                                                                | Kibana Default   | Required |
| ---------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `cursor`   | `boolean` | Whether to synchronize the cursor across related panels.                                                   | `true`           | No       |
| `tooltips` | `boolean` | Whether to synchronize tooltips across related panels.                                                     | `true`           | No       |
| `colors`   | `boolean` | Whether to apply the same color palette to all panels on the dashboard.                                    | `true`           | No       |

## Methods (for programmatic generation)

While primarily declarative, the underlying Pydantic models for `Dashboard` support methods for adding components if you are generating configurations programmatically (not directly used in YAML):

* `add_filter(filter: FilterTypes)`: Adds a filter to the `filters` list.
* `add_control(control: ControlTypes)`: Adds a control to the `controls` list.
* `add_panel(panel: PanelTypes)`: Adds a panel to the `panels` list.

## Related Documentation

* [Controls Configuration](../controls/config.md)
* [Filters Configuration](../filters/config.md)
* [Queries Configuration](../queries/config.md)
* [Panels Overview](../panels/base.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/controls/config.md -->\n\n# Controls Configuration

Controls are interactive elements that can be added to a dashboard, allowing users to filter data or adjust visualization settings dynamically. They are defined as a list of control objects within each dashboard's `controls` field in the `dashboards:` array. Global behavior of controls can be managed via the `settings.controls` object.

## Minimal Configuration Examples

Here's a minimal example of an `options` list control:

```yaml
dashboards:
  -
    controls:
      - type: options
        label: "Filter by Status"
        data_view: "your-data-view-id" # Replace with your data view ID or title
        field: "status.keyword"      # Replace with the field to filter on
```

Here's a minimal example of a `range` slider control:

```yaml
dashboards:
  -
    controls:
      - type: range
        label: "Response Time (ms)"
        data_view: "your-data-view-id" # Replace with your data view ID or title
        field: "response.time"       # Replace with the numeric field
```

## Complex Configuration Example

This example demonstrates multiple controls with custom widths and global control settings:

```yaml
dashboards:
  -
    name: "Application Monitoring Dashboard"
    description: "Dashboard with interactive controls."
    data_view: "logs-*" # Default data view for panels
    settings:
      controls:
        label_position: "above"
        chain_controls: true
        click_to_apply: false
    controls:
      - type: options
        label: "Service Name"
        id: "service_filter"
        width: "medium"
        data_view: "apm-*"
        field: "service.name"
        singular: false
        match_technique: "contains"
        preselected: ["checkout-service"]
      - type: range
        label: "CPU Usage (%)"
        id: "cpu_range_filter"
        width: "large"
        data_view: "metrics-*"
        field: "system.cpu.user.pct"
        step: 0.05
      - type: time
        label: "Custom Time Slice"
        id: "time_slice_control"
        width: "small"
        start_offset: 0.1  # 10% from the start of the global time range
        end_offset: 0.9    # 90% from the start of the global time range
```

## Full Configuration Options

### Control Settings (`settings.controls`)

Global settings for all controls on the dashboard. These are configured under the `settings.controls` path in your main dashboard YAML.

| YAML Key                 | Data Type                      | Description                                                                                                | Kibana Default                                       | Required |
| ------------------------ | ------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | -------- |
| `label_position`         | `Literal['inline', 'above']`   | The position of the control label.                                                                         | `inline`                                             | No       |
| `apply_global_filters`   | `boolean`                      | Whether to apply global filters to the control.                                                            | `true`                                               | No       |
| `apply_global_timerange` | `boolean`                      | Whether to apply the global time range to the control.                                                     | `true`                                               | No       |
| `ignore_zero_results`    | `boolean`                      | Whether to ignore controls that return zero results. If `true`, controls with no results will be hidden.    | `false` (controls with zero results are shown)       | No       |
| `chain_controls`         | `boolean`                      | Whether to chain controls together, allowing one control's selection to filter the options in the next.    | `true` (hierarchical chaining)                       | No       |
| `click_to_apply`         | `boolean`                      | Whether to require users to click an apply button before applying changes.                                 | `false` (changes apply immediately)                  | No       |

### Options List Control

Allows users to select one or more values from a list to filter data.

| YAML Key           | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`             | `Literal['options']`                       | Specifies the control type.                                                                                | `options`        | Yes      |
| `id`               | `string`                                   | A unique identifier for the control. If not provided, one will be generated.                               | Generated UUID   | No       |
| `width`            | `Literal['small', 'medium', 'large']`      | The width of the control in the dashboard layout.                                                          | `medium`         | No       |
| `label`            | `string`                                   | The display label for the control. If not provided, a label may be inferred.                               | `None`           | No       |
| `data_view`        | `string`                                   | The ID or title of the data view (index pattern) the control operates on.                                  | N/A              | Yes      |
| `field`            | `string`                                   | The name of the field within the data view that the control is associated with.                            | N/A              | Yes      |
| `fill_width`       | `boolean`                                  | If true, the control will automatically adjust its width to fill available space.                          | `false`          | No       |
| `match_technique`  | `Literal['prefix', 'contains', 'exact']`   | The search technique used for filtering options. See [Match Technique Enum](#match-technique-enum).        | `prefix`         | No       |
| `wait_for_results` | `boolean`                                  | If set to true, delay the display of the list of values until the results are fully loaded.                | `false`          | No       |
| `preselected`      | `list of strings`                          | A list of options that are preselected when the control is initialized.                                    | `[]` (empty list)| No       |
| `singular`         | `boolean`                                  | If true, the control allows only a single selection from the options list.                                 | `false`          | No       |

### Range Slider Control

Allows users to select a range of numeric values to filter data.

| YAML Key     | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`       | `Literal['range']`                         | Specifies the control type.                                                                                | `range`          | Yes      |
| `id`         | `string`                                   | A unique identifier for the control. If not provided, one will be generated.                               | Generated UUID   | No       |
| `width`      | `Literal['small', 'medium', 'large']`      | The width of the control in the dashboard layout.                                                          | `medium`         | No       |
| `label`      | `string`                                   | The display label for the control. If not provided, a label may be inferred.                               | `None`           | No       |
| `data_view`  | `string`                                   | The ID or title of the data view (index pattern) the control operates on.                                  | N/A              | Yes      |
| `field`      | `string`                                   | The name of the field within the data view that the control is associated with.                            | N/A              | Yes      |
| `fill_width` | `boolean`                                  | If true, the control will automatically adjust its width to fill available space.                          | `false`          | No       |
| `step`       | `integer` or `float`                       | The step value for the range, defining the granularity of selections.                                      | `1`              | No       |

### Time Slider Control

Allows users to select a sub-section of the dashboard's current time range. This control does not use a `data_view` or `field` as it operates on the global time context.

| YAML Key       | Data Type                                  | Description                                                                                                                                  | Kibana Default   | Required |
| -------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`         | `Literal['time']`                          | Specifies the control type.                                                                                                                  | `time`           | Yes      |
| `id`           | `string`                                   | A unique identifier for the control. If not provided, one will be generated.                                                                 | Generated UUID   | No       |
| `width`        | `Literal['small', 'medium', 'large']`      | The width of the control in the dashboard layout.                                                                                            | `medium`         | No       |
| `label`        | `string`                                   | The display label for the control. If not provided, a label may be inferred.                                                                 | `None`           | No       |
| `start_offset` | `float` (between 0.0 and 1.0)              | The start offset for the time range as a percentage of the global time range (e.g., `0.25` for 25%). Must be less than `end_offset`.         | `0.0` (0%)       | No       |
| `end_offset`   | `float` (between 0.0 and 1.0)              | The end offset for the time range as a percentage of the global time range (e.g., `0.75` for 75%). Must be greater than `start_offset`.       | `1.0` (100%)     | No       |

**Note on Time Slider Offsets:** The YAML configuration expects `start_offset` and `end_offset` as float values between 0.0 (0%) and 1.0 (100%). Kibana internally represents these as percentages from 0.0 to 100.0. If not provided, Kibana defaults to `0.0` for start and `100.0` for end.

## Match Technique Enum (`match_technique`)

This enum defines the possible search techniques used for filtering options in an `OptionsListControl`.

* `prefix`: (Default) Filters options starting with the input text.
* `contains`: Filters options containing the input text.
* `exact`: Filters options matching the input text exactly.

## Related Documentation

* [Dashboard Configuration](./../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/filters/config.md -->\n\n# Filters Configuration

Filters are used to narrow down the data displayed on a dashboard or within individual panels. They are defined as a list of filter objects, typically under the `filters` key of a `dashboard` object or a panel that supports filtering.

## Minimal Configuration Examples

**Exists Filter:** Check if the `error.message` field exists.

```yaml
filters:
  - exists: "error.message"
```

**Phrase Filter:** Find documents where `status.keyword` is exactly "active".

```yaml
filters:
  - field: "status.keyword"
    equals: "active"
```

**Phrases Filter (using `in` alias):** Find documents where `event.category` is "authentication" OR "network".

```yaml
filters:
  - field: "event.category"
    in: ["authentication", "network"]
```

**Range Filter:** Find documents where `response_time` is between 100 (inclusive) and 500 (exclusive).

```yaml
filters:
  - field: "response_time"
    gte: "100" # Values are typically strings, Kibana handles conversion
    lt: "500"
```

## Complex Configuration Example

This example demonstrates a combination of filter types, including logical junctions (`and`, `or`) and a modifier (`not`).

```yaml
filters:
  - alias: "Successful Logins from US or CA"
    and: # `and_filters` in Pydantic, `and` in YAML
      - field: "event.action"
        equals: "user_login"
      - field: "event.outcome"
        equals: "success"
      - or: # `or_filters` in Pydantic, `or` in YAML
          - field: "source.geo.country_iso_code"
            equals: "US"
          - field: "source.geo.country_iso_code"
            equals: "CA"
  - alias: "Exclude test users"
    not: # `not_filter` in Pydantic, `not` in YAML
      field: "user.name"
      in: ["test_user_01", "qa_bot"]
  - exists: "transaction.id"
    disabled: true # This filter is defined but currently disabled
  - dsl:
      query_string:
        query: "message:(*error* OR *exception*) AND NOT logger_name:debug"
```

## Full Configuration Options

All filter types can include the following base fields:

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `alias`    | `string`  | An optional alias for the filter, used for display purposes in Kibana.           | `None`         | No       |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Exists Filter

Checks for the existence of a specific field.

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `exists`   | `string`  | The field name to check for existence.                                           | N/A            | Yes      |
| `alias`    | `string`  | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Phrase Filter

Matches documents where a specific field contains an exact phrase.

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `field`    | `string`  | The field name to apply the filter to.                                           | N/A            | Yes      |
| `equals`   | `string`  | The exact phrase value that the field must match.                                | N/A            | Yes      |
| `alias`    | `string`  | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Phrases Filter

Matches documents where a specific field contains one or more of the specified phrases.

| YAML Key   | Data Type         | Description                                                                      | Kibana Default | Required |
| ---------- | ----------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `field`    | `string`          | The field name to apply the filter to.                                           | N/A            | Yes      |
| `in`       | `list of strings` | A list of phrases. Documents must match at least one of these phrases.           | N/A            | Yes      |
| `alias`    | `string`          | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean`         | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Range Filter

Matches documents where a numeric or date field falls within a specified range. At least one of `gte`, `lte`, `gt`, or `lt` must be provided.

| YAML Key   | Data Type | Description                                                                      | Kibana Default | Required                |
| ---------- | --------- | -------------------------------------------------------------------------------- | -------------- | ----------------------- |
| `field`    | `string`  | The field name to apply the filter to.                                           | N/A            | Yes                     |
| `gte`      | `string`  | Greater than or equal to value.                                                  | `None`         | No (but one must exist) |
| `lte`      | `string`  | Less than or equal to value.                                                     | `None`         | No (but one must exist) |
| `gt`       | `string`  | Greater than value.                                                              | `None`         | No (but one must exist) |
| `lt`       | `string`  | Less than value.                                                                 | `None`         | No (but one must exist) |
| `alias`    | `string`  | An optional alias for the filter.                                                | `None`         | No                      |
| `disabled` | `boolean` | If `true`, the filter is defined but not applied.                                | `false`        | No                      |

### Custom Filter

Allows for defining a custom Elasticsearch Query DSL filter.

| YAML Key   | Data Type        | Description                                                                      | Kibana Default | Required |
| ---------- | ---------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `dsl`      | `object (dict)`  | The custom Elasticsearch query definition.                                       | N/A            | Yes      |
| `alias`    | `string`         | An optional alias for the filter.                                                | `None`         | No       |
| `disabled` | `boolean`        | If `true`, the filter is defined but not applied.                                | `false`        | No       |

### Negate Filter (`not`)

Excludes documents that match the nested filter. This filter itself does not have `alias` or `disabled` directly; those would apply to the filter it contains or a parent filter.

| YAML Key | Data Type      | Description                                                                      | Kibana Default | Required |
| -------- | -------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `not`    | `FilterTypes`  | The filter object to negate. Can be any of the other filter types or junctions.  | N/A            | Yes      |

### And Filter (`and`)

Matches documents that satisfy ALL of the specified nested filters.

| YAML Key   | Data Type               | Description                                                                      | Kibana Default | Required |
| ---------- | ----------------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `and`      | `list of FilterTypes`   | A list of filter objects. All filters must match for a document to be included.  | N/A            | Yes      |
| `alias`    | `string`                | An optional alias for the AND group.                                             | `None`         | No       |
| `disabled` | `boolean`               | If `true`, the entire AND group is defined but not applied.                      | `false`        | No       |

### Or Filter (`or`)

Matches documents that satisfy AT LEAST ONE of the specified nested filters.

| YAML Key   | Data Type               | Description                                                                      | Kibana Default | Required |
| ---------- | ----------------------- | -------------------------------------------------------------------------------- | -------------- | -------- |
| `or`       | `list of FilterTypes`   | A list of filter objects. At least one filter must match.                        | N/A            | Yes      |
| `alias`    | `string`                | An optional alias for the OR group.                                              | `None`         | No       |
| `disabled` | `boolean`               | If `true`, the entire OR group is defined but not applied.                       | `false`        | No       |

## Related Documentation

* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../queries/config.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/base.md -->\n\n# Base Panel Configuration

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

* [Markdown Panel](./markdown/markdown.md)
* [Links Panel](./links/links.md)
* [Search Panel](./search/search.md) (*Documentation to be created/updated*)
* **Charts:**
  * [Lens Panel (for various chart types like bar, line, area, pie, metric, table)](./charts/lens/lens.md)
  * [ESQL Panel (for ESQL-driven visualizations)](./charts/esql/esql.md) (*Documentation to be created/updated*)
  * (*Other chart types like Vega, Timelion, TSVB might be added here if supported*)

## Related Documentation

* [Dashboard Configuration](../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/esql.md -->\n\n# ESQL Panel

The `esql` panel is used to display data visualizations based on an ESQL query.

```yaml
- panel:
    type: esql
    # Common panel fields (id, title, description, grid, hide_title) also apply
    query: string         # (Required) The ESQL query string.
    chart: object         # (Required) The chart configuration for the ESQL panel.
```

## Fields

* `type` (required, string): Must be `esql`.
* `query` (required, string): The ESQL query string that determines the data for the chart.
* `chart` (required, object): The chart configuration for the ESQL panel. See [ESQL Chart Types](#esql-chart-types) for details.

## ESQL Chart Types

ESQL panels can display various chart types based on the results of the ESQL query. The configuration for the chart is defined within the `chart` object.

### ESQL Pie Chart

Represents a Pie chart configuration within an ESQL panel. Pie charts are used to visualize the proportion of categories from the ESQL query results.

```yaml
chart:
  type: pie           # (Required) Must be 'pie'.
  metric: object      # (Required) The metric that determines the size of the slices.
  slice_by: list      # (Required) The dimensions that determine the slices.
  appearance: object  # (Optional) Chart appearance formatting options.
  titles_and_text: object # (Optional) Titles and text formatting options.
  legend: object      # (Optional) Legend formatting options.
```

* **Fields:**
  * `type` (required, string): Must be `pie`.
  * `metric` (required, object): A metric that determines the size of the slice of the pie chart. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `slice_by` (required, list of objects): The dimensions that determine the slices of the pie chart. This is a list of [ESQL Dimension Objects](../dimensions/dimension.md#esql-dimension-type) referencing columns from the ESQL query results.
  * `appearance` (optional, object): Formatting options for the chart appearance, including donut size. See [Pie Chart Appearance](../lens.md#pie-chart-appearance) for details.
  * `titles_and_text` (optional, object): Formatting options for the chart titles and text. See [Pie Chart Titles and Text](../lens.md#pie-chart-titles-and-text) for details.
  * `legend` (optional, object): Formatting options for the chart legend. See [Pie Chart Legend](../lens.md#pie-chart-legend) for details.

### ESQL Metric Chart

Represents a Metric chart configuration within an ESQL panel. Metric charts display a single value or a list of values from the ESQL query results.

```yaml
chart:
  type: metric        # (Required) Must be 'metric'.
  primary: object     # (Required) The primary metric to display.
  secondary: object   # (Optional) An optional secondary metric.
  maximum: object     # (Optional) An optional maximum metric.
  breakdown: object   # (Optional) An optional breakdown dimension.
```

* **Fields:**
  * `type` (required, string): Must be `metric`.
  * `primary` (required, object): The primary metric to display in the chart. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `secondary` (optional, object): An optional secondary metric to display alongside the primary metric. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `maximum` (optional, object): An optional maximum metric to display, often used for comparison or thresholds. This should be an [ESQL Metric Object](../metrics/metric.md#esql-metric) referencing a column from the ESQL query results.
  * `breakdown` (optional, object): An optional breakdown dimension to display. This should be an [ESQL Dimension Object](../dimensions/dimension.md#esql-dimension-type) referencing a column from the ESQL query results.

## Related Documentation

* [Base Panel Object](../base.md)
* [Metric Objects](../metrics/metric.md)
* [Dimension Objects](../dimensions/dimension.md)
* [Pie Chart Appearance](../lens.md#pie-chart-appearance)
* [Pie Chart Titles and Text](../lens.md#pie-chart-titles-and-text)
* [Pie Chart Legend](../lens.md#pie-chart-legend)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/esql/esql.md -->\n\n# ESQL Panel Configuration

ESQL panels leverage the power of Elasticsearch Query Language (ESQL) to create visualizations. This allows for more complex data transformations and aggregations directly within the query that feeds the chart.

The `ESQLPanel` is the primary container. Its `esql` field holds the ESQL query, and its `chart` field defines the specific type of visualization (e.g., `metric`, `pie`).

## Minimal Configuration Examples

**Minimal ESQL Metric Chart:**

```yaml
# Within a dashboard's 'panels' list:
# - type: charts  # This is the ESQLPanel type (distinguished by `esql` field)
#   title: "Total Processed Events"
#   grid: { x: 0, y: 0, w: 4, h: 3 }
#   esql: |
#     FROM my_event_stream
#     | STATS total_events = COUNT(event_id)
#   chart:
#     type: metric
#     primary:
#       field: "total_events" # Must match a column name from ESQL query

# For a complete dashboard structure:
dashboard:
  name: "ESQL Metrics Dashboard"
  panels:
    - type: charts
      title: "Total Processed Events"
      grid: { x: 0, y: 0, w: 4, h: 3 }
      esql: |
        FROM my_event_stream
        | STATS total_events = COUNT(event_id)
      chart:
        type: metric # Specifies an ESQLMetricChart
        primary:
          field: "total_events"
          # Label can be inferred from field if not provided
```

**Minimal ESQL Pie Chart:**

```yaml
# Within a dashboard's 'panels' list:
# - type: charts
#   title: "Events by Type (ESQL)"
#   grid: { x: 4, y: 0, w: 8, h: 3 }
#   esql: |
#     FROM my_event_stream
#     | STATS event_count = COUNT(event_id) BY event_type
#     | LIMIT 5
#   chart:
#     type: pie
#     metric:
#       field: "event_count" # Must match a metric column from ESQL
#     slice_by:
#       - field: "event_type"  # Must match a dimension column from ESQL

# For a complete dashboard structure:
dashboard:
  name: "ESQL Event Analysis"
  panels:
    - type: charts
      title: "Events by Type (ESQL)"
      grid: { x: 4, y: 0, w: 8, h: 3 }
      esql: |
        FROM my_event_stream
        | STATS event_count = COUNT(event_id) BY event_type
        | ORDER event_count DESC
        | LIMIT 5
      chart:
        type: pie # Specifies an ESQLPieChart
        metric:
          field: "event_count"
        slice_by:
          - field: "event_type"
```

## Full Configuration Options

### ESQL Panel (`type: charts` with an `esql` field)

This is the main object for an ESQL-based visualization. It inherits from the [Base Panel Configuration](../base.md). The presence of the `esql` field distinguishes it from a Lens panel.

| YAML Key | Data Type                                  | Description                                                                                                | Kibana Default                  | Required |
| -------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type`   | `Literal['charts']`                        | Specifies the panel type. For ESQL panels, this is `charts`.                                               | `charts`                        | Yes      |
| `id`     | `string`                                   | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID                    | No       |
| `title`  | `string`                                   | The title displayed on the panel header. Inherited from BasePanel.                                         | `""` (empty string)             | No       |
| `hide_title` | `boolean`                              | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`                         | No       |
| `description`| `string`                               | A brief description of the panel. Inherited from BasePanel.                                                | `""` (empty string, if `None`)  | No       |
| `grid`   | `Grid` object                              | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                             | Yes      |
| `esql`   | `string` or `ESQLQuery` object             | The ESQL query string. See [Queries Documentation](../../queries/config.md#esql-query).                    | N/A                             | Yes      |
| `chart`  | `ESQLChartTypes` object                    | Defines the actual ESQL visualization configuration. This will be one of [ESQL Metric Chart](#esql-metric-chart) or [ESQL Pie Chart](#esql-pie-chart). | N/A                             | Yes      |

---

## ESQL Metric Chart (`chart.type: metric`)

Displays a single primary metric derived from an ESQL query, optionally with a secondary metric, a maximum value, and a breakdown dimension. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key    | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`      | `Literal['metric']`                        | Specifies the chart type as an ESQL Metric visualization.                                                  | `metric`         | Yes      |
| `id`        | `string`                                   | An optional unique identifier for this specific chart layer.                                               | Generated ID     | No       |
| `primary`   | `ESQLMetric` object                        | The primary metric to display. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A              | Yes      |
| `secondary` | `ESQLMetric` object                        | An optional secondary metric. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | `None`           | No       |
| `maximum`   | `ESQLMetric` object                        | An optional maximum metric. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | `None`           | No       |
| `breakdown` | `ESQLDimension` object                     | An optional dimension to break down the metric by. Its `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | `None`           | No       |

**Example (ESQL Metric Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: metric
# primary:
#   field: "avg_response_time" # Column from ESQL: ... | STATS avg_response_time = AVG(response.time)
# secondary:
#   field: "p95_response_time" # Column from ESQL: ... | STATS p95_response_time = PERCENTILE(response.time, 95.0)
# breakdown:
#   field: "service_name"      # Column from ESQL: ... BY service_name
```

---

## ESQL Pie Chart (`chart.type: pie`)

Visualizes proportions of categories using slices of a pie or a donut chart, with data sourced from an ESQL query. The `field` names in the chart configuration **must** correspond to column names produced by the ESQL query.

| YAML Key          | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`            | `Literal['pie']`                           | Specifies the chart type as an ESQL Pie visualization.                                                     | `pie`            | Yes      |
| `id`              | `string`                                   | An optional unique identifier for this specific chart layer.                                               | Generated ID     | No       |
| `metric`          | `ESQLMetric` object                        | The metric that determines the size of each slice. Its `field` refers to an ESQL result column. See [ESQL Metric Column](#esql-metric-column). | N/A              | Yes      |
| `slice_by`        | `list of ESQLDimension` objects            | One or more dimensions that determine how the pie is sliced. Each `field` refers to an ESQL result column. See [ESQL Dimension Column](#esql-dimension-column). | N/A              | Yes      |
| `appearance`      | `PieChartAppearance` object                | Formatting options for the chart appearance. See [Pie Chart Appearance](#pie-chart-appearance-formatting) (shared with Lens). | `None`           | No       |
| `titles_and_text` | `PieTitlesAndText` object                  | Formatting options for slice labels and values. See [Pie Titles and Text](#pie-titles-and-text-formatting) (shared with Lens). | `None`           | No       |
| `legend`          | `PieLegend` object                         | Formatting options for the chart legend. See [Pie Legend](#pie-legend-formatting) (shared with Lens).        | `None`           | No       |
| `color`           | `ColorMapping` object                      | Formatting options for the chart color palette. See [Color Mapping](#color-mapping-formatting) (shared with Lens). | `None`           | No       |

**Example (ESQL Pie Chart):**

```yaml
# Within an ESQLPanel's 'chart' field:
# type: pie
# metric:
#   field: "error_count"  # Column from ESQL: ... | STATS error_count = COUNT(error.code) BY error.type
# slice_by:
#   - field: "error_type" # Column from ESQL
# appearance:
#   donut: "small"
```

---

## ESQL Columns

For ESQL panels, the `primary`, `secondary`, `maximum` (in metric charts) and `metric`, `slice_by` (in pie charts) fields refer to columns that **must be present in the output of your ESQL query**.

### ESQL Metric Column

Used to specify a metric column from your ESQL query result.

| YAML Key | Data Type | Description                                                                                                | Kibana Default   | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id`     | `string`  | An optional unique identifier for this metric column definition.                                           | Generated ID     | No       |
| `field`  | `string`  | The name of the column in your ESQL query result that represents the metric value.                         | N/A              | Yes      |

### ESQL Dimension Column

Used to specify a dimension/grouping column from your ESQL query result.

| YAML Key | Data Type | Description                                                                                                | Kibana Default   | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id`     | `string`  | An optional unique identifier for this dimension column definition.                                          | Generated ID     | No       |
| `field`  | `string`  | The name of the column in your ESQL query result that represents the dimension.                            | N/A              | Yes      |

---

## Pie Chart Specific Formatting (Shared with Lens)

ESQL Pie Charts share the same formatting options for appearance, titles/text, legend, and colors as Lens Pie Charts.

### Pie Chart Appearance Formatting (`appearance` field)

| YAML Key | Data Type                             | Description                                      | Kibana Default   | Required |
| -------- | ------------------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `donut`  | `Literal['small', 'medium', 'large']` | If set, creates a donut chart with the specified hole size. | `None` (pie)     | No       |

### Pie Titles and Text Formatting (`titles_and_text` field)

| YAML Key               | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `slice_labels`         | `Literal['hide', 'inside', 'auto']`        | How to display labels for each slice.                                                                      | `auto`           | No       |
| `slice_values`         | `Literal['hide', 'integer', 'percent']`    | How to display the value for each slice.                                                                   | `percent`        | No       |
| `value_decimal_places` | `integer` (0-10)                           | Number of decimal places for slice values.                                                                 | `2`              | No       |

### Pie Legend Formatting (`legend` field)

| YAML Key            | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `visible`           | `Literal['show', 'hide', 'auto']`          | Controls legend visibility.                                                                                | `auto`           | No       |
| `width`             | `Literal['small', 'medium', 'large', 'extra_large']` | Width of the legend area.                                                                                  | `medium`         | No       |
| `truncate_labels`   | `integer` (0-5)                            | Max number of lines for legend labels before truncating. `0` disables truncation.                          | `1`              | No       |

### Color Mapping Formatting (`color` field)

| YAML Key  | Data Type | Description                                      | Kibana Default   | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `palette` | `string`  | The ID of the color palette to use (e.g., `default`, `elasticColors`). | `default`        | Yes      |

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../../queries/config.md#esql-query)
* Elasticsearch ESQL Reference (external)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/lens.md -->\n\n# Lens Panel

The `lens` panel is used to display data visualizations created with Kibana Lens.

```yaml
- panel:
    type: lens
    # Common panel fields (id, title, description, grid, hide_title) also apply
    chart: object         # (Required) The chart configuration for the Lens panel.
```

## Fields

* `type` (required, string): Must be `lens`.
* `chart` (required, object): The chart configuration for the Lens panel. See [Lens Chart Types](#lens-chart-types) for details.

## Lens Chart Types

Lens panels can display various chart types. The configuration for the chart is defined within the `chart` object.

### Lens Pie Chart

Represents a Pie chart configuration within a Lens panel. Pie charts are used to visualize the proportion of categories.

```yaml
chart:
  type: pie           # (Required) Must be 'pie'.
  metric: object      # (Required) The metric that determines the size of the slices.
  slice_by: list      # (Required) The dimensions that determine the slices.
  appearance: object  # (Optional) Chart appearance formatting options.
  titles_and_text: object # (Optional) Titles and text formatting options.
  legend: object      # (Optional) Legend formatting options.
```

* **Fields:**
  * `type` (required, string): Must be `pie`.
  * `metric` (required, object): A metric that determines the size of the slice of the pie chart. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
  * `slice_by` (required, list of objects): The dimensions that determine the slices of the pie chart. This is a list of Lens dimension objects. See [Dimension Objects](../dimensions/dimension.md) for details on Lens dimension types.
  * `appearance` (optional, object): Formatting options for the chart appearance, including donut size. See [Pie Chart Appearance](#pie-chart-appearance) for details.
  * `titles_and_text` (optional, object): Formatting options for the chart titles and text. See [Pie Chart Titles and Text](#pie-chart-titles-and-text) for details.
  * `legend` (optional, object): Formatting options for the chart legend. See [Pie Chart Legend](#pie-chart-legend) for details.

### Lens Metric Chart

Represents a Metric chart configuration within a Lens panel. Metric charts display a single value or a list of values, often representing key performance indicators.

```yaml
chart:
  type: metric        # (Required) Must be 'metric'.
  primary: object     # (Required) The primary metric to display.
  secondary: object   # (Optional) An optional secondary metric.
  maximum: object     # (Optional) An optional maximum metric.
  breakdown: object   # (Optional) An optional breakdown dimension.
```

* **Fields:**
  * `type` (required, string): Must be `metric`.
  * `primary` (required, object): The primary metric to display in the chart. This is the main value shown in the metric visualization. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
  * `secondary` (optional, object): An optional secondary metric to display alongside the primary metric. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
  * `maximum` (optional, object): An optional maximum metric to display, often used for comparison or thresholds. See [Metric Objects](../metrics/metric.md) for details on Lens metric types.
  * `breakdown` (optional, object): An optional breakdown dimension to display. See [Dimension Objects](../dimensions/dimension.md) for details on Lens dimension types.

## Pie Chart Appearance

Represents chart appearance formatting options for pie charts.

```yaml
appearance:
  donut: string       # (Optional) The size of the donut hole (small, medium, large).
```

* `donut` (optional, string): The size of the donut hole in the pie chart. Options are `small`, `medium`, or `large`.

## Pie Chart Titles and Text

Represents titles and text formatting options for pie charts.

```yaml
titles_and_text:
  slice_labels: string # (Optional) Controls slice label visibility (hide, show, auto). Defaults to "auto".
  slice_values: string # (Optional) Controls slice value display (hide, integer, percent). Defaults to "percent".
  value_decimal_places: integer # (Optional) Number of decimal places for slice values (0-10). Defaults to 2.
```

* `slice_labels` (optional, string): Controls the visibility of slice labels in the pie chart. Valid values are `hide`, `show`, or `auto`. Kibana defaults to `auto` if not specified.
* `slice_values` (optional, string): Controls the display of slice values in the pie chart. Valid values are `hide`, `integer`, or `percent`. Kibana defaults to `percentage` if not specified.
* `value_decimal_places` (optional, integer): Controls the number of decimal places for slice values in the pie chart. Value should be between 0 and 10. Kibana defaults to 2, if not specified.

## Pie Chart Legend

Represents legend formatting options for pie charts.

```yaml
legend:
  visible: string     # (Optional) Visibility of the legend (show, hide, auto). Defaults to "auto".
  width: string       # (Optional) Width of the legend (small, medium, large, extra_large). Defaults to "medium".
  truncate_labels: integer # (Optional) Number of lines to truncate labels (0-5). Defaults to 1.
```

* `visible` (optional, string): Visibility of the legend in the pie chart. Valid values are `show`, `hide`, or `auto`. Kibana defaults to `auto` if not specified.
* `width` (optional, string): Width of the legend in the pie chart. Valid values are `small`, `medium`, `large`, or `extra_large`. Kibana defaults to `medium` if not specified.
* `truncate_labels` (optional, integer): Number of lines to truncate the legend labels to. Value should be between 0 and 5. Kibana defaults to 1 if not specified. Set to 0 to disable truncation.

## Related Documentation

* [Base Panel Object](../base.md)
* [Metric Objects](../metrics/metric.md)
* [Dimension Objects](../dimensions/dimension.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/lens/dimensions/dimension.md -->\n\n# Dimension Objects

Dimension objects are used within chart panels (Lens and ESQL) to define how data is grouped or categorized, often corresponding to an axis or a breakdown.

## Base Dimension Fields

All dimension types inherit from a base dimension with the following optional field:

* `id` (optional, string): A unique identifier for the dimension. If not provided, one may be generated during compilation.

## Lens Dimension Types

Lens charts use the following dimension types:

### Base Lens Dimension Fields

All Lens dimension types inherit from a base Lens dimension with the following optional fields:

* `label` (optional, string): The display label for the dimension. If not provided, a label may be inferred from the field and type.

### Lens Top Values Dimension

Represents a top values dimension configuration within a Lens chart. Top values dimensions are used for aggregating data based on unique values of a field.

```yaml
- type: values        # (Required) Must be 'values'.
  field: string       # (Required) The name of the field to use for the dimension.
  size: integer       # (Optional) The number of top terms to display.
  sort: object        # (Optional) Sort configuration. See [Sort Object](../shared/config.md#sort-object) for details.
  other_bucket: boolean # (Optional) If true, show a bucket for terms not included in the top size. Defaults to false.
  missing_bucket: boolean # (Optional) If true, show a bucket for documents with a missing value. Defaults to false.
  include: list       # (Optional) A list of terms to include.
  exclude: list       # (Optional) A list of terms to exclude.
  include_is_regex: boolean # (Optional) If true, treat include values as regex. Defaults to false.
  exclude_is_regex: boolean # (Optional) If true, treat exclude values as regex. Defaults to false.
  # Base Lens Dimension fields also apply
```

* **Fields:**
  * `type` (required, string): Must be `values`.
  * `field` (required, string): The name of the field in the data view that this dimension is based on.
  * `size` (optional, integer): The number of top terms to display.
  * `sort` (optional, object): Defines how the terms are sorted. See [Sort Object](../shared/config.md#sort-object).
  * `other_bucket` (optional, boolean): If `true`, a bucket for all other terms not included in the top `size` will be shown. Defaults to `false`.
  * `missing_bucket` (optional, boolean): If `true`, a bucket for documents with a missing value for the field will be shown. Defaults to `false`.
  * `include` (optional, list of strings): A list of term values or regex patterns to include.
  * `exclude` (optional, list of strings): A list of term values or regex patterns to exclude.
  * `include_is_regex` (optional, boolean): If `true`, the values in the `include` list will be treated as regular expressions. Defaults to `false`.
  * `exclude_is_regex` (optional, boolean): If `true`, the values in the `exclude` list will be treated as regular expressions. Defaults to `false`.
* **Example:**

    ```yaml
    - type: values
      field: user.country
      label: Users by Country
      size: 5
      sort:
        by: "_count"
        direction: desc
      other_bucket: true
    ```

### Lens Date Histogram Dimension

Represents a date histogram dimension configuration within a Lens chart. Date histogram dimensions are used for aggregating data into buckets based on time intervals.

```yaml
- type: date_histogram # (Required) Must be 'date_histogram'.
  field: string       # (Required) The name of the field to use for the dimension.
  minimum_interval: string # (Optional) The minimum time interval for the buckets (e.g., 'auto', '1h', '1d'). Defaults to 'auto'.
  partial_intervals: boolean # (Optional) If true, show partial intervals. Defaults to true.
  collapse: string    # (Optional) The aggregation to use for collapsing intervals. See [Collapse Aggregation Enum](#collapse-aggregation-enum) for details.
  # Base Lens Dimension fields also apply
```

* **Fields:**
  * `type` (required, string): Must be `date_histogram`.
  * `field` (required, string): The name of the field in the data view that this dimension is based on.
  * `minimum_interval` (optional, string): The minimum time interval for the histogram buckets. Defaults to `auto` if not specified.
  * `partial_intervals` (optional, boolean): If `true`, show partial intervals. Kibana defaults to `true` if not specified.
  * `collapse` (optional, string): The aggregation to use for the dimension when intervals are collapsed. See [Collapse Aggregation Enum](#collapse-aggregation-enum).
* **Example:**

    ```yaml
    - type: date_histogram
      field: "@timestamp"
      label: Events over Time
      minimum_interval: 1d
    ```

### Lens Filters Dimension

Represents a filters dimension configuration within a Lens chart. Filters dimensions are used for filtering data based on a set of defined filters.

```yaml
- type: filters       # (Required) Must be 'filters'.
  filters: list       # (Required) A list of filters to use for the dimension.
  # Base Lens Dimension fields also apply
```

* **Fields:**
  * `type` (required, string): Must be `filters`.
  * `filters` (required, list of objects): A list of filter objects. Each object should have a `query` (see [Queries Documentation](../queries/config.md)) and an optional `label` (string).
* **Example:**

    ```yaml
    - type: filters
      label: Response Status
      filters:
        - query:
            kql: "http.response.status_code >= 200 and http.response.status_code < 300"
          label: Success
        - query:
            kql: "http.response.status_code >= 400 and http.response.status_code < 500"
          label: Client Error
        - query:
            kql: "http.response.status_code >= 500"
          label: Server Error
    ```

### Lens Intervals Dimension

Represents an intervals dimension configuration within a Lens chart. Intervals dimensions are used for aggregating data based on numeric ranges.

```yaml
- type: intervals     # (Required) Must be 'intervals'.
  field: string       # (Required) The name of the field to use for the dimension.
  intervals: list     # (Optional) A list of interval objects.
  granularity: integer # (Optional) Interval granularity (1-7). Defaults to 4.
  collapse: string    # (Optional) The aggregation to use for collapsing intervals. See [Collapse Aggregation Enum](#collapse-aggregation-enum) for details.
  empty_bucket: boolean # (Optional) If true, show a bucket for documents with a missing value. Defaults to false.
  # Base Lens Dimension fields also apply
```

* **Fields:**
  * `type` (required, string): Must be `intervals`.
  * `field` (required, string): The name of the field in the data view that this dimension is based on.
  * `intervals` (optional, list of objects): A list of interval objects. Each object should have optional `from` (integer) and `to` (integer) values and an optional `label` (string). If not provided, intervals will be automatically picked.
  * `granularity` (optional, integer): Interval granularity divides the field into evenly spaced intervals based on the minimum and maximum values for the field. Kibana defaults to 4 if not specified. Value should be between 1 and 7.
  * `collapse` (optional, string): The aggregation to use for the dimension when intervals are collapsed. See [Collapse Aggregation Enum](#collapse-aggregation-enum).
  * `empty_bucket` (optional, boolean): If `true`, show a bucket for documents with a missing value for the field. Defaults to `false`.
* **Example:**

    ```yaml
    - type: intervals
      field: response_time
      label: Response Time Intervals
      intervals:
        - to: 100
          label: "< 100ms"
        - from: 100
          to: 500
          label: "100ms - 500ms"
        - from: 500
          label: "> 500ms"
    ```

## ESQL Dimension Type

ESQL charts use a single dimension type defined by the ESQL query.

### ESQL Dimension

A dimension that is defined in the ESQL query.

```yaml
- field: string       # (Required) The field in the data view that this dimension is based on.
  # Base Dimension fields also apply
```

* **Fields:**
  * `field` (required, string): The field in the data view that this dimension is based on. This field should correspond to a column returned by the ESQL query.
* **Example:**

    ```yaml
    - field: country
      label: Country from ESQL
    ```

## Collapse Aggregation Enum

This enum defines the possible aggregation types to use when collapsing intervals in Lens Date Histogram and Intervals dimensions.

* `SUM`
* `MIN`
* `MAX`
* `AVG`

## Related Structures

* [Sort Object](../shared/config.md#sort-object)
* [Queries Documentation](../queries/config.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/lens/lens.md -->\n\n# Lens Panel Configuration

Lens panels in Kibana provide a flexible and user-friendly way to create various types of visualizations, such as metric displays, pie charts, bar charts, line charts, and more. This document covers the YAML configuration for Lens panels using this compiler.

The `LensPanel` is the primary container. Its `chart` field will define the specific type of visualization (e.g., `metric`, `pie`).

## Minimal Configuration Examples

**Minimal Lens Metric Chart:**

```yaml
# Within a dashboard's 'panels' list:
# - type: charts  # This is the LensPanel type
#   title: "Total Users"
#   grid: { x: 0, y: 0, w: 4, h: 3 }
#   chart:
#     type: metric
#     primary:
#       aggregation: "unique_count"
#       field: "user.id" # Field for unique count

# For a complete dashboard structure:
dashboard:
  name: "Key Metrics Dashboard"
  panels:
    - type: charts
      title: "Total Users"
      grid: { x: 0, y: 0, w: 4, h: 3 }
      query: # Optional panel-specific query
        kql: "event.dataset:website.visits"
      chart:
        type: metric # Specifies a LensMetricChart
        primary:
          aggregation: "unique_count"
          field: "user.id"
          label: "Unique Visitors"
```

**Minimal Lens Pie Chart:**

```yaml
# Within a dashboard's 'panels' list:
# - type: charts
#   title: "Traffic by Source"
#   grid: { x: 4, y: 0, w: 8, h: 3 }
#   chart:
#     type: pie
#     data_view: "your-data-view-id" # Required for pie chart
#     metric:
#       aggregation: "count" # Count of documents for slice size
#     slice_by:
#       - type: values
#         field: "source.medium" # Field to create slices from

# For a complete dashboard structure:
dashboard:
  name: "Traffic Analysis"
  panels:
    - type: charts
      title: "Traffic by Source"
      grid: { x: 4, y: 0, w: 8, h: 3 }
      chart:
        type: pie # Specifies a LensPieChart
        data_view: "weblogs-*"
        metric:
          aggregation: "count"
          label: "Sessions"
        slice_by:
          - type: values
            field: "source.medium"
            label: "Traffic Source"
            size: 5 # Top 5 sources
```

## Full Configuration Options

### Lens Panel (`type: charts`)

This is the main object for a Lens-based visualization. It inherits from the [Base Panel Configuration](../base.md).

| YAML Key | Data Type                                  | Description                                                                                                | Kibana Default                  | Required |
| -------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type`   | `Literal['charts']`                        | Specifies the panel type as a Lens panel.                                                                  | `charts`                        | Yes      |
| `id`     | `string`                                   | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID                    | No       |
| `title`  | `string`                                   | The title displayed on the panel header. Inherited from BasePanel.                                         | `""` (empty string)             | No       |
| `hide_title` | `boolean`                              | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`                         | No       |
| `description`| `string`                               | A brief description of the panel. Inherited from BasePanel.                                                | `""` (empty string, if `None`)  | No       |
| `grid`   | `Grid` object                              | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                             | Yes      |
| `query`  | `LegacyQueryTypes` object (KQL or Lucene)  | A panel-specific query to filter data for this Lens visualization. See [Queries Documentation](../../queries/config.md). | `None` (uses dashboard query)   | No       |
| `filters`| `list of FilterTypes`                      | A list of panel-specific filters. See [Filters Documentation](../../filters/config.md).                    | `[]` (empty list)               | No       |
| `chart`  | `LensChartTypes` object                    | Defines the actual Lens visualization configuration. This will be one of [Lens Metric Chart](#lens-metric-chart) or [Lens Pie Chart](#lens-pie-chart). | N/A                             | Yes      |
| `layers` | `list of MultiLayerChartTypes`             | For multi-layer charts (e.g., multiple pie charts on one panel). *Currently, only `LensPieChart` is supported as a multi-layer type.* | `None`                          | No       |

**Note on `layers` vs `chart`**:

* Use the `chart` field for single-layer visualizations (most common use case, e.g., one metric display, one pie chart).
* Use the `layers` field if you need to define multiple, distinct visualizations within the same Lens panel (e.g., overlaying different chart types or configurations). If `layers` is used, the `chart` field should not be.

---

## Lens Metric Chart (`chart.type: metric`)

Displays a single primary metric, optionally with a secondary metric, a maximum value, and a breakdown dimension.

| YAML Key    | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`      | `Literal['metric']`                        | Specifies the chart type as a Lens Metric visualization.                                                   | `metric`         | Yes      |
| `id`        | `string`                                   | An optional unique identifier for this specific chart layer.                                               | Generated ID     | No       |
| `primary`   | `LensMetricTypes` object                   | The primary metric to display. This is the main value shown. See [Lens Metrics](#lens-metrics).            | N/A              | Yes      |
| `secondary` | `LensMetricTypes` object                   | An optional secondary metric to display alongside the primary. See [Lens Metrics](#lens-metrics).          | `None`           | No       |
| `maximum`   | `LensMetricTypes` object                   | An optional maximum metric, often used for context (e.g., showing a value out of a total). See [Lens Metrics](#lens-metrics). | `None`           | No       |
| `breakdown` | `LensDimensionTypes` object                | An optional dimension to break down the metric by (e.g., showing primary metric per country). See [Lens Dimensions](#lens-dimensions). | `None`           | No       |

**Example (Lens Metric Chart):**

```yaml
# Within a LensPanel's 'chart' field:
# type: metric
# primary:
#   aggregation: "sum"
#   field: "bytes_transferred"
#   label: "Total Data"
#   format: { type: "bytes" }
# secondary:
#   aggregation: "average"
#   field: "response_time_ms"
#   label: "Avg Response"
#   format: { type: "duration", suffix: " ms" }
# breakdown:
#   type: values
#   field: "host.name"
#   size: 3
#   label: "Top Hosts"
```

---

## Lens Pie Chart (`chart.type: pie`)

Visualizes proportions of categories using slices of a pie or a donut chart.

| YAML Key          | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`            | `Literal['pie']`                           | Specifies the chart type as a Lens Pie visualization.                                                      | `pie`            | Yes      |
| `id`              | `string`                                   | An optional unique identifier for this specific chart layer.                                               | Generated ID     | No       |
| `data_view`       | `string`                                   | The ID or title of the data view (index pattern) for this pie chart.                                       | N/A              | Yes      |
| `metric`          | `LensMetricTypes` object                   | The metric that determines the size of each slice. See [Lens Metrics](#lens-metrics).                     | N/A              | Yes      |
| `slice_by`        | `list of LensDimensionTypes` objects       | One or more dimensions that determine how the pie is sliced. See [Lens Dimensions](#lens-dimensions).        | N/A              | Yes      |
| `appearance`      | `PieChartAppearance` object                | Formatting options for the chart appearance. See [Pie Chart Appearance](#pie-chart-appearance).            | `None`           | No       |
| `titles_and_text` | `PieTitlesAndText` object                  | Formatting options for slice labels and values. See [Pie Titles and Text](#pie-titles-and-text).           | `None`           | No       |
| `legend`          | `PieLegend` object                         | Formatting options for the chart legend. See [Pie Legend](#pie-legend).                                    | `None`           | No       |
| `color`           | `ColorMapping` object                      | Formatting options for the chart color palette. See [Color Mapping](#color-mapping).                       | `None`           | No       |

**Example (Lens Pie Chart):**

```yaml
# Within a LensPanel's 'chart' field:
# type: pie
# data_view: "ecommerce-orders"
# metric:
#   aggregation: "sum"
#   field: "order_value"
#   label: "Total Order Value"
# slice_by:
#   - type: values
#     field: "product.category"
#     size: 5
#     label: "Product Category"
# appearance:
#   donut: "medium"
# legend:
#   visible: "show"
#   width: "large"
# titles_and_text:
#   slice_labels: "inside"
#   slice_values: "percent"
```

---

## Lens Dimensions (`breakdown` for Metric, `slice_by` for Pie)

Dimensions define how data is grouped or bucketed in Lens visualizations.

### Common Dimension Fields (`BaseLensDimension`)

All specific dimension types below can include:

| YAML Key | Data Type | Description                                                                                                | Kibana Default   | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id`     | `string`  | An optional unique identifier for the dimension.                                                           | Generated ID     | No       |
| `label`  | `string`  | A custom display label for the dimension. If not provided, a label is inferred.                            | Inferred         | No       |

### Top Values Dimension (`type: values`)

Groups data by the most frequent unique values of a field.

| YAML Key           | Data Type         | Description                                                                                                | Kibana Default   | Required |
| ------------------ | ----------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`             | `Literal['values']`| Specifies the dimension type.                                                                              | `values`         | Yes      |
| `field`            | `string`          | The field to get top values from.                                                                          | N/A              | Yes      |
| `size`             | `integer`         | The number of top values to display.                                                                       | `3`              | No       |
| `sort`             | `Sort` object     | How to sort the terms. `by` can be a metric label or `_term` (alphabetical). `direction` is `asc` or `desc`. | Sort by metric, `desc` | No       |
| `other_bucket`     | `boolean`         | If `true`, groups remaining values into an "Other" bucket.                                                 | `true`           | No       |
| `missing_bucket`   | `boolean`         | If `true`, creates a bucket for documents where the field is missing.                                      | `false`          | No       |
| `include`          | `list of strings` | A list of specific terms to include.                                                                       | `None`           | No       |
| `exclude`          | `list of strings` | A list of specific terms to exclude.                                                                       | `None`           | No       |
| `include_is_regex` | `boolean`         | If `true`, treats `include` values as regex patterns.                                                      | `false`          | No       |
| `exclude_is_regex` | `boolean`         | If `true`, treats `exclude` values as regex patterns.                                                      | `false`          | No       |

### Date Histogram Dimension (`type: date_histogram`)

Groups data into time-based buckets (e.g., per hour, day).

| YAML Key            | Data Type                       | Description                                                                                                | Kibana Default   | Required |
| ------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`              | `Literal['date_histogram']`     | Specifies the dimension type.                                                                              | `date_histogram` | Yes      |
| `field`             | `string`                        | The date field to use for the histogram.                                                                   | N/A              | Yes      |
| `minimum_interval`  | `string`                        | The time interval (e.g., `auto`, `1h`, `1d`, `1w`).                                                        | `auto`           | No       |
| `partial_intervals` | `boolean`                       | If `true`, includes buckets for time periods that are only partially covered by the data.                  | `true`           | No       |
| `collapse`          | `CollapseAggregationEnum`       | For stacked charts, how to aggregate values within the same time bucket if multiple series exist. (`sum`, `min`, `max`, `avg`) | `None`           | No       |

### Filters Dimension (`type: filters`)

Creates buckets based on a list of custom KQL/Lucene queries.

| YAML Key  | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| --------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`    | `Literal['filters']`                       | Specifies the dimension type.                                                                              | `filters`        | Yes      |
| `filters` | `list of LensFiltersDimensionFilter` objects | A list of filter definitions. Each filter object has `query` (KQL/Lucene) and an optional `label`.         | N/A              | Yes      |

**`LensFiltersDimensionFilter` Object:**

| YAML Key | Data Type                 | Description                                      | Kibana Default   | Required |
| -------- | ------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `query`  | `LegacyQueryTypes` object | The KQL or Lucene query for this filter bucket.  | N/A              | Yes      |
| `label`  | `string`                  | A display label for this filter bucket.          | Query string     | No       |

### Intervals Dimension (`type: intervals`)

Groups data into numeric ranges (buckets).

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`        | `Literal['intervals']`                     | Specifies the dimension type.                                                                              | `intervals`      | Yes      |
| `field`       | `string`                                   | The numeric field to create intervals from.                                                                | N/A              | Yes      |
| `intervals`   | `list of LensIntervalsDimensionInterval` objects | A list of custom interval ranges. If not provided, `granularity` is used.                                | `None`           | No       |
| `granularity` | `integer` (1-7)                            | Divides the field into evenly spaced intervals. 1 is coarsest, 7 is finest.                                | `4`              | No       |
| `collapse`    | `CollapseAggregationEnum`                  | For stacked charts, how to aggregate values within the same interval if multiple series exist. (`sum`, `min`, `max`, `avg`) | `None`           | No       |
| `empty_bucket`| `boolean`                                  | If `true`, shows a bucket for documents with missing values for the field.                                 | `false`          | No       |

**`LensIntervalsDimensionInterval` Object:**

| YAML Key | Data Type | Description                                      | Kibana Default   | Required |
| -------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `from`   | `integer` | The start of the interval (inclusive).           | `None`           | No       |
| `to`     | `integer` | The end of the interval (exclusive).             | `None`           | No       |
| `label`  | `string`  | A display label for this interval bucket.        | Auto-generated   | No       |

---

## Lens Metrics (`primary`, `secondary`, `maximum` for Metric; `metric` for Pie)

Metrics define the calculations performed on your data (e.g., count, sum, average).

### Common Metric Fields (`BaseLensMetric`)

All specific metric types below can include:

| YAML Key | Data Type                 | Description                                                                                                | Kibana Default   | Required |
| -------- | ------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `id`     | `string`                  | An optional unique identifier for the metric.                                                              | Generated ID     | No       |
| `label`  | `string`                  | A custom display label for the metric. If not provided, a label is inferred.                               | Inferred         | No       |
| `format` | `LensMetricFormatTypes` object | How to format the metric's value (e.g., number, bytes, percent). See [Metric Formatting](#metric-formatting). | Default for type | No       |
| `filter` | `LegacyQueryTypes` object | A KQL or Lucene query to filter data *before* this metric is calculated.                                   | `None`           | No       |

### Aggregated Metric Types

These metrics perform an aggregation on a field.

**Count / Unique Count (`aggregation: count` or `aggregation: unique_count`)**

| YAML Key        | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| --------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation`   | `Literal['count', 'unique_count']`         | Type of count.                                                                                             | N/A              | Yes      |
| `field`         | `string`                                   | For `unique_count`, the field whose unique values are counted. For `count`, optional (counts all documents if `None`). | `None` for `count` | No (Yes for `unique_count`) |
| `exclude_zeros` | `boolean`                                  | If `true`, zero values are excluded from the aggregation.                                                  | `true`           | No       |

**Sum (`aggregation: sum`)**

| YAML Key        | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| --------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation`   | `Literal['sum']`                           | Specifies sum aggregation.                                                                                 | `sum`            | Yes      |
| `field`         | `string`                                   | The numeric field to sum.                                                                                  | N/A              | Yes      |
| `exclude_zeros` | `boolean`                                  | If `true`, zero values are excluded from the sum.                                                          | `true`           | No       |

**Min, Max, Average, Median (`aggregation: min` / `max` / `average` / `median`)**

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['min', 'max', 'average', 'median']` | The aggregation type.                                                                                      | N/A              | Yes      |
| `field`       | `string`                                   | The numeric field for the aggregation.                                                                     | N/A              | Yes      |

**Last Value (`aggregation: last_value`)**

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['last_value']`                    | Retrieves the most recent value of a field.                                                                | `last_value`     | Yes      |
| `field`       | `string`                                   | The field whose last value is retrieved.                                                                   | N/A              | Yes      |
| `date_field`  | `string`                                   | The date field used to determine the "last" value.                                                         | `@timestamp`     | No       |

**Percentile (`aggregation: percentile`)**

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['percentile']`                    | Calculates the value at a specific percentile.                                                             | `percentile`     | Yes      |
| `field`       | `string`                                   | The numeric field for percentile calculation.                                                              | N/A              | Yes      |
| `percentile`  | `integer`                                  | The percentile to calculate (e.g., `95` for 95th percentile).                                              | N/A              | Yes      |

**Percentile Rank (`aggregation: percentile_rank`)**

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `aggregation` | `Literal['percentile_rank']`               | Determines the rank of a specific value within the dataset.                                                | `percentile_rank`| Yes      |
| `field`       | `string`                                   | The numeric field for percentile rank calculation.                                                         | N/A              | Yes      |
| `rank`        | `integer`                                  | The value for which to find the percentile rank.                                                           | N/A              | Yes      |

### Formula Metric

Allows custom calculations using a formula string. *Note: Formula structure is complex and detailed parsing/compilation for its internal operations is not fully covered here but is handled by the compiler.*

| YAML Key  | Data Type | Description                                      | Kibana Default   | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `formula` | `string`  | The formula string (e.g., `count() / unique_count(user.id)`).  | N/A              | Yes      |

---

## Metric Formatting (`format` field within a metric)

Defines how metric values are displayed.

### Standard Format (`format.type: number` / `bytes` / `bits` / `percent` / `duration`)

| YAML Key  | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| --------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type`    | `Literal['number', 'bytes', 'bits', 'percent', 'duration']` | The general type of formatting.                                                                          | N/A              | Yes      |
| `suffix`  | `string`                                   | A suffix to append to the value (e.g., "ms", " GB").                                                       | `None`           | No       |
| `compact` | `boolean`                                  | If `true`, uses compact notation (e.g., "1K" instead of "1000").                                           | `None` (false)   | No       |
| `pattern` | `string`                                   | A Numeral.js format pattern (used if `type` is `number` or `percent`).                                     | Default for type | No       |

**Default Decimal Places (Kibana):**

* `number`: 2
* `bytes`: 2
* `bits`: 0
* `percent`: 2
* `duration`: 0 (Kibana often uses smart duration formatting like "1m 30s")

### Custom Format (`format.type: custom`)

| YAML Key  | Data Type             | Description                                      | Kibana Default   | Required |
| --------- | --------------------- | ------------------------------------------------ | ---------------- | -------- |
| `type`    | `Literal['custom']`   | Specifies custom formatting.                     | `custom`         | Yes      |
| `pattern` | `string`              | A Numeral.js format pattern.                     | N/A              | Yes      |

---

## Pie Chart Specific Formatting

These objects are used within the `LensPieChart` configuration.

### Pie Chart Appearance (`appearance` field)

| YAML Key | Data Type                             | Description                                      | Kibana Default   | Required |
| -------- | ------------------------------------- | ------------------------------------------------ | ---------------- | -------- |
| `donut`  | `Literal['small', 'medium', 'large']` | If set, creates a donut chart with the specified hole size. | `None` (pie)     | No       |

### Pie Titles and Text (`titles_and_text` field)

| YAML Key               | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `slice_labels`         | `Literal['hide', 'inside', 'auto']`        | How to display labels for each slice.                                                                      | `auto`           | No       |
| `slice_values`         | `Literal['hide', 'integer', 'percent']`    | How to display the value for each slice.                                                                   | `percent`        | No       |
| `value_decimal_places` | `integer` (0-10)                           | Number of decimal places for slice values.                                                                 | `2`              | No       |

### Pie Legend (`legend` field)

| YAML Key            | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `visible`           | `Literal['show', 'hide', 'auto']`          | Controls legend visibility.                                                                                | `auto`           | No       |
| `width`             | `Literal['small', 'medium', 'large', 'extra_large']` | Width of the legend area.                                                                                  | `medium`         | No       |
| `truncate_labels`   | `integer` (0-5)                            | Max number of lines for legend labels before truncating. `0` disables truncation.                          | `1`              | No       |

### Color Mapping (`color` field)

| YAML Key  | Data Type | Description                                      | Kibana Default   | Required |
| --------- | --------- | ------------------------------------------------ | ---------------- | -------- |
| `palette` | `string`  | The ID of the color palette to use (e.g., `default`, `elasticColors`). | `default`        | Yes      |

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* [Queries Configuration](../../queries/config.md)
* [Filters Configuration](../../filters/config.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/lens/metrics/metric.md -->\n\n# Metric Objects

Metric objects are used within chart panels (Lens and ESQL) to define the values being visualized, typically corresponding to the y-axis or the size of elements.

## Base Metric Fields

All metric types inherit from a base metric with the following optional field:

* `id` (optional, string): A unique identifier for the metric. If not provided, one may be generated during compilation.

## Lens Metric Types

Lens charts use the following metric types:

### Base Lens Metric Fields

All Lens metric types inherit from a base Lens metric with the following optional fields:

* `label` (optional, string): The display label for the metric. If not provided, a label may be inferred from the type and field.
* `format` (optional, object): The format of the metric. See [Lens Metric Format](#lens-metric-format) for details.
* `filter` (optional, object): A query (KQL or Lucene) applied before determining the metric value. See [Queries Documentation](../queries/config.md) for details.

### Lens Formula Metric

Represents a formula metric configuration within a Lens chart. Formula metrics allow for custom calculations based on other fields or metrics.

```yaml
- type: formula       # (Required) Must be 'formula'.
  formula: string     # (Required) The formula string to be evaluated.
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `type` (required, string): Must be `formula`.
  * `formula` (required, string): The formula string to be evaluated for this metric.
* **Example:**

    ```yaml
    - type: formula
      label: Error Rate
      formula: "count(kql='event.outcome:failure') / count() * 100"
    ```

### Lens Aggregated Metric Types

These metric types represent various standard aggregations.

#### Lens Count Aggregated Metric

Represents a count metric configuration within a Lens chart. Count metrics are used to count the number of documents or unique values in a data view.

```yaml
- aggregation: string # (Required) Aggregation type ('count' or 'unique_count').
  field: string       # (Optional for 'count', Required for 'unique_count') The field to count.
  exclude_zeros: boolean # (Optional) Whether to exclude zero values. Defaults to true.
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `aggregation` (required, string): The aggregation type. Must be `count` or `unique_count`.
  * `field` (optional, string): The field to count. Required for `unique_count`. If not provided for `count`, it will count all documents.
  * `exclude_zeros` (optional, boolean): Whether to exclude zero values from the count. Kibana defaults to true if not specified.
* **Example (Count):**

    ```yaml
    - aggregation: count
      label: Total Documents
    ```

* **Example (Unique Count):**

    ```yaml
    - aggregation: unique_count
      field: user.id
      label: Unique Users
    ```

#### Lens Sum Aggregated Metric

Represents a sum metric configuration within a Lens chart. Sum metrics are used to sum the values of a field.

```yaml
- aggregation: sum    # (Required) Must be 'sum'.
  field: string       # (Required) The field to sum.
  exclude_zeros: boolean # (Optional) Whether to exclude zero values. Defaults to true.
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `aggregation` (required, string): Must be `sum`.
  * `field` (required, string): The field to sum.
  * `exclude_zeros` (optional, boolean): Whether to exclude zero values from the count. Kibana defaults to true if not specified.
* **Example:**

    ```yaml
    - aggregation: sum
      field: bytes
      label: Total Bytes
    ```

#### Lens Other Aggregated Metric

Represents various aggregated metric configurations within a Lens chart, including min, max, median, and average.

```yaml
- aggregation: string # (Required) Aggregation type ('min', 'max', 'median', 'average').
  field: string       # (Required) The field to aggregate on.
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `aggregation` (required, string): The aggregation type. Must be `min`, `max`, `median`, or `average`.
  * `field` (required, string): The field to aggregate on.
* **Example (Average):**

    ```yaml
    - aggregation: average
      field: response_time
      label: Average Response Time
    ```

#### Lens Last Value Aggregated Metric

Represents a last value metric configuration within a Lens chart. Last value metrics retrieve the most recent value of a field based on a specified sort order.

```yaml
- aggregation: last_value # (Required) Must be 'last_value'.
  field: string       # (Required) The field whose last value is retrieved.
  date_field: string  # (Optional) The field used to determine the 'last' value (e.g., @timestamp).
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `aggregation` (required, string): Must be `last_value`.
  * `field` (required, string): The field whose last value is retrieved.
  * `date_field` (optional, string): The field used to determine the 'last' value. If not provided, the default time field for the data view is used.
* **Example:**

    ```yaml
    - aggregation: last_value
      field: system.load.5
      label: Last 5-minute Load Average
      date_field: "@timestamp"
    ```

#### Lens Percentile Rank Aggregated Metric

Represents a percentile rank metric configuration within a Lens chart. Percentile rank metrics determine the rank of a value in a data set.

```yaml
- aggregation: percentile_rank # (Required) Must be 'percentile_rank'.
  field: string       # (Required) The field to calculate the percentile rank on.
  rank: integer       # (Required) The rank to determine the percentile for.
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `aggregation` (required, string): Must be `percentile_rank`.
  * `field` (required, string): The field to calculate the percentile rank on.
  * `rank` (required, integer): The rank to determine the percentile for.
* **Example:**

    ```yaml
    - aggregation: percentile_rank
      field: response_time
      rank: 95
      label: 95th Percentile Rank Response Time
    ```

#### Lens Percentile Aggregated Metric

Represents a percentile metric configuration within a Lens chart. Percentile metrics determine the value at a specific percentile in a data set.

```yaml
- aggregation: percentile # (Required) Must be 'percentile'.
  field: string       # (Required) The field to calculate the percentile on.
  percentile: integer # (Required) The percentile to determine the value for.
  # Base Lens Metric fields also apply
```

* **Fields:**
  * `aggregation` (required, string): Must be `percentile`.
  * `field` (required, string): The field to calculate the percentile on.
  * `percentile` (required, integer): The percentile to determine the value for.
* **Example:**

    ```yaml
    - aggregation: percentile
      field: response_time
      percentile: 99
      label: 99th Percentile Response Time
    ```

### Lens Metric Format

Configures the display format of a Lens metric.

```yaml
format:
  type: string        # (Required) The format type (number, bytes, bits, percent, duration, custom).
  suffix: string      # (Optional) Suffix to display after the number.
  compact: boolean    # (Optional) Whether to display in a compact format.
  pattern: string     # (Optional for type: custom, Required for other types) The pattern to display the number in.
```

* **Fields:**
  * `type` (required, string): The format type. Valid values are `number`, `bytes`, `bits`, `percent`, `duration`, or `custom`.
  * `suffix` (optional, string): The suffix to display after the number.
  * `compact` (optional, boolean): Whether to display the number in a compact format (e.g., 1k instead of 1000).
  * `pattern` (optional, string): The pattern to display the number in. Required for `custom` type.

#### Lens Custom Metric Format

Allows for defining a custom format pattern for a Lens metric.

```yaml
format:
  type: custom        # (Required) Must be 'custom'.
  pattern: string     # (Required) The custom pattern to display the number in.
```

* **Fields:**
  * `type` (required, string): Must be `custom`.
  * `pattern` (required, string): The custom pattern to display the number in.

## ESQL Metric Type

ESQL charts use a single metric type defined by the ESQL query.

### ESQL Metric

A metric that is defined in the ESQL query.

```yaml
- field: string       # (Required) The field in the data view that this metric is based on.
  # Base Metric fields also apply
```

* **Fields:**
  * `field` (required, string): The field in the data view that this metric is based on. This field should correspond to a column returned by the ESQL query.
* **Example:**

    ```yaml
    - field: total_requests
      label: Total Requests from ESQL

\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/metric/config.md -->\n\n# Metric Chart Panel Configuration

The Metric chart panel displays a single value or a small set of key metrics, often used for KPIs or summary statistics.

## Minimal Configuration Example

```yaml
dashboard:
  name: "KPI Dashboard"
  panels:
    - type: metric
      title: "Total Revenue"
      grid: { x: 0, y: 0, w: 3, h: 2 }
      data:
        index: "sales-data"
        value: "revenue"
```

## Full Configuration Options

| YAML Key      | Data Type         | Description                                      | Required |
|--------------|-------------------|--------------------------------------------------|----------|
| `type`       | `Literal['metric']`| Specifies the panel type.                        | Yes      |
| `title`      | `string`          | Title of the panel.                              | No       |
| `grid`       | `Grid` object     | Position and size of the panel.                  | Yes      |
| `data`       | `object`          | Data source and field mapping.                   | Yes      |
| `value`      | `string`          | Field for the metric value.                      | Yes      |
| `color`      | `string`          | Color for the metric display.                    | No       |
| `description`| `string`          | Panel description.                               | No       |

## Related

* [Base Panel Configuration](../../base.md)
* [Dashboard Configuration](../../../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/charts/pie/config.md -->\n\n# Pie Chart Panel Configuration

The Pie chart panel visualizes data as a pie or donut chart, useful for showing proportions of a whole.

## Minimal Configuration Example

```yaml
dashboard:
  name: "Traffic Sources"
  panels:
    - type: pie
      title: "Website Traffic Sources"
      grid: { x: 0, y: 0, w: 6, h: 6 }
      data:
        index: "traffic-data"
        category: "source"
        value: "visits"
```

## Full Configuration Options

| YAML Key      | Data Type         | Description                                      | Required |
|--------------|-------------------|--------------------------------------------------|----------|
| `type`       | `Literal['pie']`  | Specifies the panel type.                        | Yes      |
| `title`      | `string`          | Title of the panel.                              | No       |
| `grid`       | `Grid` object     | Position and size of the panel.                  | Yes      |
| `data`       | `object`          | Data source and field mapping.                   | Yes      |
| `category`   | `string`          | Field for pie slices (categories).               | Yes      |
| `value`      | `string`          | Field for values (size of slices).               | Yes      |
| `donut`      | `boolean`         | Display as donut chart.                          | No       |
| `color`      | `string/list`     | Color(s) for slices.                             | No       |
| `legend`     | `object`          | Legend display options.                          | No       |
| `description`| `string`          | Panel description.                               | No       |

## Related

* [Base Panel Configuration](../../base.md)
* [Dashboard Configuration](../../../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/images/image.md -->\n\n# Image Panel Configuration

The `image` panel type is used to display an image directly on your dashboard. This can be useful for branding, diagrams, or other visual elements.

## Minimal Configuration Example

To add an Image panel, you need to specify its `type`, `grid` position, and the `from_url` for the image source.

```yaml
# Within a dashboard's 'panels' list:
# - type: image
#   title: "Company Logo"
#   grid:
#     x: 0
#     y: 0
#     w: 4  # Width of 4 grid units
#     h: 3  # Height of 3 grid units
#   from_url: "https://example.com/path/to/your/logo.png"

# For a complete dashboard structure:
dashboard:
  name: "Branded Dashboard"
  panels:
    - type: image
      title: "Company Logo"
      grid:
        x: 0
        y: 0
        w: 4
        h: 3
      from_url: "https://example.com/path/to/your/logo.png"
```

## Complex Configuration Example

This example demonstrates an Image panel with specific `fit` behavior, alternative text for accessibility, and a background color.

```yaml
dashboard:
  name: "Dashboard with Informative Image"
  panels:
    - type: image
      title: "System Architecture Diagram"
      grid:
        x: 0
        y: 0
        w: 12 # Full width
        h: 6
      from_url: "https://example.com/path/to/architecture.svg"
      fit: "contain"  # Ensure the whole image is visible within the panel
      description: "Overview of the system components and their interactions." # Alt text
      background_color: "#f0f0f0" # Light grey background
```

## Full Configuration Options

Image panels inherit from the [Base Panel Configuration](../base.md) and have the following specific fields:

| YAML Key           | Data Type                                   | Description                                                                                                | Kibana Default                  | Required |
| ------------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type`             | `Literal['image']`                          | Specifies the panel type.                                                                                | `image`                         | Yes      |
| `id`               | `string`                                    | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID                    | No       |
| `title`            | `string`                                    | The title displayed on the panel header. Inherited from BasePanel.                                         | `""` (empty string)             | No       |
| `hide_title`       | `boolean`                                   | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`                         | No       |
| `description`      | `string`                                    | Alternative text for the image, used for accessibility. This overrides the BasePanel `description` if you want specific alt text for the image itself. | `""` (empty string, if `None`)  | No       |
| `grid`             | `Grid` object                               | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                             | Yes      |
| `from_url`         | `string`                                    | The URL of the image to be displayed in the panel.                                                         | N/A                             | Yes      |
| `fit`              | `Literal['contain', 'cover', 'fill', 'none']` | The sizing of the image within the panel boundaries.                                                       | `contain`                       | No       |
| `background_color` | `string`                                    | Background color for the image panel (e.g., hex code like `#FFFFFF` or color name like `transparent`).   | `""` (empty string, likely transparent in Kibana) | No       |

**Details for `fit` options:**

* `contain`: (Default) Scales the image to fit within the panel while maintaining its aspect ratio. The entire image will be visible.
* `cover`: Scales the image to fill the panel while maintaining its aspect ratio. Some parts of the image may be cropped to achieve this.
* `fill`: Stretches or compresses the image to fill the panel completely, potentially altering its original aspect ratio.
* `none`: Displays the image at its original size. If the image is larger than the panel, it will be cropped. If smaller, it will sit within the panel, respecting its original dimensions.

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/links/links.md -->\n\n# Links Panel Configuration

The `links` panel type is used to display a collection of hyperlinks on your dashboard. These links can point to other Kibana dashboards or external web URLs. This panel is useful for creating navigation hubs or providing quick access to related resources.

## Minimal Configuration Examples

**Linking to another Dashboard:**

```yaml
# Within a dashboard's 'panels' list:
# - type: links
#   title: "Navigate to User Details"
#   grid: { x: 0, y: 0, w: 6, h: 2 }
#   links:
#     - label: "View User Activity Dashboard"
#       dashboard: "user-activity-dashboard-id" # ID of the target dashboard

# For a complete dashboard structure:
dashboard:
  name: "Main Overview"
  panels:
    - type: links
      title: "Navigate to User Details"
      grid: { x: 0, y: 0, w: 6, h: 2 }
      links:
        - label: "View User Activity Dashboard"
          dashboard: "user-activity-dashboard-id"
```

**Linking to an External URL:**

```yaml
# Within a dashboard's 'panels' list:
# - type: links
#   title: "External Resources"
#   grid: { x: 6, y: 0, w: 6, h: 2 }
#   links:
#     - label: "Project Documentation"
#       url: "https://docs.example.com/project-alpha"

# For a complete dashboard structure:
dashboard:
  name: "Main Overview"
  panels:
    - type: links
      title: "External Resources"
      grid: { x: 6, y: 0, w: 6, h: 2 }
      links:
        - label: "Project Documentation"
          url: "https://docs.example.com/project-alpha"
          new_tab: true # Open this external link in a new tab
```

## Complex Configuration Example

This example demonstrates a Links panel with multiple link types, a vertical layout, and specific options for how links behave.

```yaml
dashboard:
  name: "Operations Hub"
  panels:
    - type: links
      title: "Quick Access"
      description: "Links to key operational dashboards and tools."
      grid: { x: 0, y: 0, w: 12, h: 3 }
      layout: "vertical" # Display links one above the other
      links:
        - label: "Service Health Dashboard"
          dashboard: "service-health-monitor-v2"
          with_time: true      # Carry over current time range
          with_filters: true   # Carry over current filters
          new_tab: false       # Open in the same tab
        - label: "System Logs (Last 1 Hour)"
          dashboard: "system-logs-deep-dive"
          # This link will use the target dashboard's default time/filters
        - label: "Runbook Wiki"
          url: "https://internal.wiki/ops/runbooks"
          new_tab: true
          encode: false # If the URL should not be encoded
        - label: "Grafana Metrics"
          url: "https://grafana.example.com/d/abcdef/service-metrics"
          new_tab: true
```

## Full Configuration Options

### Links Panel

Defines the main container for a list of links. It inherits from the [Base Panel Configuration](../base.md).

| YAML Key    | Data Type                               | Description                                                                                                | Kibana Default      | Required |
| ----------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| `type`      | `Literal['links']`                      | Specifies the panel type.                                                                                | `links`             | Yes      |
| `id`        | `string`                                | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID        | No       |
| `title`     | `string`                                | The title displayed on the panel header. Inherited from BasePanel.                                         | `""` (empty string) | No       |
| `hide_title`| `boolean`                               | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`             | No       |
| `description`| `string`                               | A brief description of the panel. Inherited from BasePanel.                                                | `""` (empty string, if `None`) | No       |
| `grid`      | `Grid` object                           | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                 | Yes      |
| `layout`    | `Literal['horizontal', 'vertical']`     | The layout of the links in the panel.                                                                      | `horizontal`        | No       |
| `links`     | `list of LinkTypes`                     | A list of link objects to be displayed. Each object can be a [Dashboard Link](#dashboard-link) or a [URL Link](#url-link). | `[]` (empty list)   | Yes      |

### Link Types

Each item in the `links` list will be one of the following types. They share common base fields.

#### Base Link Fields (Common to DashboardLink and UrlLink)

| YAML Key | Data Type | Description                                                                                                | Kibana Default      | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| `id`     | `string`  | An optional unique identifier for the individual link item. Not typically needed.                          | Generated ID        | No       |
| `label`  | `string`  | The text displayed for the link. If not provided for a URL link, Kibana may show the URL itself. For dashboard links, a label is recommended. | `None` (or URL for URL links) | No       |

#### Dashboard Link

Represents a link to another Kibana dashboard.

| YAML Key       | Data Type | Description                                                                                                | Kibana Default | Required |
| -------------- | --------- | ---------------------------------------------------------------------------------------------------------- | -------------- | -------- |
| `dashboard`    | `string`  | The ID of the target Kibana dashboard.                                                                     | N/A            | Yes      |
| `id`           | `string`  | An optional unique identifier for this link item.                                                          | Generated ID   | No       |
| `label`        | `string`  | The display text for the link.                                                                             | `None`         | No       |
| `new_tab`      | `boolean` | If `true`, the linked dashboard will open in a new browser tab.                                            | `false`        | No       |
| `with_time`    | `boolean` | If `true`, the linked dashboard will inherit the current time range from the source dashboard.             | `true`         | No       |
| `with_filters` | `boolean` | If `true`, the linked dashboard will inherit the current filters from the source dashboard.                | `true`         | No       |

#### URL Link

Represents a link to an external web URL.

| YAML Key  | Data Type | Description                                                                                                | Kibana Default | Required |
| --------- | --------- | ---------------------------------------------------------------------------------------------------------- | -------------- | -------- |
| `url`     | `string`  | The full web URL that the link points to (e.g., `https://www.example.com`).                                | N/A            | Yes      |
| `id`      | `string`  | An optional unique identifier for this link item.                                                          | Generated ID   | No       |
| `label`   | `string`  | The display text for the link. If not set, Kibana defaults to showing the URL.                             | `""` (empty string) or URL | No       |
| `encode`  | `boolean` | If `true`, the URL will be URL-encoded before navigation.                                                  | `true`         | No       |
| `new_tab` | `boolean` | If `true`, the link will open in a new browser tab.                                                        | `false`        | No       |

## Methods (for programmatic generation)

The `LinksPanel` Pydantic model includes an `add_link(link: LinkTypes)` method, which can be used if you are generating dashboard configurations programmatically in Python (not directly used in YAML).

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/markdown/markdown.md -->\n\n# Markdown Panel Configuration

The `markdown` panel type is used to display rich text content, formatted using Markdown syntax, directly on your dashboard. This is equivalent to the "Text" visualization in Kibana.

## Minimal Configuration Example

To add a simple Markdown panel, you need to specify its `type`, `grid` position, and the `content`.

```yaml
# Within a dashboard's 'panels' list:
# - type: markdown
#   title: "Welcome Note"
#   grid:
#     x: 0
#     y: 0
#     w: 12 # Full width
#     h: 3  # Height of 3 grid units
#   content: "## Welcome to the Dashboard!\nThis panel provides an overview."

# For a complete dashboard structure:
dashboard:
  name: "Dashboard with Markdown"
  panels:
    - type: markdown
      title: "Welcome Note"
      grid:
        x: 0
        y: 0
        w: 12
        h: 3
      content: |
        ## Welcome to the Dashboard!
        This panel provides an overview of the key metrics and reports available.

        - Item 1
        - Item 2
```

## Complex Configuration Example

This example demonstrates a Markdown panel with a custom font size and a setting for how links are opened.

```yaml
dashboard:
  name: "Informational Dashboard"
  panels:
    - type: markdown
      title: "Important Instructions & Links"
      description: "Follow these steps for system setup."
      grid:
        x: 0
        y: 0
        w: 8
        h: 5
      content: |
        # Setup Guide

        Please follow the [official documentation](https://example.com/docs) for detailed setup instructions.

        Key steps include:
        1.  **Download** the installer.
        2.  **Configure** the `config.yaml` file.
        3.  **Run** the start script.

        For issues, refer to the [Troubleshooting Page](https://example.com/troubleshooting).
      font_size: 14
      links_in_new_tab: false # Links will open in the same tab
```

## Full Configuration Options

Markdown panels inherit from the [Base Panel Configuration](../base.md) and have the following specific fields:

| YAML Key           | Data Type        | Description                                                                                                | Kibana Default                               | Required |
| ------------------ | ---------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------- | -------- |
| `type`             | `Literal['markdown']` | Specifies the panel type.                                                                                | `markdown`                                   | Yes      |
| `id`               | `string`         | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID                                 | No       |
| `title`            | `string`         | The title displayed on the panel header. Inherited from BasePanel.                                         | `""` (empty string)                          | No       |
| `hide_title`       | `boolean`        | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`                                      | No       |
| `description`      | `string`         | A brief description of the panel. Inherited from BasePanel.                                                | `""` (empty string, if `None`)               | No       |
| `grid`             | `Grid` object    | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                                          | Yes      |
| `content`          | `string`         | The Markdown content to be displayed in the panel. You can use YAML multi-line string syntax (e.g., `|` or `>`) for readability. | N/A                                          | Yes      |
| `font_size`        | `integer`        | The font size for the Markdown content, in pixels.                                                         | `12`                                         | No       |
| `links_in_new_tab` | `boolean`        | If `true`, links in the Markdown content will open in a new tab.                                           | `true`                                       | No       |

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../../dashboard/dashboard.md)
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/panels/search/search.md -->\n\n# Search Panel Configuration

The `search` panel type is used to embed the results of a pre-existing, saved Kibana search directly onto your dashboard. This allows you to display dynamic log views, event lists, or any other data set defined by a saved search in Discover.

## Minimal Configuration Example

To add a Search panel, you need to specify its `type`, `grid` position, and the `saved_search_id`.

```yaml
# Within a dashboard's 'panels' list:
# - type: search
#   title: "All System Logs"
#   grid:
#     x: 0
#     y: 0
#     w: 12 # Full width
#     h: 10 # Height of 10 grid units
#   saved_search_id: "your-saved-search-id" # Replace with the actual ID

# For a complete dashboard structure:
dashboard:
  name: "Log Monitoring Dashboard"
  panels:
    - type: search
      title: "All System Logs"
      grid:
        x: 0
        y: 0
        w: 12
        h: 10
      saved_search_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef" # Example ID
```

## Complex Configuration Example (Illustrative)

Search panels primarily rely on the configuration of the saved search itself (columns, sort order, query within the saved search). The panel configuration in the dashboard YAML is straightforward. This example shows it with a description and a hidden title.

```yaml
dashboard:
  name: "Security Incidents Overview"
  panels:
    - type: search
      # Title is defined in the saved search, so we hide the panel's own title
      hide_title: true
      description: "Displays critical security alerts from the last 24 hours, as defined in the 'Critical Alerts' saved search."
      grid:
        x: 0
        y: 0
        w: 12
        h: 8
      saved_search_id: "critical-security-alerts-saved-search"
```

## Full Configuration Options

Search panels inherit from the [Base Panel Configuration](../base.md) and have one specific required field:

| YAML Key          | Data Type        | Description                                                                                                | Kibana Default                  | Required |
| ----------------- | ---------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type`            | `Literal['search']`| Specifies the panel type.                                                                                | `search`                        | Yes      |
| `id`              | `string`         | A unique identifier for the panel. Inherited from BasePanel.                                               | Generated ID                    | No       |
| `title`           | `string`         | The title displayed on the panel header. This can override the title of the saved search if desired. Inherited from BasePanel. | `""` (empty string)             | No       |
| `hide_title`      | `boolean`        | If `true`, the panel title will be hidden. Inherited from BasePanel.                                       | `false`                         | No       |
| `description`     | `string`         | A brief description of the panel. Inherited from BasePanel.                                                | `""` (empty string, if `None`)  | No       |
| `grid`            | `Grid` object    | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](../base.md#grid-object-configuration). | N/A                             | Yes      |
| `saved_search_id` | `string`         | The ID of the saved Kibana search object (from Discover app) to display in the panel.                      | N/A                             | Yes      |

**Note on Behavior:** The appearance, columns displayed, sort order, and underlying query of the Search panel are primarily controlled by the configuration of the saved search itself within Kibana's Discover application. The dashboard panel configuration mainly serves to embed that saved search.

## Related Documentation

* [Base Panel Configuration](../base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* Kibana Discover and Saved Searches documentation (external to this project).
\n\n\n---\n\n<!-- Source: src/dashboard_compiler/queries/config.md -->\n\n# Queries Configuration

Queries are used to define the search criteria for retrieving data. They can be applied globally at the dashboard level or specifically to individual panels that support them. This compiler supports KQL (Kibana Query Language), Lucene, and ESQL (Elasticsearch Query Language).

## Minimal Configuration Examples

**KQL Query:**

```yaml
# Applied at the dashboard level
dashboard:
  # ...
  query:
    kql: 'response_code:200 AND "user.id": "test-user"'
```

**Lucene Query:**

```yaml
# Applied at the dashboard level
dashboard:
  # ...
  query:
    lucene: 'event.module:nginx AND event.dataset:nginx.access'
```

**ESQL Query (typically for specific panel types like ESQL-backed charts):**

```yaml
# Example within a panel configuration that supports ESQL
panels:
  - type: some_esql_panel # Hypothetical panel type
    # ... other panel config
    query: |
      FROM my_index
      | STATS RARE(clientip)
```

## Full Configuration Options

Queries are typically defined under a `query` key, either at the root of the `dashboard` object or within a specific panel's configuration. The structure of the `query` object determines the language.

### KQL Query

Filters documents using the Kibana Query Language (KQL). This is often the default query language in Kibana.

| YAML Key | Data Type | Description                                      | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------ | -------------- | -------- |
| `kql`    | `string`  | The KQL query string to apply.                   | N/A            | Yes      |
| `query`  | `object`  | The parent object containing the `kql` key.      | N/A            | Yes      |

**Usage Example (Dashboard Level):**

```yaml
dashboard:
  # ...
  query:
    kql: 'event.action:"user_login" AND event.outcome:success'
```

### Lucene Query

Filters documents using the more expressive, but complex, Lucene query syntax.

| YAML Key | Data Type | Description                                      | Kibana Default | Required |
| -------- | --------- | ------------------------------------------------ | -------------- | -------- |
| `lucene` | `string`  | The Lucene query string to apply.                | N/A            | Yes      |
| `query`  | `object`  | The parent object containing the `lucene` key.   | N/A            | Yes      |

**Usage Example (Dashboard Level):**

```yaml
dashboard:
  # ...
  query:
    lucene: '(geo.src:"US" OR geo.src:"CA") AND tags:"production"'
```

### ESQL Query

Uses Elasticsearch Query Language (ESQL) for data retrieval and aggregation. ESQL queries are typically used by specific panel types that are designed to work with ESQL's tabular results (e.g., ESQL-driven charts or tables). The configuration is a direct string under the `query` key for such panels.

| YAML Key | Data Type | Description                                                                 | Kibana Default | Required |
| -------- | --------- | --------------------------------------------------------------------------- | -------------- | -------- |
| `query`  | `string`  | The ESQL query string. The Pydantic model uses `root` for this direct string. | N/A            | Yes      |

**Usage Example (Panel Level - for a hypothetical ESQL panel):**

```yaml
panels:
  - type: esql_backed_chart # This panel type would be designed to use ESQL
    title: "Top User Agents by Count"
    query: |
      FROM "web-logs-*"
      | STATS count = COUNT(user_agent.name) BY user_agent.name
      | SORT count DESC
      | LIMIT 10
    # ... other panel-specific configurations
```

## Query Scope

* **Dashboard Level Query**: Defined under `dashboard.query`. This query is applied globally to all panels that do not explicitly override it or ignore global queries. KQL and Lucene are supported at this level.
* **Panel Level Query**: Defined under `panel.query` (for panels that support it, e.g., Lens panels, ESQL panels). This query is specific to the panel and is often combined with (or can override) the dashboard-level query, depending on the panel's behavior.
  * Lens panels typically use KQL for their panel-specific query.
  * ESQL-specific panels will use an ESQL query string.

## Related Documentation

* [Dashboard Configuration](../dashboard/dashboard.md)
* [Filters Configuration](../filters/config.md)
* [Panel Documentation (e.g., Lens, ESQL specific panels)](../panels/base.md)
