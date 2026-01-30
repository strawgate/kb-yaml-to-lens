# Drilldowns Demo Dashboard

Demonstrates panel drilldowns including dashboard-to-dashboard navigation and URL drilldowns.

## Overview

This example shows how to configure drilldowns on Lens panels to enable interactive navigation. Drilldowns allow users to click on chart elements and either navigate to another dashboard or open an external URL.

## Features Demonstrated

| Feature | Description |
|---------|-------------|
| **Dashboard Drilldowns** | Navigate to another Kibana dashboard when clicking on a chart element |
| **URL Drilldowns** | Open an external URL (optionally with template variables) |
| **Filter Preservation** | Pass current filters to the target dashboard |
| **Time Preservation** | Pass current time range to the target dashboard |
| **Multiple Triggers** | Configure click, filter, or range triggers |
| **Multiple Drilldowns** | Add multiple drilldown actions to a single panel |

## Drilldown Types

### Dashboard Drilldown

Navigate to another dashboard with optional context preservation:

```yaml
drilldowns:
  - name: View Details
    dashboard: target-dashboard-id  # Required: target dashboard ID
    with_filters: true              # Optional: pass current filters (default: true)
    with_time: true                 # Optional: pass time range (default: true)
    triggers:                       # Optional: trigger types (default: [click])
      - click
```

### URL Drilldown

Open an external URL with optional template variables:

```yaml
drilldowns:
  - name: Open Documentation
    url: "https://docs.example.com/{{event.value}}"  # Required: URL template
    new_tab: true                                     # Optional: open in new tab (default: false)
    encode_url: true                                  # Optional: URL-encode variables (default: true)
    triggers:
      - click
```

## Trigger Types

| Trigger | Description |
|---------|-------------|
| `click` | Triggered when clicking on a data point (VALUE_CLICK_TRIGGER) |
| `filter` | Triggered when applying a filter action (FILTER_TRIGGER) |
| `range` | Triggered when selecting a time range (SELECT_RANGE_TRIGGER) |

## Dashboard Definition

<!-- markdownlint-disable MD046 -->
??? example "Drilldowns Demo (01-drilldowns-demo.yaml)"

    ```yaml
    --8<-- "examples/drilldowns/01-drilldowns-demo.yaml"
    ```
<!-- markdownlint-enable MD046 -->

## Prerequisites

- **Kibana**: Version 8.x or later
- **Target Dashboards**: For dashboard drilldowns, the target dashboards must exist in your Kibana instance

## Usage Notes

1. **Dashboard IDs**: Replace the example dashboard IDs (`event-details-dashboard`, `status-code-analysis`, etc.) with actual dashboard IDs from your Kibana instance.

2. **URL Templates**: URL drilldowns support Kibana's template syntax. Common variables include:
   - `{{event.value}}` - The clicked value
   - `{{context.panel.query}}` - The panel's query
   - `{{context.panel.filters}}` - Applied filters

3. **Data View**: This example uses `logs-*` as the data view. Adjust to match your data.

## Related

- [Drilldowns Documentation](../../panels/drilldowns.md)
- [Lens Panel Configuration](../../panels/lens.md)
- [Base Panel Configuration](../../panels/base.md)
