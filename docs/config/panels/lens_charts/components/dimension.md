# Dimension Object

The `dimension` object is used within Lens charts (specifically Bar, Area, Line, and Pie) to define how data is grouped or categorized, often corresponding to an axis or a breakdown.

```yaml
- field: string     # (Required) Field name.
  id: string        # (Optional) Unique identifier for the dimension.
  type: string      # (Required) Aggregation type (e.g., date_histogram, terms, histogram).
  label: string     # (Optional) Display label for the dimension. Defaults to field name.
  interval: string  # (Optional, for date_histogram or histogram) Time or number interval.
  size: integer     # (Optional, for terms) Number of terms to show.
  sort: object      # (Optional, for terms) Sort configuration.
  other_bucket: boolean # (Optional, for terms) Show 'Other' bucket.
  missing_bucket: boolean # (Optional, for terms) Show 'Missing' bucket.
  include: list     # (Optional, for terms) Include terms matching these values/regex.
  exclude: list     # (Optional, for terms) Exclude terms matching these values/regex.
  include_is_regex: boolean # (Optional, for terms) Treat include values as regex.
  exclude_is_regex: boolean # (Optional, for terms) Treat exclude values as regex.
```

## Fields

*   `field` (required, string): The name of the field to use for the dimension.
*   `id` (optional, string): A unique identifier for the dimension.
*   `type` (required, string): The aggregation type to apply to the field. Common types include `date_histogram` (for time-based data), `terms` (for categorical data), and `histogram` (for numerical ranges).
*   `label` (optional, string): A display label for the dimension. If not provided, the field name will be used.
*   `interval` (optional, string): Required for `date_histogram` and `histogram` aggregation types. Specifies the time interval (e.g., `auto`, `1h`, `1d`) or number interval for grouping.
*   `size` (optional, integer): Used with the `terms` aggregation type to specify the number of top terms to display.
*   `sort` (optional, object): Defines how the terms are sorted when using the `terms` aggregation. See [Sort Object](#sort-object).
*   `other_bucket` (optional, boolean): Used with the `terms` aggregation. If `true`, a bucket for all other terms not included in the top `size` will be shown.
*   `missing_bucket` (optional, boolean): Used with the `terms` aggregation. If `true`, a bucket for documents with a missing value for the field will be shown.
*   `include` (optional, list of strings): Used with the `terms` aggregation. A list of term values or regex patterns to include.
*   `exclude` (optional, list of strings): Used with the `terms` aggregation. A list of term values or regex patterns to exclude.
*   `include_is_regex` (optional, boolean): If `true`, the values in the `include` list will be treated as regular expressions.
*   `exclude_is_regex` (optional, boolean): If `true`, the values in the `exclude` list will be treated as regular expressions.

## Example (Terms Aggregation)

```yaml
dimensions:
  - field: user.country
    type: terms
    label: Users by Country
    size: 5
    sort:
      by: "_count" # Sort by document count
      direction: desc
    other_bucket: true
```

## Example (Date Histogram Aggregation)

```yaml
dimensions:
  - field: "@timestamp"
    type: date_histogram
    label: Events over Time
    interval: 1d
```

## Related Structures

*   [Sort Object](#sort-object)