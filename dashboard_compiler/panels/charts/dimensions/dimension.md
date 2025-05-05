# Dimension Objects

Dimension objects are used within chart panels (Lens and ESQL) to define how data is grouped or categorized, often corresponding to an axis or a breakdown.

## Base Dimension Fields

All dimension types inherit from a base dimension with the following optional field:

*   `id` (optional, string): A unique identifier for the dimension. If not provided, one may be generated during compilation.

## Lens Dimension Types

Lens charts use the following dimension types:

### Base Lens Dimension Fields

All Lens dimension types inherit from a base Lens dimension with the following optional fields:

*   `label` (optional, string): The display label for the dimension. If not provided, a label may be inferred from the field and type.

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

*   **Fields:**
    *   `type` (required, string): Must be `values`.
    *   `field` (required, string): The name of the field in the data view that this dimension is based on.
    *   `size` (optional, integer): The number of top terms to display.
    *   `sort` (optional, object): Defines how the terms are sorted. See [Sort Object](../shared/config.md#sort-object).
    *   `other_bucket` (optional, boolean): If `true`, a bucket for all other terms not included in the top `size` will be shown. Defaults to `false`.
    *   `missing_bucket` (optional, boolean): If `true`, a bucket for documents with a missing value for the field will be shown. Defaults to `false`.
    *   `include` (optional, list of strings): A list of term values or regex patterns to include.
    *   `exclude` (optional, list of strings): A list of term values or regex patterns to exclude.
    *   `include_is_regex` (optional, boolean): If `true`, the values in the `include` list will be treated as regular expressions. Defaults to `false`.
    *   `exclude_is_regex` (optional, boolean): If `true`, the values in the `exclude` list will be treated as regular expressions. Defaults to `false`.
*   **Example:**
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

*   **Fields:**
    *   `type` (required, string): Must be `date_histogram`.
    *   `field` (required, string): The name of the field in the data view that this dimension is based on.
    *   `minimum_interval` (optional, string): The minimum time interval for the histogram buckets. Defaults to `auto` if not specified.
    *   `partial_intervals` (optional, boolean): If `true`, show partial intervals. Kibana defaults to `true` if not specified.
    *   `collapse` (optional, string): The aggregation to use for the dimension when intervals are collapsed. See [Collapse Aggregation Enum](#collapse-aggregation-enum).
*   **Example:**
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

*   **Fields:**
    *   `type` (required, string): Must be `filters`.
    *   `filters` (required, list of objects): A list of filter objects. Each object should have a `query` (see [Queries Documentation](../queries/config.md)) and an optional `label` (string).
*   **Example:**
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

*   **Fields:**
    *   `type` (required, string): Must be `intervals`.
    *   `field` (required, string): The name of the field in the data view that this dimension is based on.
    *   `intervals` (optional, list of objects): A list of interval objects. Each object should have optional `from` (integer) and `to` (integer) values and an optional `label` (string). If not provided, intervals will be automatically picked.
    *   `granularity` (optional, integer): Interval granularity divides the field into evenly spaced intervals based on the minimum and maximum values for the field. Kibana defaults to 4 if not specified. Value should be between 1 and 7.
    *   `collapse` (optional, string): The aggregation to use for the dimension when intervals are collapsed. See [Collapse Aggregation Enum](#collapse-aggregation-enum).
    *   `empty_bucket` (optional, boolean): If `true`, show a bucket for documents with a missing value for the field. Defaults to `false`.
*   **Example:**
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

*   **Fields:**
    *   `field` (required, string): The field in the data view that this dimension is based on. This field should correspond to a column returned by the ESQL query.
*   **Example:**
    ```yaml
    - field: country
      label: Country from ESQL
    ```

## Collapse Aggregation Enum

This enum defines the possible aggregation types to use when collapsing intervals in Lens Date Histogram and Intervals dimensions.

*   `SUM`
*   `MIN`
*   `MAX`
*   `AVG`

## Related Structures

*   [Sort Object](../shared/config.md#sort-object)
*   [Queries Documentation](../queries/config.md)