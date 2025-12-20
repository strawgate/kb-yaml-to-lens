# Metric Objects

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
