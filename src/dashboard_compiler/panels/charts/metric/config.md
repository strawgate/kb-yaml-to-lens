# Metric Chart Panel Configuration

The Metric chart panel displays a single value or a small set of key metrics, often used for KPIs or summary statistics.

## Minimal Configuration Example

```yaml
dashboard:
  name: "KPI Dashboard"
  panels:
    - type: metric
      title: "Total Revenue"
      grid: { x: 0, y: 0, w: 3, h: 2 }
      data:
        index: "sales-data"
        value: "revenue"
```

## Full Configuration Options

| YAML Key      | Data Type         | Description                                      | Required |
|--------------|-------------------|--------------------------------------------------|----------|
| `type`       | `Literal['metric']`| Specifies the panel type.                        | Yes      |
| `title`      | `string`          | Title of the panel.                              | No       |
| `grid`       | `Grid` object     | Position and size of the panel.                  | Yes      |
| `data`       | `object`          | Data source and field mapping.                   | Yes      |
| `value`      | `string`          | Field for the metric value.                      | Yes      |
| `color`      | `string`          | Color for the metric display.                    | No       |
| `description`| `string`          | Panel description.                               | No       |

## Related
- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md) 