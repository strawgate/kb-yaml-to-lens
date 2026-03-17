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

## Lens Datatable Charts

::: kb_dashboard_core.panels.charts.datatable.config.LensDatatableChart
    options:
      show_root_heading: false
      heading_level: 3

## Column Appearance

::: kb_dashboard_core.panels.charts.datatable.appearance.DatatableColumnAppearance
    options:
      show_root_heading: false
      heading_level: 3

## Metric Column Configuration

::: kb_dashboard_core.panels.charts.datatable.appearance.DatatableMetricAppearance
    options:
      show_root_heading: false
      heading_level: 3

## One-Click Filter

Set `appearance.one_click_filter: true` on a metric or dimension to enable Kibana's one-click filtering interaction for that column.

```yaml
dashboards:
  - name: "Datatable With One-Click Filter"
    panels:
      - title: "Top Services"
        size: {w: 24, h: 15}
        lens:
          type: datatable
          data_view: "logs-*"
          breakdowns:
            - id: "service"
              field: "service.name"
              type: values
              appearance:
                one_click_filter: true
          metrics:
            - id: "request-count"
              aggregation: count
              label: "Request Count"
```

## Column Colors

Datatable metric columns support range-based coloring to highlight values based on numeric thresholds. Configure `color.apply_to` and optional range settings under `color`.
Range palettes are emitted only when `color.thresholds` is configured; without `thresholds`, no range palette is generated even if other range fields are set.

### Color Configuration Fields

| Field | Description |
| ----- | ----------- |
| `color.apply_to` | How generated range colors are applied: `cell` (background color) or `text` (text color) |
| `color` | Optional range settings (`range_type`, `range_min`, `range_max`, `thresholds`) |

### Example: CPU Usage Thresholds

```yaml
dashboards:
  - name: "System Metrics"
    panels:
      - title: "CPU Usage by Host"
        size: {w: 24, h: 15}
        lens:
          type: datatable
          data_view: "metrics-*"
          breakdowns:
            - id: "host"
              field: "host.name"
              type: values
          metrics:
            - id: "cpu-avg"
              field: "system.cpu.total.pct"
              aggregation: average
              label: "CPU %"
              color:
                apply_to: cell
                range_type: percent
                range_min: 0
                range_max: 100
                thresholds:
                  - up_to: 50
                    color: '#00BF6F'  # Green for low usage
                  - up_to: 80
                    color: '#FFA500'  # Orange for moderate
                  - up_to: 100
                    color: '#BD271E'  # Red for high usage
```

For detailed `ColorRangeMapping` configuration options, see the [Color Assignments documentation](../guides/color-assignments.md).

## Datatable Appearance

::: kb_dashboard_core.panels.charts.datatable.config.DatatableAppearance
    options:
      show_root_heading: false
      heading_level: 3

## Sorting Configuration

::: kb_dashboard_core.panels.charts.datatable.config.DatatableSortingConfig
    options:
      show_root_heading: false
      heading_level: 3

## Pagination Configuration

::: kb_dashboard_core.panels.charts.datatable.config.DatatablePagingConfig
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Datatable Charts

::: kb_dashboard_core.panels.charts.datatable.config.ESQLDatatableChart
    options:
      show_root_heading: false
      heading_level: 3

## Related Documentation

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
