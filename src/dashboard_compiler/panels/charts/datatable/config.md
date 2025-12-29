# Datatable Chart Panel Configuration

The Datatable chart panel displays tabular data with customizable columns, sorting, pagination, and formatting options. Perfect for displaying detailed records and performing quick data analysis.

## A Poem for the Infrastructure Observability Team

_For @graphaelli and the team who keep the lights on:_

```text
In rows and columns, data flows,
Where metrics dance and insight grows.
From pods that crash at 3 AM,
To logs that tell us "Here I am!"

Your tables sort, they page, they shine,
With summary rows of COUNT and MIN.
While others sleep, your dashboards wake,
Detecting every small mistake.

So here's to datatable displays,
That light our darkest on-call days.
With alignment left and summaries right,
You make observability a delight!

Infrastructure never sleeps, they say,
But datatables help us find the way.
From namespace counts to error rates,
Your tabular views are truly great!
```

---

## Minimal Configuration Example

```yaml
dashboard:
  name: "Service Status Dashboard"
  panels:
    - type: charts
      title: "Service Health Table"
      grid: { x: 0, y: 0, w: 12, h: 6 }
      chart:
        type: datatable
        data_view: "metrics-*"
        metrics:
          - id: "service-count"
            field: "service.name"
            aggregation: count
        breakdowns:
          - id: "service-breakdown"
            type: values
            field: "service.name"
```

## Full Configuration Options

### Lens Datatable Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------------------- | ---------------------------------------------------- | -------- | -------- |
| `type` | `Literal['datatable']` | Specifies the chart type. | N/A | Yes |
| `data_view` | `string` | The data view (index pattern) to query. | N/A | Yes |
| `metrics` | `list[LensMetricTypes]` | List of metrics to display as columns. | `[]` | No |
| `breakdowns` | `list[LensDimensionTypes]` | List of dimensions to use as breakdown columns. | `[]` | No |
| `columns` | `list[DatatableColumnConfig]` | Optional column configurations for customization. | `None` | No |
| `row_height` | `DatatableRowHeightEnum` | Row height mode: `auto`, `single`, or `custom`. | `auto` | No |
| `row_height_lines` | `int` | Number of lines for custom row height. | `None` | No |
| `header_row_height` | `DatatableRowHeightEnum` | Header row height mode: `auto`, `single`, or `custom`. | `auto` | No |
| `header_row_height_lines` | `int` | Number of lines for custom header row height. | `None` | No |
| `density` | `DatatableDensityEnum` | Grid density: `compact`, `normal`, or `expanded`. | `normal` | No |
| `sorting` | `DatatableSortingConfig` | Optional sorting configuration. | `None` | No |
| `paging` | `DatatablePagingConfig` | Optional pagination configuration. | `None` | No |

### Column Configuration (`DatatableColumnConfig`)

Customize individual columns with these options:

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------------------------------------------- | ------------------------------------------------ | -------- | -------- |
| `column_id` | `string` | The ID of the column (must match a metric/dimension ID). | N/A | Yes |
| `width` | `int` | Column width in pixels. | `None` | No |
| `hidden` | `bool` | Whether to hide this column. | `False` | No |
| `alignment` | `left` \| `right` \| `center` | Text alignment for the column. | `None` | No |
| `color_mode` | `none` \| `cell` \| `text` | How to apply colors to the column. | `None` | No |
| `summary_row` | `none` \| `sum` \| `avg` \| `count` \| `min` \| `max` | Summary function (only for metrics). | `None` | No |
| `summary_label` | `string` | Custom label for the summary row. | `None` | No |

### Sorting Configuration (`DatatableSortingConfig`)

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------- | -------------------------------- | ------- | -------- |
| `column_id` | `string` | The ID of the column to sort by. | N/A | Yes |
| `direction` | `asc` \| `desc` | Sort direction. | `asc` | No |

### Pagination Configuration (`DatatablePagingConfig`)

| YAML Key | Data Type | Description | Default | Required |
| ----------- | --------- | -------------------------------- | ------- | -------- |
| `enabled` | `bool` | Whether pagination is enabled. | `True` | No |
| `page_size` | `int` | Number of rows per page. | `10` | No |

## Complex Configuration Example

This example demonstrates a datatable with custom column configurations, sorting, and pagination:

```yaml
dashboard:
  name: "Service Performance Dashboard"
  panels:
    - type: charts
      title: "Top Services by Request Count"
      grid: { x: 0, y: 0, w: 12, h: 8 }
      chart:
        type: datatable
        data_view: "apm-*"
        metrics:
          - id: "request-count"
            field: "transaction.name"
            aggregation: count
          - id: "avg-duration"
            field: "transaction.duration.us"
            aggregation: average
        breakdowns:
          - id: "service-name"
            type: values
            field: "service.name"
            size: 50
        columns:
          - column_id: "service-name"
            width: 250
            alignment: left
          - column_id: "request-count"
            width: 150
            alignment: right
            summary_row: sum
            summary_label: "Total Requests"
          - column_id: "avg-duration"
            width: 150
            alignment: right
            summary_row: avg
            summary_label: "Overall Avg"
        sorting:
          column_id: "request-count"
          direction: desc
        paging:
          enabled: true
          page_size: 25
        row_height: single
        density: compact
```

## ESQL Datatable Chart

The ESQL variant supports the same configuration options but uses ESQL metrics and dimensions instead of Lens metrics and dimensions:

```yaml
dashboard:
  name: "ESQL Service Dashboard"
  panels:
    - type: charts
      title: "Service Statistics"
      grid: { x: 0, y: 0, w: 12, h: 6 }
      esql:
        query: |
          FROM metrics-*
          | STATS count = COUNT(*), avg_cpu = AVG(system.cpu.total.norm.pct) BY service.name
      chart:
        type: datatable
        metrics:
          - id: "count"
            field: "count"
          - id: "avg-cpu"
            field: "avg_cpu"
        breakdowns:
          - id: "service"
            field: "service.name"
        sorting:
          column_id: "count"
          direction: desc
```

## Tips and Best Practices

1. **Column Order**: Columns appear in the order: metrics first, then breakdowns. Plan your metric and breakdown order accordingly.

2. **Summary Rows**: Only use summary rows with metric columns. They don't make sense for dimension columns.

3. **Performance**: For large datasets, enable pagination and limit the number of breakdowns to improve performance.

4. **Readability**: Use column width and alignment to make data easier to scan. Right-align numeric values, left-align text.

5. **Sorting**: Set a default sort to help users immediately see the most important data (e.g., sort by count descending).

## Related Documentation

- [Base Panel Configuration](../../base.md)
- [Lens Metrics](../lens/metrics/metric.md)
- [Lens Dimensions](../lens/dimensions/dimension.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md)
