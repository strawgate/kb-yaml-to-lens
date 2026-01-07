# Datatable Chart Panel Configuration

The Datatable chart panel displays tabular data with customizable columns, sorting, pagination, and formatting options. Perfect for displaying detailed records and performing quick data analysis.

## A Poem for the Spreadsheet Scholars

_For those who know that sometimes you just need to see the rows:_

```text
When charts and graphs just won't suffice,
And visual flair must pay the price,
The datatable stands, precise and plain—
Row after row, your data's domain.

Sort ascending, descending too,
Filter down to just a few.
Columns wide or columns tight,
Pages of data that just feel right.

Metrics summed at bottom's end,
Summary rows, your data's friend.
From service names to error codes,
Each cell tells a tale until it folds.

Left-align text and right-align numbers,
No visual tricks, no chart encumbers.
Just pure data, clean and true—
A dream come true for someone like you.

So here's to rows and columns straight,
To tables that enumerate:
Sometimes the simplest view prevails,
When details matter, datatable never fails!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Service Status Dashboard"
    panels:
      - lens:
          type: datatable
          data_view: "metrics-*"
          metrics:
            - id: "service-count"
              field: "service.name"
              aggregation: count
          rows:
            - id: "service-breakdown"
              type: values
              field: "service.name"
        title: "Service Health Table"
        grid: { x: 0, y: 0, w: 12, h: 6 }
```

## Full Configuration Options

### Lens Datatable Chart

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------------------- | ---------------------------------------------------- | -------- | -------- |
| `type` | `Literal['datatable']` | Specifies the chart type. | N/A | Yes |
| `data_view` | `string` | The data view (index pattern) to query. | N/A | Yes |
| `metrics` | `list[LensMetricTypes]` | List of metrics to display as columns. | `[]` | No |
| `rows` | `list[LensDimensionTypes]` | List of dimensions to use as row groupings. | `[]` | No |
| `rows_by` | `list[LensDimensionTypes]` | Optional "split metrics by" dimensions (creates separate metric columns). | `None` | No |
| `columns` | `list[DatatableColumnConfig]` | Optional column configurations for row columns. See [Row Column Configuration](#row-column-configuration-datatablecolumnconfig) below. | `None` | No |
| `metric_columns` | `list[DatatableMetricColumnConfig]` | Optional column configurations for metric columns. See [Metric Column Configuration](#metric-column-configuration-datatablemetriccolumnconfig) below. | `None` | No |
| `appearance` | `DatatableAppearance \| None` | Optional appearance settings (row height, density). See [Appearance Configuration](#appearance-configuration-datatableappearance) below. | `None` | No |
| `sorting` | `DatatableSortingConfig \| None` | Optional sorting configuration. See [Sorting Configuration](#sorting-configuration-datatablesortingconfig) below. | `None` | No |
| `paging` | `DatatablePagingConfig \| None` | Optional pagination configuration. See [Pagination Configuration](#pagination-configuration-datatablepagingconfig) below. | `None` | No |

### Row Column Configuration (`DatatableColumnConfig`)

Customize row columns (non-metric columns) with these options:

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------------------------------------------- | ------------------------------------------------ | -------- | -------- |
| `column_id` | `string` | The ID of the column (must match a row dimension ID). | N/A | Yes |
| `width` | `int` | Column width in pixels. | `None` | No |
| `hidden` | `bool` | Whether to hide this column. | `False` | No |
| `alignment` | `left` \| `right` \| `center` | Text alignment for the column. | `None` | No |
| `color_mode` | `none` \| `cell` \| `text` | How to apply colors to the column. | `None` | No |

### Metric Column Configuration (`DatatableMetricColumnConfig`)

Customize metric columns with these options (includes all base options plus summary row fields):

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------------------------------------------- | ------------------------------------------------ | -------- | -------- |
| `column_id` | `string` | The ID of the column (must match a metric ID). | N/A | Yes |
| `width` | `int` | Column width in pixels. | `None` | No |
| `hidden` | `bool` | Whether to hide this column. | `False` | No |
| `alignment` | `left` \| `right` \| `center` | Text alignment for the column. | `None` | No |
| `color_mode` | `none` \| `cell` \| `text` | How to apply colors to the column. | `None` | No |
| `summary_row` | `none` \| `sum` \| `avg` \| `count` \| `min` \| `max` | Summary function (only for metrics). | `None` | No |
| `summary_label` | `string` | Custom label for the summary row. | `None` | No |

### Appearance Configuration (`DatatableAppearance`)

Control the visual appearance and density of the datatable:

| YAML Key | Data Type | Description | Default | Required |
| ----------- | ---------------------------------------------------- | ------------------------------------------------ | -------- | -------- |
| `row_height` | `'auto' \| 'single' \| 'custom'` | Row height mode: `auto` (fit content), `single` (single line), `custom` (specify lines). | `auto` | No |
| `row_height_lines` | `int` | Number of lines for custom row height. Only applies when `row_height` is `custom`. | `None` | No |
| `header_row_height` | `'auto' \| 'single' \| 'custom'` | Header row height mode. Same options as `row_height`. | `auto` | No |
| `header_row_height_lines` | `int` | Number of lines for custom header row height. Only applies when `header_row_height` is `custom`. | `None` | No |
| `density` | `'compact' \| 'normal' \| 'expanded'` | Grid density: `compact` (tight spacing), `normal` (balanced), `expanded` (more whitespace). | `normal` | No |

**Example:**

```yaml
appearance:
  row_height: single        # Show one line per row
  density: compact          # Tight spacing for more data on screen
  header_row_height: auto   # Let headers expand to fit text
```

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
dashboards:
  - name: "Service Performance Dashboard"
    panels:
      - lens:
          type: datatable
          data_view: "apm-*"
          metrics:
            - id: "request-count"
              field: "transaction.name"
              aggregation: count
            - id: "avg-duration"
              field: "transaction.duration.us"
              aggregation: average
          rows:
            - id: "service-name"
              type: values
              field: "service.name"
              size: 50
          columns:
            - column_id: "service-name"
              width: 250
              alignment: left
          metric_columns:
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
          appearance:
            row_height: single
            density: compact
        title: "Top Services by Request Count"
        grid: { x: 0, y: 0, w: 12, h: 8 }
```

## ESQL Datatable Chart

The ESQL variant supports the same configuration options but uses ESQL metrics and dimensions instead of Lens metrics and dimensions:

```yaml
dashboards:
  - name: "ESQL Service Dashboard"
    panels:
      - esql:
          query: |
            FROM metrics-*
            | STATS count = COUNT(*), avg_cpu = AVG(system.cpu.total.norm.pct) BY service.name
          type: datatable
          metrics:
            - id: "count"
              field: "count"
            - id: "avg-cpu"
              field: "avg_cpu"
          rows:
            - id: "service"
              field: "service.name"
          sorting:
            column_id: "count"
            direction: desc
        title: "Service Statistics"
        grid: { x: 0, y: 0, w: 12, h: 6 }
```

## Tips and Best Practices

1. **Column Order**: Columns appear in the order: row dimensions first, then metrics. This matches Kibana's default behavior when creating datatables through the UI.

2. **Summary Rows**: Only use summary rows with metric columns (via `metric_columns`). They don't make sense for row dimension columns.

3. **Performance**: For large datasets, enable pagination and limit the number of row dimensions to improve performance.

4. **Readability**: Use column width and alignment to make data easier to scan. Right-align numeric values, left-align text.

5. **Sorting**: Set a default sort to help users immediately see the most important data (e.g., sort by count descending).

## Related Documentation

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
