# Dashboard Configuration

The `dashboards` array is the root element in your YAML configuration file. Each dashboard defines the overall structure, content, and global settings for a Kibana dashboard.

## Minimal Configuration Example

A minimal dashboard requires a `name` and at least one panel.

```yaml
dashboards:
  - name: "Simple Log Dashboard"
    panels:
      - markdown:
          content: "Welcome to the dashboard!"
        size: {w: 6, h: 3}
```

## Complex Configuration Example

This example showcases a dashboard with various settings, a global query, filters, controls, and multiple panels.

```yaml
dashboards:
  - name: "Comprehensive Application Overview"
    description: "An overview of application performance and logs, with interactive filtering."
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
      - exists: resource.attributes.host.name
    controls:
      - type: options
        label: "Filter by Host"
        data_view: "metrics-*"
        field: "resource.attributes.host.name"
    panels:
      - markdown:
          content: "### Key Performance Indicators"
        size: {w: 12, h: 2}
      - lens:
          type: metric
          primary:
            aggregation: unique_count
            field: resource.attributes.host.name
          data_view: "metrics-*"
        title: "Total Hosts"
        size: {w: 4, h: 4}
        position: {x: 0, y: 2}
      - lens:
          type: bar
          dimension:
            type: values
            field: "resource.attributes.os.type"
          metrics:
            - aggregation: unique_count
              field: resource.attributes.host.name
          data_view: "metrics-*"
        title: "Hosts by OS Type"
        size: {w: 8, h: 4}
        position: {x: 4, y: 2}
```

## Full Configuration Options

### Dashboard Object

The main object defining the dashboard.

| YAML Key | Data Type | Description | Compiler Default | Required |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `name` | `string` | The title of the dashboard displayed in Kibana. | N/A | Yes |
| `id` | `string` | An optional unique identifier for the dashboard. If not provided, one will be generated based on the name. | Generated ID | No |
| `description` | `string` | A brief description of the dashboard's purpose or content. | `""` (empty string) | No |
| `time_range` | `TimeRange` object | A default time range to apply when opening the dashboard. See [Time Range](#time-range-time_range). | `None` | No |
| `settings` | `DashboardSettings` object | Global settings for the dashboard. See [Dashboard Settings](#dashboard-settings-settings). | See defaults below | No |
| `query` | `Query` object | A global query (KQL or Lucene) applied to the dashboard. See [Queries Documentation](../queries/config.md). | `None` | No |
| `filters` | `list of Filter objects` | A list of global filters applied to the dashboard. See [Filters Documentation](../filters/config.md). | `[]` (empty list) | No |
| `controls` | `list of Control objects` | A list of control panels for the dashboard. See [Controls Documentation](../controls/config.md). | `[]` (empty list) | No |
| `panels` | `list of Panel objects` | A list of Panel objects defining the content and layout. See [Panels Documentation](../panels/base.md). | `[]` (empty list) | Yes |

### Time Range (`time_range`)

Configure a default time range that will be restored when opening the dashboard. When `time_range` is set, Kibana will automatically apply the specified time range instead of using the global time picker value.

| YAML Key | Data Type | Description | Compiler Default | Required |
| -------- | --------- | ----------- | ------- | -------- |
| `from` | `string` | The start of the time range. Supports relative time expressions like `now-30d/d`, `now-1h`, etc. | N/A | Yes |
| `to` | `string` | The end of the time range. Supports relative time expressions. | `now` | No |

**Example:**

```yaml
dashboards:
  - name: "Last 30 Days Overview"
    time_range:
      from: "now-30d/d"
      to: "now"
    panels:
      - markdown:
          content: "This dashboard defaults to the last 30 days."
        size: {w: 12, h: 3}
```

### Dashboard Settings (`settings`)

Global settings for the dashboard, configured under the `dashboard.settings` path.

| YAML Key | Data Type | Description | Compiler Default | Required |
| ------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `margins` | `boolean` | Whether to put space (margins) between panels in the dashboard. | `true` | No |
| `sync` | `DashboardSyncSettings` object | Configures synchronization of cursor, tooltips, and colors across panels. See [Dashboard Sync Settings](#dashboard-sync-settings-settingssync). | See defaults below | No |
| `controls` | `ControlSettings` object | Global settings for controls on the dashboard. See [Controls Documentation](../controls/config.md#control-settings-settingscontrols). | See defaults in Controls docs | No |
| `titles` | `boolean` | Whether to display the titles in the panel headers. | `true` | No |
| `layout_algorithm` | `string` | The auto-layout algorithm for positioning panels without explicit coordinates. Valid values: `up-left`, `left-right`, `blocked`, `first-available-gap`. | `up-left` | No |

### Dashboard Sync Settings (`settings.sync`)

Configure whether cursor, tooltips, and colors should synchronize across panels.

> **Note:** The compiler applies different defaults than Kibana's native defaults. Kibana's native defaults are all `true`, but the compiler intentionally defaults `tooltips` and `colors` to `false` for a cleaner dashboard experience.

| YAML Key | Data Type | Description | Compiler Default | Required |
| ---------- | --------- | ---------------------------------------------------------------------------------------------------------- | ---------------- | -------- |
| `cursor` | `boolean` | Whether to synchronize the cursor across related panels. | `true` | No |
| `tooltips` | `boolean` | Whether to synchronize tooltips across related panels. | `false` | No |
| `colors` | `boolean` | Whether to apply the same color palette to all panels on the dashboard. | `false` | No |

## Methods (for programmatic generation)

While primarily declarative, the underlying Pydantic models for `Dashboard` support methods for adding components if you are generating configurations programmatically (not directly used in YAML):

* `add_filter(filter: FilterTypes)`: Adds a filter to the `filters` list.
* `add_control(control: ControlTypes)`: Adds a control to the `controls` list.
* `add_panel(panel: PanelTypes)`: Adds a panel to the `panels` list.

## Related Documentation

* [Controls Configuration](../controls/config.md)
* [Filters Configuration](../filters/config.md)
* [Queries Configuration](../queries/config.md)
* [Panels Overview](../panels/base.md)
