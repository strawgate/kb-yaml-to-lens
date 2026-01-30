# Links Panel Configuration

The `links` panel type is used to display a collection of hyperlinks on your dashboard. These links can point to other Kibana dashboards or external web URLs. This panel is useful for creating navigation hubs or providing quick access to related resources.

## A Poem for the Portal Keepers

_For those who build the bridges between dashboards:_

```text
Portals to dashboards near and far—
Links will take you where they are.
Horizontal rows or vertical stacks,
Teleporting users through the cracks.

Dashboard links with time preserved,
Filters carried, context preserved.
External URLs in tabs brand new,
Wiki pages, docs to pull you through.

"with_time: true" keeps your clock alive,
"with_filters" helps context survive.
What you selected stays in place
As you traverse from space to space.

From the ops hub to service views,
Your links provide the crucial clues.
No more wandering, lost and stressed—
Click once, arrive. You know the rest.
```

---

## Links Panel

::: kb_dashboard_core.panels.links.config.LinksPanel
    options:
      show_root_heading: false
      heading_level: 2

## Links Panel Configuration

::: kb_dashboard_core.panels.links.config.LinksPanelConfig
    options:
      show_root_heading: false
      heading_level: 3

## Link Types

### Dashboard Link

::: kb_dashboard_core.panels.links.config.DashboardLink
    options:
      show_root_heading: false
      heading_level: 4

### URL Link

::: kb_dashboard_core.panels.links.config.UrlLink
    options:
      show_root_heading: false
      heading_level: 4

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
