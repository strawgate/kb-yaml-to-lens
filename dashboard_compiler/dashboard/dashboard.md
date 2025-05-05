# Dashboard Object

The root of the YAML file is the `dashboard` object. It defines the overall structure and settings for the Kibana dashboard.

```yaml
dashboard:
  id: string            # (Optional) Unique identifier for the dashboard.
  title: string         # (Required) The title of the dashboard.
  description: string   # (Optional) A description for the dashboard. Defaults to "".
  data_view: string     # (Optional) The default data view (index pattern) for the dashboard.
  settings: object      # (Optional) Global settings for the dashboard.
  query: object         # (Optional) A query string to filter the dashboard data.
  filters: list         # (Optional) A list of filters to apply to the dashboard.
  controls: list        # (Optional) A list of control panels for the dashboard.
  panels: list          # (Required) A list of panel objects defining the dashboard content.
```

## Fields

*   `id` (optional, string): A unique identifier for the dashboard. If not provided, Kibana will generate one.
*   `title` (required, string): The title that will be displayed for the dashboard.
*   `description` (optional, string): A brief description of the dashboard. Defaults to an empty string.
*   `data_view` (optional, string): The default data view (index pattern) used by items in this dashboard. Panels and controls can override this setting.
*   `settings` (optional, object): Global settings for the dashboard. See [Dashboard Settings](#dashboard-settings) for more details.
*   `query` (optional, object): Defines a global query to filter data across all panels on the dashboard. See [Queries Documentation](../queries/config.md) for more details.
*   `filters` (optional, list of objects): Defines a list of global filters to apply across all panels on the dashboard. This is a list of filter objects. See [Filters Documentation](../filters/config.md) for more details.
*   `controls` (optional, list of objects): Defines a list of control panels to add to the dashboard. This is a list of control objects. See [Controls Documentation](../controls/config.md) for more details.
*   `panels` (required, list of objects): A list of panel objects that define the content and layout of the dashboard. This is a list of panel objects. See [Base Panel Object](../panels/base.md) and [Panel Types](../panels/base.md#panel-types) for more details.

## Dashboard Settings

The `settings` object configures global options for the dashboard.

```yaml
settings:
  margins: boolean    # (Optional) Whether to put space between panels. Defaults to true.
  sync: object        # (Optional) Configure synchronization across panels.
  controls: object    # (Optional) Settings for controls.
  titles: boolean     # (Optional) Whether to display panel titles. Defaults to true.
```

*   `margins` (optional, boolean): Whether to put space between panels in the dashboard. Defaults to `true` if not set.
*   `sync` (optional, object): Configure whether cursor, tooltips, and colors should sync across panels. See [Dashboard Sync Settings](#dashboard-sync-settings) for details.
*   `controls` (optional, object): Settings for controls in a dashboard, defining their behavior and appearance. See [Controls Settings](../controls/config.md#controls-settings) for details.
*   `titles` (optional, boolean): Whether to display the titles in the panel headers. Defaults to `true` if not set.

## Dashboard Sync Settings

The `sync` object within `settings` configures synchronization options across panels.

```yaml
sync:
  cursor: boolean     # (Optional) Whether to synchronize the cursor. Defaults to true.
  tooltips: boolean   # (Optional) Whether to synchronize tooltips. Defaults to true.
  colors: boolean     # (Optional) Whether to apply the same color palette. Defaults to true.
```

*   `cursor` (optional, boolean): Whether to synchronize the cursor across related panels. Defaults to `true` if not set.
*   `tooltips` (optional, boolean): Whether to synchronize tooltips across related panels. Defaults to `true` if not set.
*   `colors` (optional, boolean): Whether to apply the same color palette to all panels on the dashboard. Defaults to `true` if not set.

## Methods

The `Dashboard` object in the configuration can also use the following methods to programmatically add objects to its lists:

*   `add_filter(filter: FilterTypes)`: Add a filter object to the `filters` list.
*   `add_control(control: ControlTypes)`: Add a control object to the `controls` list.
*   `add_panel(panel: PanelTypes)`: Add a panel object to the `panels` list.

## Example

```yaml
dashboard:
  title: My Example Dashboard
  description: This is an example dashboard demonstrating various features.
  data_view: my-index-*
  settings:
    margins: false
    sync:
      cursor: false
    controls:
      label_position: above
  query:
    kql: 'response:200'
  filters:
    - field: machine.os.keyword
      equals: 'osx'
  controls:
    - type: optionsList
      label: Select Host
      data_view: logs-*
      field: host.name
  panels:
    - # ... panel definitions ...
```

## Related Documentation

*   [Queries Documentation](../queries/config.md)
*   [Filters Documentation](../filters/config.md)
*   [Controls Documentation](../controls/config.md)
*   [Base Panel Object](../panels/base.md)
*   [Panel Types](../panels/base.md#panel-types)