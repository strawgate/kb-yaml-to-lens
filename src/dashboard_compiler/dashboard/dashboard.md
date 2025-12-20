# Dashboard Configuration

The `dashboard` object is the root element in your YAML configuration file. It defines the overall structure, content, and global settings for a Kibana dashboard.

## Minimal Configuration Example

A minimal dashboard requires a `name` and at least one panel.

```yaml
dashboard:
  name: "Simple Log Dashboard"
  panels:
    - type: markdown # Assuming a markdown panel type exists
      content: "Welcome to the dashboard!"
      grid:
        x: 0
        y: 0
        w: 6
        h: 3
```

## Complex Configuration Example

This example showcases a dashboard with various settings, a default data view, a global query, filters, controls, and multiple panels.

```yaml
dashboard:
  name: "Comprehensive Application Overview"
  id: "app-overview-001"
  description: "An overview of application performance and logs, with interactive filtering."
  data_view: "production-logs-*" # Default data view for all items unless overridden
  settings:
    margins: true
    titles: true
    sync:
      cursor: true
      tooltips: true
      colors: false # Use distinct color palettes per panel
    controls:
      label_position: "above"
      chain_controls: true
  query:
    kql: "NOT response_code:500" # Global KQL query
  filters:
    - field: "geo.country_iso_code"
      equals: "US"
    - field: "service.environment"
      is_one_of: ["production", "staging"]
  controls:
    - type: options
      label: "Filter by Region"
      data_view: "user-sessions-*"
      field: "user.geo.region_name"
      width: "medium"
  panels:
    - type: markdown
      content: "### Key Performance Indicators"
      grid: { x: 0, y: 0, w: 12, h: 2 }
    - type: lens_metric # Assuming a lens metric panel type
      title: "Total Requests"
      data_view: "apm-traces-*"
      metrics:
        - type: count
      grid: { x: 0, y: 2, w: 4, h: 4 }
    - type: lens_bar_chart # Assuming a lens bar chart panel type
      title: "Requests by Response Code"
      data_view: "apm-traces-*"
      series_type: "bar"
      x_axis:
        field: "http.response.status_code"
      metrics:
        - type: count
      grid: { x: 4, y: 2, w: 8, h: 4 }
```

## Full Configuration Options

### Dashboard Object

The main object defining the dashboard.

| YAML Key      | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `name`        | `string`                                   | The title of the dashboard displayed in Kibana.                                                            | N/A              | Yes      |
| `id`          | `string`                                   | An optional unique identifier for the dashboard. If not provided, one will be generated based on the name. | Generated ID     | No       |
| `description` | `string`                                   | A brief description of the dashboard's purpose or content.                                                 | `""` (empty string) | No       |
| `settings`    | `DashboardSettings` object                 | Global settings for the dashboard. See [Dashboard Settings](#dashboard-settings).                          | See defaults below | No       |
| `data_view`   | `string`                                   | The default data view (index pattern) ID or title used by items in this dashboard unless overridden.       | `None`           | No       |
| `query`       | `Query` object                             | A global query (KQL or Lucene) applied to the dashboard. See [Queries Documentation](../queries/config.md). | `None`           | No       |
| `filters`     | `list of Filter objects`                   | A list of global filters applied to the dashboard. See [Filters Documentation](../filters/config.md).      | `[]` (empty list)| No       |
| `controls`    | `list of Control objects`                  | A list of control panels for the dashboard. See [Controls Documentation](../controls/config.md).           | `[]` (empty list)| No       |
| `panels`      | `list of Panel objects`                    | A list of panels defining the content and layout. See [Panels Documentation](../panels/base.md).           | `[]` (empty list)| Yes      |

### Dashboard Settings (`settings`)

Global settings for the dashboard, configured under the `dashboard.settings` path.

| YAML Key   | Data Type                                  | Description                                                                                                | Kibana Default   | Required |
| ---------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `margins`  | `boolean`                                  | Whether to put space (margins) between panels in the dashboard.                                            | `true`           | No       |
| `sync`     | `DashboardSyncSettings` object             | Configures synchronization of cursor, tooltips, and colors across panels. See [Dashboard Sync Settings](#dashboard-sync-settings). | See defaults below | No       |
| `controls` | `ControlSettings` object                   | Global settings for controls on the dashboard. See [Controls Documentation](../controls/config.md#control-settings). | See defaults in Controls docs | No       |
| `titles`   | `boolean`                                  | Whether to display the titles in the panel headers.                                                        | `true`           | No       |

### Dashboard Sync Settings (`settings.sync`)

Configure whether cursor, tooltips, and colors should synchronize across panels.

| YAML Key   | Data Type | Description                                                                                                | Kibana Default   | Required |
| ---------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `cursor`   | `boolean` | Whether to synchronize the cursor across related panels.                                                   | `true`           | No       |
| `tooltips` | `boolean` | Whether to synchronize tooltips across related panels.                                                     | `true`           | No       |
| `colors`   | `boolean` | Whether to apply the same color palette to all panels on the dashboard.                                    | `true`           | No       |

## Methods (for programmatic generation)

While primarily declarative, the underlying Pydantic models for `Dashboard` support methods for adding components if you are generating configurations programmatically (not directly used in YAML):

*   `add_filter(filter: FilterTypes)`: Adds a filter to the `filters` list.
*   `add_control(control: ControlTypes)`: Adds a control to the `controls` list.
*   `add_panel(panel: PanelTypes)`: Adds a panel to the `panels` list.

## Related Documentation

*   [Controls Configuration](../controls/config.md)
*   [Filters Configuration](../filters/config.md)
*   [Queries Configuration](../queries/config.md)
*   [Panels Overview](../panels/base.md)