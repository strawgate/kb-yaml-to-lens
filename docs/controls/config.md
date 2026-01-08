# Controls Configuration

Controls are interactive elements that can be added to a dashboard, allowing users to filter data or adjust visualization settings dynamically. They are defined as a list of control objects within each dashboard's `controls` field in the `dashboards:` array. Global behavior of controls can be managed via the `settings.controls` object.

## Minimal Configuration Examples

Here's a minimal example of an `options` list control:

```yaml
dashboards:
  - name: "Example Dashboard"
    controls:
      - type: options
        label: "Filter by OS Type"
        data_view: "metrics-*"
        field: "resource.attributes.os.type"
```

Here's a minimal example of a `range` slider control:

```yaml
dashboards:
  - name: "Example Dashboard"
    controls:
      - type: range
        label: "CPU Load Average (1m)"
        data_view: "metrics-*"
        field: "metrics.system.cpu.load_average.1m"
```

## Complex Configuration Example

This example demonstrates multiple controls with custom widths and global control settings:

```yaml
dashboards:
  - name: "Application Monitoring Dashboard"
    description: "Dashboard with interactive controls."
    settings:
      controls:
        label_position: "above"
        chain_controls: true
        click_to_apply: false
    controls:
      - type: options
        label: "Host Name"
        width: "medium"
        data_view: "metrics-*"
        field: "resource.attributes.host.name"
        singular: false
        match_technique: "contains"
      - type: range
        label: "CPU Utilization"
        width: "large"
        data_view: "metrics-*"
        field: "metrics.system.cpu.utilization"
        step: 0.01
      - type: time
        label: "Custom Time Slice"
        width: "small"
        start_offset: 0.1  # 10% from the start of the global time range
        end_offset: 0.9    # 90% from the start of the global time range
```

## Full Configuration Options

### Control Settings (`settings.controls`)

Global settings for all controls on the dashboard. These are configured under the `settings.controls` path in your main dashboard YAML.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------------ | ------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- | -------- |
| `label_position` | `Literal['inline', 'above']` | The position of the control label. | `inline` | No |
| `apply_global_filters` | `boolean` | Whether to apply global filters to the control. | `true` | No |
| `apply_global_timerange` | `boolean` | Whether to apply the global time range to the control. | `true` | No |
| `ignore_zero_results` | `boolean` | Whether to ignore controls that return zero results. If `true`, controls with no results will be hidden. | `false` (controls with zero results are shown) | No |
| `chain_controls` | `boolean` | Whether to chain controls together, allowing one control's selection to filter the options in the next. | `true` (hierarchical chaining) | No |
| `click_to_apply` | `boolean` | Whether to require users to click an apply button before applying changes. | `false` (changes apply immediately) | No |

### Options List Control

Allows users to select one or more values from a list to filter data.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['options']` | Specifies the control type. | `options` | Yes |
| `id` | `string` | A unique identifier for the control. If not provided, one will be generated. | Generated UUID | No |
| `width` | `Literal['small', 'medium', 'large']` | The width of the control in the dashboard layout. | `medium` | No |
| `label` | `string` | The display label for the control. If not provided, a label may be inferred. | `None` | No |
| `data_view` | `string` | The ID or title of the data view (index pattern) the control operates on. | N/A | Yes |
| `field` | `string` | The name of the field within the data view that the control is associated with. | N/A | Yes |
| `fill_width` | `boolean` | If true, the control will automatically adjust its width to fill available space. | `false` | No |
| `match_technique` | `Literal['prefix', 'contains', 'exact']` | The search technique used for filtering options. See [Match Technique Enum](#match-technique-enum-match_technique). | `prefix` | No |
| `wait_for_results` | `boolean` | If set to true, delay the display of the list of values until the results are fully loaded. | `false` | No |
| `preselected` | `list of strings` | A list of options that are preselected when the control is initialized. | `[]` (empty list) | No |
| `multiple` | `boolean` | If true, allow multiple selection from the options. Takes precedence over deprecated `singular` field. | `false` | No |
| `singular` | `boolean` | **DEPRECATED:** Use `multiple` instead. If true, only allow single selection. | `false` | No |

### Range Slider Control

Allows users to select a range of numeric values to filter data.

| YAML Key | Data Type | Description | Kibana Default | Required |
| ------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['range']` | Specifies the control type. | `range` | Yes |
| `id` | `string` | A unique identifier for the control. If not provided, one will be generated. | Generated UUID | No |
| `width` | `Literal['small', 'medium', 'large']` | The width of the control in the dashboard layout. | `medium` | No |
| `label` | `string` | The display label for the control. If not provided, a label may be inferred. | `None` | No |
| `data_view` | `string` | The ID or title of the data view (index pattern) the control operates on. | N/A | Yes |
| `field` | `string` | The name of the field within the data view that the control is associated with. | N/A | Yes |
| `fill_width` | `boolean` | If true, the control will automatically adjust its width to fill available space. | `false` | No |
| `step` | `integer` or `float` | The step value for the range, defining the granularity of selections. | `1` | No |

### Time Slider Control

Allows users to select a sub-section of the dashboard's current time range. This control does not use a `data_view` or `field` as it operates on the global time context.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `type` | `Literal['time']` | Specifies the control type. | `time` | Yes |
| `id` | `string` | A unique identifier for the control. If not provided, one will be generated. | Generated UUID | No |
| `width` | `Literal['small', 'medium', 'large']` | The width of the control in the dashboard layout. | `medium` | No |
| `label` | `string` | The display label for the control. If not provided, a label may be inferred. | `None` | No |
| `start_offset` | `float` (between 0.0 and 1.0) | The start offset for the time range as a percentage of the global time range (e.g., `0.25` for 25%). Must be less than `end_offset`. | `0.0` (0%) | No |
| `end_offset` | `float` (between 0.0 and 1.0) | The end offset for the time range as a percentage of the global time range (e.g., `0.75` for 75%). Must be greater than `start_offset`. | `1.0` (100%) | No |

**Note on Time Slider Offsets:** The YAML configuration expects `start_offset` and `end_offset` as float values between 0.0 (0%) and 1.0 (100%). Kibana internally represents these as percentages from 0.0 to 100.0. If not provided, Kibana defaults to `0.0` for start and `100.0` for end.

### ES|QL Controls

ES|QL controls allow users to filter ES|QL visualizations via variables. There are two main types:

1. **ES|QL Value Controls** - For value selection (VALUES, MULTI_VALUES, TIME_LITERAL variable types)
2. **ES|QL Field Controls** - For field/function selection (FIELDS, FUNCTIONS variable types)

#### ES|QL Value Control

Allows users to filter ES|QL visualizations via value variables. Supports both static values (via `choices`) and query-driven values (via `query`).

**Variable types supported:** `values` (default), `multi_values`, `time_literal`

##### Common Value Control Fields

| YAML Key | Data Type | Description | Kibana Default | Required |
| --- | --- | --- | --- | --- |
| `type` | `Literal['esql']` | Specifies the control type. | `esql` | Yes |
| `id` | `string` | A unique identifier for the control. If not provided, one will be generated. | Generated UUID | No |
| `width` | `Literal['small', 'medium', 'large']` | The width of the control in the dashboard layout. | `medium` | No |
| `label` | `string` | The display label for the control. | `None` | No |
| `variable_name` | `string` | The name of the ES\|QL variable (e.g., `status_code`). Used in queries as `?variable_name`. | N/A | Yes |
| `variable_type` | `Literal['values', 'multi_values', 'time_literal']` | The type of variable. See [ES\|QL Variable Types](#esql-variable-types-variable_type). | `values` | No |
| `choices` | `list of strings` | The static list of available values. Mutually exclusive with `query`. | N/A | Yes* |
| `query` | `string` | The ES\|QL query that returns available values. Mutually exclusive with `choices`. | N/A | Yes* |
| `default` | `string` or `list of strings` | Default selected value(s). Must be a string for single-select, list for multi-select. | `None` | No |
| `multiple` | `boolean` | If true, allow multiple selection. If not set, auto-inferred from `default` type or defaults to false for static mode. | Auto-inferred | No |

\* Either `choices` or `query` must be provided, but not both.

##### Static Mode Example

```yaml
controls:
  # Multi-select with explicit multiple property
  - type: esql
    variable_name: environment
    variable_type: values
    choices: ["production", "staging", "development"]
    label: Environment
    multiple: true
    default: ["production", "staging"]

  # Single-select with string default (auto-infers multiple: false)
  - type: esql
    variable_name: status
    variable_type: values
    choices: ["200", "404", "500"]
    label: HTTP Status
    default: "200"
```

##### Query Mode Example

```yaml
controls:
  # Query-driven single-select
  - type: esql
    variable_name: status_code
    variable_type: values
    query: FROM logs-* | STATS count BY http.response.status_code | KEEP http.response.status_code | LIMIT 20
    label: HTTP Status Code
    multiple: false

  # Query-driven multi-select
  - type: esql
    variable_name: host_names
    variable_type: values
    query: FROM logs-* | STATS count BY host.name | KEEP host.name
    label: Host Names
    multiple: true
```

**Important**: ES|QL control queries **must return exactly one column** containing the values to display in the control. Use `KEEP` to select only the field column after aggregation.

#### ES|QL Field Control

Allows users to select fields or functions for use in ES|QL visualizations. Only supports static values (via `choices`).

**Variable types supported:** `fields` (default), `functions`

##### Field Control Fields

| YAML Key | Data Type | Description | Kibana Default | Required |
| --- | --- | --- | --- | --- |
| `type` | `Literal['esql']` | Specifies the control type. | `esql` | Yes |
| `id` | `string` | A unique identifier for the control. If not provided, one will be generated. | Generated UUID | No |
| `width` | `Literal['small', 'medium', 'large']` | The width of the control in the dashboard layout. | `medium` | No |
| `label` | `string` | The display label for the control. | `None` | No |
| `variable_name` | `string` | The name of the ES\|QL variable (e.g., `selected_field`). Used in queries as `??variable_name`. | N/A | Yes |
| `variable_type` | `Literal['fields', 'functions']` | The type of variable. See [ES\|QL Variable Types](#esql-variable-types-variable_type). | `fields` | No |
| `choices` | `list of strings` | The static list of available fields or functions. **REQUIRED.** | N/A | Yes |
| `default` | `string` or `list of strings` | Default selected value(s). Must be a string for single-select, list for multi-select. | `None` | No |
| `multiple` | `boolean` | If true, allow multiple selection. If not set, auto-inferred from `default` type or defaults to false (single-select). | Auto-inferred | No |

##### Field Control Example

```yaml
controls:
  # Field selection control
  - type: esql
    variable_name: selected_field
    variable_type: fields
    choices: ["@timestamp", "host.name", "message", "log.level"]
    label: Select Field
    default: "@timestamp"

  # Function selection control
  - type: esql
    variable_name: aggregate_fn
    variable_type: functions
    choices: ["COUNT", "AVG", "SUM", "MAX", "MIN"]
    label: Aggregate Function
    default: "COUNT"
```

**Using ES|QL Variables in Panels:**

ES|QL control variables can be referenced in ES|QL panel queries:

- **Value variables** use single `?` prefix: `?variable_name`
- **Field/function variables** use double `??` prefix: `??variable_name`

```yaml
panels:
  # Using value variable
  - title: Filtered Requests
    esql:
      type: metric
      query:
        - FROM logs-*
        - WHERE http.response.status_code == ?status_code
        - STATS total = COUNT(*)

  # Using field variable
  - title: Dynamic Field Display
    esql:
      type: table
      query:
        - FROM logs-*
        - KEEP ??selected_field
        - LIMIT 100
```

## ES|QL Variable Types (`variable_type`)

This defines the type of variable used in ES|QL controls. These match Kibana's `ESQLVariableType` enum.

**Value Controls** (use single `?` prefix in queries):

- `values`: (Default) Standard values variable type for filtering by field values
- `multi_values`: Multi-value variable type for array-based filtering
- `time_literal`: Time literal variable type for time-based filtering

**Field Controls** (use double `??` prefix in queries):

- `fields`: Fields variable type for dynamic field selection
- `functions`: Functions variable type for dynamic function selection

**Note:** Field and function controls only support static values (via `choices`). Query-driven mode is only available for value controls.

## Match Technique Enum (`match_technique`)

This enum defines the possible search techniques used for filtering options in an `OptionsListControl`.

- `prefix`: (Default) Filters options starting with the input text.
- `contains`: Filters options containing the input text.
- `exact`: Filters options matching the input text exactly.

## Related Documentation

- [Dashboard Configuration](./../dashboard/dashboard.md)
