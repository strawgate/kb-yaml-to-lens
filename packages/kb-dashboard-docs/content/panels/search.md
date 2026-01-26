# Search Panel Configuration

The `search` panel type is used to embed the results of a pre-existing, saved Kibana search directly onto your dashboard. This allows you to display dynamic log views, event lists, or any other data set defined by a saved search in Discover.

## A Poem for the Log Detectives

_For those who hunt through haystacks for needles:_

```text
The case runs hot. The logs are cold.
But Discover's got the clues on hold.
Embedded here upon your board—
No need to leave; it's all aboard.

Security breaches? Last night's crime?
System errors frozen in time?
Columns lined up, suspects neat,
Each row of evidence, complete.

saved_search_id—that's your lead,
The only clue you'll ever need.
Filters applied, the query's set,
The perp's in there. I'd place a bet.

From error logs to audit trails,
This search panel never fails.
Dynamic views that auto-scroll—
The log detective's on patrol.
```

---

## Search Panel

::: kb_dashboard_core.panels.search.config.SearchPanel
    options:
      show_root_heading: false
      heading_level: 2

## Search Panel Configuration

::: kb_dashboard_core.panels.search.config.SearchPanelConfig
    options:
      show_root_heading: false
      heading_level: 3

**Note on Behavior:** The appearance, columns displayed, sort order, and underlying query of the Search panel are primarily controlled by the configuration of the saved search itself within Kibana's Discover application. The dashboard panel configuration mainly serves to embed that saved search.

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* Kibana Discover and Saved Searches documentation (external to this project).
