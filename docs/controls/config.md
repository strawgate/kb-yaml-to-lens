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

### ES|QL Control

Allows users to filter ES|QL visualizations via variables. ES|QL controls can use either static values or query-driven values.

**The control type is automatically determined based on the fields you provide:**

- If you provide `choices` with a single default value (or `multiple: false`), it creates a static single-select control
- If you provide `choices` with a list default value (or `multiple: true`), it creates a static multi-select control
- If you provide `query`, it creates a query-driven control

#### ES|QL Static Single-Select Control

For single-selection controls with predefined values.

::: dashboard_compiler.controls.config.ESQLStaticSingleSelectControl
    options:
      show_root_heading: false
      heading_level: 5

#### ES|QL Static Multi-Select Control

For multi-selection controls with predefined values.

::: dashboard_compiler.controls.config.ESQLStaticMultiSelectControl
    options:
      show_root_heading: false
      heading_level: 5

#### ES|QL Query-Driven Control

For controls that dynamically fetch values from an ES|QL query.

::: dashboard_compiler.controls.config.ESQLQueryControl
    options:
      show_root_heading: false
      heading_level: 5

#### Static Values Example

```yaml
controls:
  # Single-select control with explicit multiple
  - type: esql
    variable_name: environment
    variable_type: values
    choices:
      - production
      - staging
      - development
    label: Environment
    multiple: false

  # Single-select control with string default (auto-infers multiple: false)
  - type: esql
    variable_name: status
    variable_type: values
    choices: ["200", "404", "500"]
    label: HTTP Status
    default: "200"

  # Multi-select control with list default (auto-infers multiple: true)
  - type: esql
    variable_name: regions
    variable_type: values
    choices: ["us-east", "us-west", "eu-west"]
    label: Regions
    default: ["us-east", "us-west"]
```

#### Query-Driven Example

```yaml
controls:
  - type: esql
    variable_name: status_code
    variable_type: values
    query: FROM logs-* | STATS count = COUNT(*) BY http.response.status_code | KEEP http.response.status_code | LIMIT 20
    label: HTTP Status Code
```

**Important**: ES|QL control queries **must return exactly one column** containing the values to display in the control. Use `KEEP` to select only the field column after aggregation.

**Using ES|QL Variables in Panels:**

ES|QL control variables can be referenced in ES|QL panel queries using the `?variable_name` syntax:

```yaml
panels:
  - title: Filtered Requests
    esql:
      type: metric
      query:
        - FROM logs-*
        - WHERE http.response.status_code == ?status_code
        - STATS total = COUNT(*)
```

## ES|QL Variable Types

::: dashboard_compiler.controls.types.ESQLVariableType
    options:
      show_root_heading: false
      heading_level: 3

## Related Documentation

- [Dashboard Configuration](./../dashboard/dashboard.md)
