# Lens Panel

The `lens` panel is used to display various chart types created with Kibana Lens.

```yaml
- panel:
    type: lens
    # Common panel fields (id, title, description, grid, hide_title) also apply
    chart: object         # (Required) Nested chart definition.
    index_pattern: string # (Required) Index pattern used by the Lens visualization.
    query: string         # (Optional) Panel-specific KQL query. Defaults to "".
    filters: list         # (Optional) Panel-specific filters applied *in addition* to any global dashboard filters.
```

## Fields

*   `type` (required, string): Must be `lens`.
*   `chart` (required, object): Defines the specific Lens visualization to display. See [Lens Chart Types](#lens-chart-types) for more details.
*   `index_pattern` (required, string): The index pattern that the Lens visualization will use for data.
*   `query` (optional, string): A KQL query specific to this panel that will be applied in addition to any global dashboard query. Defaults to an empty string.
*   `filters` (optional, list of objects): A list of filters specific to this panel that will be applied in addition to any global dashboard filters. See [Panel Filters](#panel-filters) for more details.

## Example

```yaml
dashboard:
  title: Dashboard with Lens Chart
  panels:
    - panel:
        type: lens
        grid: { x: 0, y: 0, w: 24, h: 15 }
        title: My Lens Visualization
        index_pattern: logs-*
        query: 'event.category: "authentication"'
        filters:
          - field: event.outcome
            type: phrase
            value: success
            operator: equals
        chart:
          type: line # Example chart type
          # ... chart-specific fields ...
```

## Lens Chart Types

*   [Bar, Area, Line Charts](./lens_charts/xy.md)
*   [Table Chart](./lens_charts/table.md)
*   [Pie Chart](./lens_charts/pie.md)
*   [Metric Chart](./lens_charts/metric.md)

## Related Structures

*   [Panel Filters](#panel-filters)
*   [Lens Chart Components](#lens-chart-components)
*   [Axis Object](./lens_charts/base.md#axis-object)
*   [Legend Object](./lens_charts/base.md#legend-object)
*   [Appearance Object](./lens_charts/base.md#appearance-object)