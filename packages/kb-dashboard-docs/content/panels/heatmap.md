# Heatmap Chart Panel Configuration

The Heatmap chart panel displays data as a matrix where cell colors represent metric values, typically used for visualizing patterns across two categorical dimensions or time-based intensity analysis.

## A Poem for the Pattern Seekers

_For those who see the world in shades of meaning:_

```text
When numbers need a visual cue,
And gradients tell the story true,
The heatmap paints intensity—
From cold to hot, for all to see.

Two dimensions cross and meet,
Where X and Y each take a seat.
Time and category, side by side,
Color coding serves as guide.

Dark where values run down low,
Bright where metrics brightly glow.
Each cell a window, each shade a clue,
The heatmap shows what's hiding in your view.

From server loads to user trends,
On color scale the truth depends.
So here's to heatmaps, bold and bright,
That turn cold data into light!
```

---

## Minimal Configuration Example

```yaml
dashboards:
  - name: "Server Activity Dashboard"
    panels:
      - title: "Activity by Hour and Day"
        size: {w: 24, h: 15}
        lens:
          type: heatmap
          data_view: "logs-*"
          x_axis:
            field: "@timestamp"
            type: date_histogram
            label: "Hour of Day"
          y_axis:
            field: "host.name"
            type: values
            label: "Server"
          value:
            aggregation: count
            label: "Request Count"
```

## Grid and Legend Configuration Example

Customize the appearance of your heatmap with grid and legend options:

```yaml
dashboards:
  - name: "Customized Heatmap"
    panels:
      - title: "Response Time Heatmap"
        size: {w: 24, h: 15}
        lens:
          type: heatmap
          data_view: "logs-*"
          x_axis:
            field: "@timestamp"
            type: date_histogram
          y_axis:
            field: "service.name"
            type: values
          value:
            aggregation: average
            field: "response.time"
            format:
              type: duration
          grid_config:
            cells:
              show_labels: true
            x_axis:
              show_labels: true
              show_title: true
            y_axis:
              show_labels: true
              show_title: true
          legend:
            visible: show
            position: right
```

## One-Dimensional Heatmap Example

Create a 1D heatmap by omitting the Y-axis:

```yaml
dashboards:
  - name: "Hourly Traffic Pattern"
    panels:
      - title: "Traffic Intensity by Hour"
        size: {w: 48, h: 8}
        lens:
          type: heatmap
          data_view: "logs-*"
          x_axis:
            field: "@timestamp"
            type: date_histogram
            label: "Hour"
          value:
            aggregation: count
            label: "Events"
```

## Lens Heatmap Chart

::: kb_dashboard_core.panels.charts.heatmap.config.LensHeatmapChart
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Heatmap Chart

::: kb_dashboard_core.panels.charts.heatmap.config.ESQLHeatmapChart
    options:
      show_root_heading: false
      heading_level: 3

## Grid Configuration

Control the visibility of cell labels, axis labels, and titles:

::: kb_dashboard_core.panels.charts.heatmap.config.HeatmapGridConfig
    options:
      show_root_heading: false
      heading_level: 3

::: kb_dashboard_core.panels.charts.heatmap.config.HeatmapCellsConfig
    options:
      show_root_heading: false
      heading_level: 3

::: kb_dashboard_core.panels.charts.heatmap.config.HeatmapAxisConfig
    options:
      show_root_heading: false
      heading_level: 3

## Legend Configuration

Configure the color legend for your heatmap:

::: kb_dashboard_core.panels.charts.heatmap.config.HeatmapLegendConfig
    options:
      show_root_heading: false
      heading_level: 3

## Related Documentation

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
- [Legend Configuration Guide](../advanced/legend-configuration.md)
- [Heatmap Examples](../examples/heatmap-examples.yaml)
