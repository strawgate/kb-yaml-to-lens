# Search Panel Configuration

The `search` panel type is used to embed the results of a pre-existing, saved Kibana search directly onto your dashboard. This allows you to display dynamic log views, event lists, or any other data set defined by a saved search in Discover.

## A Poem for the Log Detectives

_For those who hunt through haystacks for needles:_

```text
Saved searches from Discover's land,
Embedded on dashboards, close at hand.
No need to navigate away,
Your logs are right here on display!

Critical alerts from the last day,
Security incidents on full replay,
System logs in columns neat,
Making investigations complete.

saved_search_id is all you need,
To bring your query's results with speed.
Columns sorted, filters applied,
All your search configs right inside.

From error logs to audit trails,
Your search panel never fails.
Dynamic views that auto-update,
Helping you investigate and compute!
```

---

## Minimal Configuration Example

To add a Search panel, you need to specify its `type`, `grid` position, and the `saved_search_id`.

```yaml
dashboards:
  - name: "Log Monitoring Dashboard"
    panels:
      - type: search
        title: "All System Logs"
        grid:
          x: 0
          y: 0
          w: 12
          h: 10
        saved_search_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef" # Example ID
```

## Complex Configuration Example (Illustrative)

Search panels primarily rely on the configuration of the saved search itself (columns, sort order, query within the saved search). The panel configuration in the dashboard YAML is straightforward. This example shows it with a description and a hidden title.

```yaml
dashboards:
  - name: "Security Incidents Overview"
    panels:
      - type: search
        # Title is defined in the saved search, so we hide the panel's own title
        hide_title: true
        description: "Displays critical security alerts from the last 24 hours, as defined in the 'Critical Alerts' saved search."
        grid:
          x: 0
          y: 0
          w: 12
          h: 8
        saved_search_id: "critical-security-alerts-saved-search"
```

## Full Configuration Options

Search panels inherit from the [Base Panel Configuration](./base.md) and have one specific required field:

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ---------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `type` | `Literal['search']` | Specifies the panel type. | `search` | Yes |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. This can override the title of the saved search if desired. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](./base.md#grid-object-configuration). | N/A | Yes |
| `saved_search_id` | `string` | The ID of the saved Kibana search object (from Discover app) to display in the panel. | N/A | Yes |

**Note on Behavior:** The appearance, columns displayed, sort order, and underlying query of the Search panel are primarily controlled by the configuration of the saved search itself within Kibana's Discover application. The dashboard panel configuration mainly serves to embed that saved search.

## Programmatic Usage (Python)

You can create Search panels programmatically using Python:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.search.config import SearchPanel

panel = SearchPanel(
    grid=Grid(x=0, y=0, w=48, h=20),
    saved_search_id='my-saved-search',
)
```

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* Kibana Discover and Saved Searches documentation (external to this project).
