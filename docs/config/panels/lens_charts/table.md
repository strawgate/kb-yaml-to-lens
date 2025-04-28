# Table Chart (Lens Datatable)

The `table` Lens chart type is used to display data in a tabular format.

```yaml
chart:
  type: table         # (Required) Visualization type: table.
  id: string          # (Optional) Unique identifier for the chart.
  columns: list       # (Required) Defines the table columns. Order matters.
```

## Fields

*   `type` (required, string): Specifies the chart type. Must be `table`.
*   `id` (optional, string): A unique identifier for the chart.
*   `columns` (required, list of objects): Defines the columns of the table. The order of objects in the list determines the order of columns in the table. See [Column Object](../components/column.md).

## Example

```yaml
dashboard:
  title: Table Chart Example
  panels:
    - panel:
        type: lens
        grid: { x: 0, y: 0, w: 24, h: 15 }
        index_pattern: logs-*
        chart:
          type: table
          columns:
            - field: user.name
              type: terms
              label: User Name
              size: 10
            - field: event.action
              type: terms
              label: Action
              size: 10
            - type: count
              label: Count
```

## Related Structures

*   [Column Object](../components/column.md)