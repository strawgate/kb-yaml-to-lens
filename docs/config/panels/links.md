# Links Panel

The `links` panel is used to display a list of links to other dashboards or external URLs.

```yaml
- panel:
    type: links
    # Common panel fields (id, title, description, grid, hide_title) also apply
    layout: string        # (Optional) Layout of the links (horizontal, vertical). Defaults to "horizontal".
    links: list           # (Required) List of link objects.
      - label: string     # (Optional) Display text for the link.
        # Choose one of the following link types:
        dashboard: string # (Optional) ID of dashboard or other object for dashboardLink.
        url: string       # (Optional) URL for urlLink.
```

## Fields

*   `type` (required, string): Must be `links`.
*   `layout` (optional, string): Specifies the layout of the links. Can be `horizontal` or `vertical`. Defaults to `horizontal`.
*   `links` (required, list of objects): A list of link objects to be displayed in the panel. Each object represents a single link.
    *   `label` (optional, string): The text that will be displayed for the link.
    *   **Link Types (Choose one):**
        *   `dashboard` (optional, string): The ID of a Kibana dashboard or other object to link to.
        *   `url` (optional, string): A full URL to an external page.

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