# Metric Object

The `metric` object is used within Lens charts (specifically Bar, Area, Line, Pie, and Metric) to define the values being visualized, typically corresponding to the y-axis or the size of elements.

```yaml
- type: string    # (Required) Aggregation type (e.g., count, max, average, unique_count, formula, last_value).
  id: string      # (Optional) Unique identifier for the metric.
  label: string   # (Optional) Display label for the metric. Defaults to standard label (e.g., "Count").
  field: string   # (Optional, required for most types except count) Field name. Use '___records___' for count.
  formula: string # (Optional, for type: formula) The formula string.
  sort_field: string # (Optional, for last_value) Field to determine the "last" value.
  filter: string  # (Optional, for last_value) KQL filter applied before taking the last value.
```

## Fields

*   `type` (required, string): The aggregation type to apply to the field. Common types include `count`, `max`, `average`, `unique_count`, `sum`, `formula`, and `last_value`.
*   `id` (optional, string): A unique identifier for the metric.
*   `label` (optional, string): A display label for the metric. If not provided, a standard label based on the aggregation type will be used (e.g., "Count of ").
*   `field` (optional, string): The name of the field to use for the metric. This is required for most aggregation types except `count`, where you can use `___records___` or omit the field.
*   `formula` (optional, string): Required when `type` is `formula`. A string containing the Lens formula to calculate the metric.
*   `sort_field` (optional, string): Used with the `last_value` aggregation type to specify the field used to determine the "last" document (e.g., `@timestamp`).
*   `filter` (optional, string): Used with the `last_value` aggregation type to apply a KQL filter before determining the last value.

## Example (Count Aggregation)

```yaml
metrics:
  - type: count
    label: Total Documents
```

## Example (Average Aggregation)

```yaml
metrics:
  - type: average
    field: response_time
    label: Average Response Time
```

## Example (Formula Aggregation)

```yaml
metrics:
  - type: formula
    label: Error Rate
    formula: "count(kql='event.outcome:failure') / count() * 100"
```

## Example (Last Value Aggregation)

```yaml
metrics:
  - type: last_value
    field: system.load.5
    label: Last 5-minute Load Average
    sort_field: "@timestamp"
    filter: "system.load.5 > 0"