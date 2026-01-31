# Drilldowns Configuration

Drilldowns enable interactive navigation from dashboard panels. When users click on chart elements, they can either navigate to another dashboard or open an external URL with context from the clicked element.

## A Poem for the Navigator

_For those who build paths between dashboards:_

```text
Click a bar, a slice, a dot—
And suddenly you're somewhere not.
A drilldown takes you deeper still,
Through data paths at your will.

From overview to detail's door,
From summary to so much more.
The filters travel with your click,
The time range follows, smooth and quick.

Or venture to the web outside,
With URLs as your guide.
Template values fill the gap—
Context flows across the map.

So build your drilldowns, link your views,
Let users choose their data cruise.
Each click a portal, each tap a way
To discover more from what's displayed.
```

---

## Overview

Drilldowns can be added to any Lens or ESQL panel by specifying the `drilldowns` field in the panel configuration. There are two types of drilldowns:

| Type | Description | Use Case |
| ---- | ----------- | -------- |
| **Dashboard Drilldown** | Navigate to another Kibana dashboard | Deep-dive analysis, related dashboards |
| **URL Drilldown** | Open an external URL | Documentation, external systems, tickets |

## Quick Example

```yaml
panels:
  - title: Events by Status
    size: { w: half, h: 12 }
    lens:
      type: bar
      data_view: logs-*
      dimension:
        type: values
        field: http.response.status_code
        id: status
      metrics:
        - aggregation: count
          id: count
    drilldowns:
      # Navigate to another dashboard
      - name: View Status Details
        dashboard: status-details-dashboard
        with_filters: true
        with_time: true
      # Open external documentation
      - name: HTTP Status Reference
        url: "https://httpstatuses.com/{{event.value}}"
        new_tab: true
```

## Drilldown Types

### Dashboard Drilldown

::: kb_dashboard_core.panels.drilldowns.config.DashboardDrilldown
    options:
      show_root_heading: false
      heading_level: 4

### URL Drilldown

::: kb_dashboard_core.panels.drilldowns.config.UrlDrilldown
    options:
      show_root_heading: false
      heading_level: 4

## Trigger Types

::: kb_dashboard_core.panels.drilldowns.config.DrilldownTrigger
    options:
      show_root_heading: false
      heading_level: 4

Triggers determine what user action activates the drilldown:

| Trigger | Kibana Trigger | Description |
| ------- | -------------- | ----------- |
| `click` | `VALUE_CLICK_TRIGGER` | Click on a data point (default) |
| `filter` | `FILTER_TRIGGER` | Apply a filter action |
| `range` | `SELECT_RANGE_TRIGGER` | Select a time range on a chart |

## Configuration Examples

### Basic Dashboard Drilldown

Navigate to another dashboard while preserving context:

```yaml
drilldowns:
  - name: View Detailed Metrics
    dashboard: detailed-metrics-dashboard
```

### Dashboard Drilldown Without Filters

Navigate without preserving current filters:

```yaml
drilldowns:
  - name: View Clean Dashboard
    dashboard: target-dashboard
    with_filters: false
    with_time: true
```

### URL Drilldown with Template Variables

Open a URL with the clicked value:

```yaml
drilldowns:
  - name: Search in Splunk
    url: "https://splunk.example.com/search?q={{event.value}}"
    new_tab: true
    encode_url: true
```

### Multiple Triggers

Configure a drilldown to respond to multiple trigger types:

```yaml
drilldowns:
  - name: Analyze Time Period
    dashboard: time-analysis-dashboard
    triggers:
      - click
      - range
```

### Multiple Drilldowns on One Panel

Add multiple drilldown options to a single panel:

```yaml
drilldowns:
  # Primary drilldown
  - name: View Details
    dashboard: details-dashboard
    id: primary-drill
  # Secondary drilldown
  - name: Open in External System
    url: "https://external.example.com/item/{{event.value}}"
    id: external-drill
    new_tab: true
```

### Custom Drilldown ID

Specify a custom ID for stable references:

```yaml
drilldowns:
  - name: Go to Host Details
    dashboard: host-details-dashboard
    id: host-details-drilldown
```

## URL Template Variables

URL drilldowns support Kibana's template syntax for dynamic URL construction:

| Variable | Description |
| -------- | ----------- |
| `{{event.value}}` | The value of the clicked element |
| `{{event.key}}` | The key/label of the clicked element |
| `{{context.panel.query}}` | The panel's query string |
| `{{context.panel.filters}}` | Applied filters as JSON |
| `{{context.panel.timeRange.from}}` | Start of time range |
| `{{context.panel.timeRange.to}}` | End of time range |

## Supported Panel Types

Drilldowns are supported on all chart panel types:

- Lens panels (metric, bar, line, area, pie, gauge, heatmap, datatable, tagcloud, mosaic)
- ESQL panels (all chart types)

## Best Practices

1. **Use descriptive names**: The drilldown name appears in the context menu when users right-click.

2. **Preserve context when relevant**: Use `with_filters: true` and `with_time: true` for drill-down analysis.

3. **Use custom IDs**: When you need stable references, specify an `id` to prevent ID changes when reordering drilldowns.

4. **Open external URLs in new tabs**: Use `new_tab: true` for URL drilldowns to preserve the user's dashboard session.

5. **Encode URLs**: Keep `encode_url: true` (the default) to properly escape special characters in template values.

## Related Documentation

- [Drilldowns Example Dashboard](../examples/drilldowns/README.md)
- [Base Panel Configuration](./base.md)
- [Lens Panel Configuration](./lens.md)
- [ESQL Panel Configuration](./esql.md)
