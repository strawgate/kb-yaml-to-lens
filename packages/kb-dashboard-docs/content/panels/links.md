# Links Panel Configuration

The `links` panel type is used to display a collection of hyperlinks on your dashboard. These links can point to other Kibana dashboards or external web URLs. This panel is useful for creating navigation hubs or providing quick access to related resources.

## Links Panel

::: dashboard_compiler.panels.links.config.LinksPanel
    options:
      show_root_heading: false
      heading_level: 2

## Links Panel Configuration

::: dashboard_compiler.panels.links.config.LinksPanelConfig
    options:
      show_root_heading: false
      heading_level: 3

## Link Types

### Dashboard Link

::: dashboard_compiler.panels.links.config.DashboardLink
    options:
      show_root_heading: false
      heading_level: 4

### URL Link

::: dashboard_compiler.panels.links.config.UrlLink
    options:
      show_root_heading: false
      heading_level: 4

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
