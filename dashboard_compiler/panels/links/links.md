# Links Panel

The `links` panel is used to display a list of links to other dashboards or external URLs.

```yaml
- panel:
    type: links
    # Common panel fields (id, title, description, grid, hide_title) also apply
    layout: string        # (Optional) Layout of the links (horizontal, vertical). Defaults to "horizontal".
    links: list           # (Required) List of link objects.
      - # Link object (see Link Types below)
```

## Fields

*   `type` (required, string): Must be `links`.
*   `layout` (optional, string): Specifies the layout of the links. Can be `horizontal` or `vertical`. Defaults to `horizontal`.
*   `links` (required, list of objects): A list of link objects to be displayed in the panel. Each object represents a single link. See [Link Types](#link-types) for details.

## Link Types

The following link types are available:

### Base Link Fields

All link types inherit from a base link with the following optional field:

*   `id` (optional, string): An optional unique identifier for the link. Not normally required.
*   `label` (optional, string): The text that will be displayed for the link. Kibana defaults to showing the URL if not set.

### Dashboard Link

Represents a link to another dashboard within a Links panel.

```yaml
- dashboard: string   # (Required) The ID of the dashboard to link to.
  new_tab: boolean    # (Optional) If true, links will open in a new tab. Defaults to false.
  with_time: boolean  # (Optional) If true, inherit the time range from the dashboard. Defaults to true.
  with_filters: boolean # (Optional) If true, inherit the filters from the dashboard. Defaults to true.
  # Base Link fields also apply
```

*   **Fields:**
    *   `dashboard` (required, string): The ID of the dashboard that the link points to.
    *   `new_tab` (optional, boolean): If `true`, links will open in a new browser tab. Kibana defaults to `false` if not set.
    *   `with_time` (optional, boolean): If `true`, the links will inherit the time range from the dashboard. Kibana defaults to `True` if not set.
    *   `with_filters` (optional, boolean): If `true`, the links will inherit the filters from the dashboard. Kibana defaults to `True` if not set.
*   **Example:**
    ```yaml
    - label: User Overview Dashboard
      dashboard: user-overview-dashboard-id
      new_tab: true
    ```

### URL Link

Represents a link to an external URL within a Links panel.

```yaml
- url: string         # (Required) The Web URL that the link points to.
  encode: boolean     # (Optional) If true, the URL will be URL-encoded. Defaults to true.
  new_tab: boolean    # (Optional) If true, the link will open in a new tab. Defaults to false.
  # Base Link fields also apply
```

*   **Fields:**
    *   `url` (required, string): The Web URL that the link points to.
    *   `encode` (optional, boolean): If `true`, the URL will be URL-encoded. Kibana defaults to `True` if not set.
    *   `new_tab` (optional, boolean): If `true`, the link will open in a new browser tab. Kibana defaults to `false` if not set.
*   **Example:**
    ```yaml
    - label: External Documentation
      url: https://docs.example.com
      new_tab: true
    ```

## Methods

The `LinksPanel` object in the configuration can also use an `add_link` method to programmatically add link objects to the `links` list.

## Example

```yaml
dashboard:
  title: Dashboard with Links
  panels:
    - panel:
        type: links
        grid: { x: 0, y: 0, w: 48, h: 3 }
        title: Related Dashboards and Resources
        layout: vertical
        links:
          - label: User Overview Dashboard
            dashboard: user-overview-dashboard-id
          - label: External Documentation
            url: https://docs.example.com
    # Example using add_link method (in Python configuration)
    # links_panel = LinksPanel(...)
    # links_panel.add_link(DashboardLink(label="Another Dashboard", dashboard="another-dashboard-id"))