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

## Missing Capabilities

The following features are available in Kibana's native pie chart implementation but are not currently supported in kb-yaml-to-lens:

### Chart Shapes

**Status**: Not supported
**Impact**: Medium

Kibana supports five chart shapes: `pie`, `donut`, `treemap`, `mosaic`, and `waffle`. Currently, kb-yaml-to-lens only supports `pie` and `donut`.

**Workaround**: Use standard pie or donut charts. For hierarchical data visualization needs, consider using secondary groups with pie/donut charts.

### Legend Position

**Status**: Not supported
**Impact**: Low

Kibana allows specifying legend position (`top`, `left`, `right`, `bottom`). kb-yaml-to-lens uses Kibana's default positioning.

**Workaround**: None needed - default positioning works for most use cases.

### Legend Stats

**Status**: Not supported
**Impact**: Low

Kibana allows controlling which statistics appear in legend items (value, percent, comparison values).

**Workaround**: Use the `titles_and_text` configuration to control label and value display on slices.

### Advanced Color Mapping

**Status**: Partially supported
**Impact**: Medium

kb-yaml-to-lens creates basic color mappings with palette IDs but doesn't support:

- Custom color assignments for specific values
- Special assignment rules
- Color mode configuration

**Workaround**: Use the default color palettes. Custom colors can be configured in Kibana UI after import.

### Colors by Dimension

**Status**: Not supported
**Impact**: Medium

Kibana allows mapping specific dimension values to hex colors (e.g., "USA" → "#0000FF").

**Workaround**: Configure colors in Kibana UI after importing the dashboard.

## Related

- [Base Panel Configuration](../../base.md)
- [Dashboard Configuration](../../../dashboard/dashboard.md)
