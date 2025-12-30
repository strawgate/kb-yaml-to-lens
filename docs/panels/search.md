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

## Minimal Configuration Example

To add a Search panel, you need to specify its `grid` position and the `search` configuration with `saved_search_id`.

```yaml
dashboards:
  - name: "Log Monitoring Dashboard"
    panels:
      - title: "All System Logs"
        grid:
          x: 0
          y: 0
          w: 48
          h: 10
        search:
          saved_search_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef" # Example ID
```

## Complex Configuration Example (Illustrative)

Search panels primarily rely on the configuration of the saved search itself (columns, sort order, query within the saved search). The panel configuration in the dashboard YAML is straightforward. This example shows it with a description and a hidden title.

```yaml
dashboards:
  - name: "Security Incidents Overview"
    panels:
      - # Title is defined in the saved search, so we hide the panel's own title
        hide_title: true
        description: "Displays critical security alerts from the last 24 hours, as defined in the 'Critical Alerts' saved search."
        grid:
          x: 0
          y: 0
          w: 48
          h: 8
        search:
          saved_search_id: "critical-security-alerts-saved-search"
```

## Full Configuration Options

Search panels inherit from the [Base Panel Configuration](./base.md) and have one specific required field:

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ---------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. This can override the title of the saved search if desired. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](./base.md#grid-object-configuration). | N/A | Yes |
| `search` | `Search` object | Configuration for the search panel. | N/A | Yes |

**Search Object Configuration:**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------------- | ---------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------- | -------- |
| `saved_search_id` | `string` | The ID of the saved Kibana search object (from Discover app) to display in the panel. | N/A | Yes |

**Note on Behavior:** The appearance, columns displayed, sort order, and underlying query of the Search panel are primarily controlled by the configuration of the saved search itself within Kibana's Discover application. The dashboard panel configuration mainly serves to embed that saved search.

## Programmatic Usage (Python)

You can create Search panels programmatically using Python:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.search.config import SearchPanel, SearchPanelConfig

panel = SearchPanel(
    grid=Grid(x=0, y=0, w=48, h=20),
    search=SearchPanelConfig(
        saved_search_id='my-saved-search',
    ),
)
```

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
* Kibana Discover and Saved Searches documentation (external to this project).
