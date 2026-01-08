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
        multiple: true
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

::: dashboard_compiler.controls.config.ControlSettings
    options:
      show_root_heading: false
      heading_level: 4

### Options List Control

Allows users to select one or more values from a list to filter data.

::: dashboard_compiler.controls.config.OptionsListControl
    options:
      show_root_heading: false
      heading_level: 4

#### Match Technique Options

::: dashboard_compiler.controls.config.MatchTechnique
    options:
      show_root_heading: false
      heading_level: 5

### Range Slider Control

Allows users to select a range of numeric values to filter data.

::: dashboard_compiler.controls.config.RangeSliderControl
    options:
      show_root_heading: false
      heading_level: 4

### Time Slider Control

Allows users to select a sub-section of the dashboard's current time range. This control does not use a `data_view` or `field` as it operates on the global time context.

::: dashboard_compiler.controls.config.TimeSliderControl
    options:
      show_root_heading: false
      heading_level: 4

**Note on Time Slider Offsets:** The YAML configuration expects `start_offset` and `end_offset` as float values between 0.0 (0%) and 1.0 (100%). Kibana internally represents these as percentages from 0.0 to 100.0. If not provided, Kibana defaults to `0.0` for start and `100.0` for end.

### ES|QL Controls

ES|QL controls allow users to filter ES|QL visualizations via variables. There are two main types:

1. **ES|QL Field/Function Controls** - For field/function selection (FIELDS, FUNCTIONS variable types)
2. **ES|QL Value Controls** - For value selection (VALUES, MULTI_VALUES, TIME_LITERAL variable types)

#### ES|QL Field Control

For field selection in ES|QL visualizations. Only supports static values via `choices`.

::: dashboard_compiler.controls.config.ESQLFieldControl
    options:
      show_root_heading: false
      heading_level: 5

#### ES|QL Function Control

For function selection in ES|QL visualizations. Only supports static values via `choices`.

::: dashboard_compiler.controls.config.ESQLFunctionControl
    options:
      show_root_heading: false
      heading_level: 5

#### Field/Function Control Examples

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

- **Value variables** (VALUES, MULTI_VALUES, TIME_LITERAL) use single `?` prefix: `?variable_name`
- **Field/function variables** (FIELDS, FUNCTIONS) use double `??` prefix: `??variable_name`

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

#### ES|QL Static Single-Select Control (DEPRECATED)

::: dashboard_compiler.controls.config.ESQLStaticSingleSelectControl
    options:
      show_root_heading: false
      heading_level: 5

#### Static Values Example

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

#### ES|QL Static Multi-Select Control (DEPRECATED)

::: dashboard_compiler.controls.config.ESQLStaticMultiSelectControl
    options:
      show_root_heading: false
      heading_level: 5

#### ES|QL Query-Driven Control (DEPRECATED)

::: dashboard_compiler.controls.config.ESQLQueryControl
    options:
      show_root_heading: false
      heading_level: 5

#### Query-Driven Example

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

## ES|QL Variable Types

::: dashboard_compiler.controls.types.ESQLVariableType
    options:
      show_root_heading: false
      heading_level: 3

## Related Documentation

- [Dashboard Configuration](./../dashboard/dashboard.md)
