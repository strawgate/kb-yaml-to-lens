# Controls Configuration

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
