# Pie Chart Panel Configuration

The Pie chart panel visualizes data as a pie or donut chart, useful for showing proportions of a whole.

## Minimal Configuration Example

```yaml
dashboard:
  name: "Traffic Sources"
  panels:
    - type: pie
      title: "Website Traffic Sources"
      grid: { x: 0, y: 0, w: 6, h: 6 }
      data:
        index: "traffic-data"
        category: "source"
        value: "visits"
```

## Full Configuration Options

| YAML Key      | Data Type         | Description                                      | Required |
|--------------|-------------------|--------------------------------------------------|----------|
| `type`       | `Literal['pie']`  | Specifies the panel type.                        | Yes      |
| `title`      | `string`          | Title of the panel.                              | No       |
| `grid`       | `Grid` object     | Position and size of the panel.                  | Yes      |
| `data`       | `object`          | Data source and field mapping.                   | Yes      |
| `category`   | `string`          | Field for pie slices (categories).               | Yes      |
| `value`      | `string`          | Field for values (size of slices).               | Yes      |
| `donut`      | `boolean`         | Display as donut chart.                          | No       |
| `color`      | `string/list`     | Color(s) for slices.                             | No       |
| `legend`     | `object`          | Legend display options.                          | No       |
| `description`| `string`          | Panel description.                               | No       |

## Related
- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md) 