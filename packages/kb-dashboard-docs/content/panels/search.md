# Search Panel Configuration

The `search` panel type is used to embed the results of a pre-existing, saved Kibana search directly onto your dashboard. This allows you to display dynamic log views, event lists, or any other data set defined by a saved search in Discover.

## Search Panel

::: dashboard_compiler.panels.search.config.SearchPanel
    options:
      show_root_heading: false
      heading_level: 2

## Search Panel Configuration

::: dashboard_compiler.panels.search.config.SearchPanelConfig
    options:
      show_root_heading: false
      heading_level: 3

**Note on Behavior:** The appearance, columns displayed, sort order, and underlying query of the Search panel are primarily controlled by the configuration of the saved search itself within Kibana's Discover application. The dashboard panel configuration mainly serves to embed that saved search.

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* Kibana Discover and Saved Searches documentation (external to this project).
