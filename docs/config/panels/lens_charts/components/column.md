# Column Object

The `column` object is used within Lens Table charts to define the data displayed in each column. Columns can represent dimensions or metrics.

```yaml
- field: string     # (Required for dimension/metric columns) Field name. Use '___records___' for count.
  id: string        # (Optional) Unique identifier for the column.
  type: string      # (Required) Aggregation type (e.g., terms, count, last_value, max, average).
  label: string     # (Optional) Display label for the column.
  size: integer     # (Optional, for terms) Number of terms to show.
  sort: object      # (Optional, for terms) Sort configuration.
  sort_field: string # (Optional, for last_value) Field to determine the "last" value.
  filter: string  # (Optional, for last_value) KQL filter applied before taking the last value.
```

## Fields

*   `field` (required, string): The name of the field to use for the column. Required for dimension and metric columns. Use `___records___` for a count of documents.
*   `id` (optional, string): A unique identifier for the column.
*   `type` (required, string): The aggregation type to apply to the field for this column. Common types include `terms`, `count`, `last_value`, `max`, and `average`.
*   `label` (optional, string): A display label for the column header. If not provided, a label based on the field and aggregation type will be used.
*   `size` (optional, integer): Used with the `terms` aggregation type to specify the number of top terms to display in this column.
*   `sort` (optional, object): Defines how the terms are sorted when using the `terms` aggregation in this column. See [Sort Object](#sort-object).
*   `sort_field` (optional, string): Used with the `last_value` aggregation type to specify the field used to determine the "last" document for this column (e.g., `@timestamp`).
*   `filter` (optional, string): Used with the `last_value` aggregation type to apply a KQL filter before determining the last value for this column.

## Example (Terms Column)

```yaml
columns:
  - field: user.city
    type: terms
    label: City
    size: 10
    sort:
      by: "_count"
      direction: desc
```

## Example (Metric Column - Count)

```yaml
columns:
  - type: count
    label: Number of Users
```

## Example (Metric Column - Last Value)

```yaml
columns:
  - field: system.uptime
    type: last_value
    label: Last Reported Uptime
    sort_field: "@timestamp"
```

## Related Structures

*   [Sort Object](#sort-object)