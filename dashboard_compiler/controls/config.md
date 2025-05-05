# Controls

Controls can be added to the dashboard allowing users to interactively filter or modify the data displayed. They are defined as a list of control objects within the `controls` field of the `dashboard` object.

```yaml
dashboard:
  controls: list        # (Optional) A list of control panels for the dashboard. Can be empty.
    - # Control object (see Control Types below)
```

## Base Control Fields

All control types inherit from a base control with the following optional fields:

*   `id` (optional, string): A unique identifier for the control. If not provided, one may be generated.
*   `width` (optional, string): The width of the control in the dashboard layout. Valid values are `small`, `medium`, and `large`. If not set, defaults to `medium`.
*   `label` (optional, string): The display label for the control. If not provided, a label may be inferred.

## Control Settings

The `controls` field within the `dashboard`'s `settings` object allows for configuring global settings for controls.

```yaml
settings:
  controls:
    label_position: string # (Optional) The position of the control label (inline, above). Defaults to "inline".
    apply_global_filters: boolean # (Optional) Whether to apply global filters to the control. Defaults to true.
    apply_global_timerange: boolean # (Optional) Whether to apply the global time range to the control. Defaults to true.
    ignore_zero_results: boolean # (Optional) Whether to ignore controls that return zero results. Defaults to true.
    chain_controls: boolean # (Optional) Whether to chain controls together. Defaults to true.
    click_to_apply: boolean # (Optional) Whether to require clicking apply button. Defaults to false.
```

*   `label_position` (optional, string): The position of the control label, either `inline` or `above`. Defaults to `inline` if not set.
*   `apply_global_filters` (optional, boolean): Whether to apply global filters to the control. Defaults to `true` if not set.
*   `apply_global_timerange` (optional, boolean): Whether to apply the global time range to the control. Defaults to `true` if not set.
*   `ignore_zero_results` (optional, boolean): Whether to ignore controls that return zero results. Defaults to `true` if not set.
*   `chain_controls` (optional, boolean): Whether to chain controls together, allowing one control's selection to filter the next. Defaults to `true` if not set.
*   `click_to_apply` (optional, boolean): Whether to require users to click the apply button before applying changes. Defaults to `false` if not set.

## Control Types

The following control types are available:

### Options List Control

The `optionsList` control provides a dropdown or list of values from a specific field, allowing users to filter the dashboard data by selecting one or more options.

```yaml
- type: options       # (Required) Must be 'options'.
  data_view: string   # (Required) The ID or title of the data view.
  field: string       # (Required) The field name for the control.
  fill_width: boolean # (Optional) If true, the control fills available width. Defaults to false.
  match_technique: string # (Optional) The search technique for filtering options (prefix, contains, exact).
  wait_for_results: boolean # (Optional) If true, delay display until results load. Defaults to false.
  preselected: list   # (Optional) A list of preselected options. Defaults to empty list.
  singular: boolean   # (Optional) If true, allows only a single selection. Defaults to false.
  # Base Control fields also apply
```

*   **Fields:**
    *   `type` (required, string): Must be `options`.
    *   `data_view` (required, string): The ID or title of the data view (index pattern) the control operates on.
    *   `field` (required, string): The field in the data view that the control is associated with.
    *   `fill_width` (optional, boolean): If true, the control will automatically adjust its width to fill available space. Defaults to `false`.
    *   `match_technique` (optional, string): The search technique used for filtering options. See [Match Technique Enum](#match-technique-enum) for valid values.
    *   `wait_for_results` (optional, boolean): If set to true, delay the display of the list of values until the results are fully loaded. Defaults to `false`.
    *   `preselected` (optional, list of strings): A list of options that are preselected when the control is initialized. Defaults to an empty list.
    *   `singular` (optional, boolean): If true, the control allows only a single selection from the options list. Defaults to `false`.
*   **Example:**
    ```yaml
    - type: options
      label: Select Country
      data_view: users-*
      field: user.country.keyword
      singular: true
      preselected: ["USA"]
    ```

### Range Slider Control

The `rangeSlider` control provides a slider that allows users to filter data based on a numerical range of a specific field.

```yaml
- type: range         # (Required) Must be 'range'.
  data_view: string   # (Required) The ID or title of the data view.
  field: string       # (Required) The field name for the control.
  fill_width: boolean # (Optional) If true, the control fills available width. Defaults to false.
  step: number        # (Optional) Step value for the slider.
  # Base Control fields also apply
```

*   **Fields:**
    *   `type` (required, string): Must be `range`.
    *   `data_view` (required, string): The ID or title of the data view (index pattern) the control operates on.
    *   `field` (required, string): The field in the data view that the control will operate on.
    *   `fill_width` (optional, boolean): If true, the control will automatically adjust its width to fill available space. Defaults to `false`.
    *   `step` (optional, number): The step value for the slider, defining the granularity of selections.
*   **Example:**
    ```yaml
    - type: range
      label: Filter by Response Time (ms)
      data_view: logs-*
      field: response_time
      step: 10
    ```

### Time Slider Control

The `timeSlider` control allows users to select a time range based on a percentage of the total time range.

```yaml
- type: time          # (Required) Must be 'time'.
  start_offset: number # (Optional) The start offset for the time range as a %. Value between 0 and 1.
  end_offset: number  # (Optional) The end offset for the time range as a %. Value between 0 and 1.
  # Base Control fields also apply
```

*   **Fields:**
    *   `type` (required, string): Must be `time`.
    *   `start_offset` (optional, number): The start offset for the time range as a percentage (0 to 1).
    *   `end_offset` (optional, number): The end offset for the time range as a percentage (0 to 1).
*   **Example:**
    ```yaml
    - type: time
      label: Time Range
      start_offset: 0.25 # Start at 25% of the time range
      end_offset: 0.75   # End at 75% of the time range
    ```
*   **Note:** The `TimeSliderControl` has a validation to ensure `start_offset` is less than `end_offset` when both are provided.

## Match Technique Enum

This enum defines the possible search techniques used for filtering options in an Options List control.

*   `PREFIX`: Filters options starting with the input text.
*   `CONTAINS`: Filters options containing the input text.
*   `EXACT`: Filters options matching the input text exactly.

## Related Documentation

*   [Dashboard Object](../dashboard/dashboard.md)