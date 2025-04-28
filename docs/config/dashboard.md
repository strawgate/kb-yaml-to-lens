# Dashboard Object

The root of the YAML file is the `dashboard` object. It defines the overall structure and settings for the Kibana dashboard.

```yaml
dashboard:
  id: string            # (Optional) Unique identifier for the dashboard.
  title: string         # (Required) The title of the dashboard.
  description: string   # (Optional) A description for the dashboard. Defaults to "".
  query: object         # (Optional) A query string to filter the dashboard data. Defaults to an empty KQL query.
  filters: list         # (Optional) A list of filters to apply to the dashboard. Can be empty.
  controls: list        # (Optional) A list of control panels for the dashboard. Can be empty.
  panels: list          # (Required) A list of panel objects defining the dashboard content. Can be empty for an empty dashboard.
```

## Fields

*   `id` (optional, string): A unique identifier for the dashboard. If not provided, Kibana will generate one.
*   `title` (required, string): The title that will be displayed for the dashboard.
*   `description` (optional, string): A brief description of the dashboard. Defaults to an empty string.
*   `query` (optional, object): Defines a global query to filter data across all panels on the dashboard. See [Queries](#queries) for more details.
*   `filters` (optional, list of objects): Defines a list of global filters to apply across all panels on the dashboard. See [Filters](#filters) for more details.
*   `controls` (optional, list of objects): Defines a list of control panels to add to the dashboard. See [Controls](#controls) for more details.
*   `panels` (required, list of objects): A list of panel objects that define the content and layout of the dashboard. See [Panel Object](#panel-object) and [Panel Types](#panel-types) for more details.

## Example

```yaml
dashboard:
  title: My Example Dashboard
  description: This is an example dashboard demonstrating various features.
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