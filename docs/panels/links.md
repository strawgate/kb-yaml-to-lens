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
Filters carried, context served.
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

## Minimal Configuration Examples

**Linking to another Dashboard:**

```yaml
dashboards:
  - name: "Main Overview"
    panels:
      - title: "Navigate to User Details"
        grid: { x: 0, y: 0, w: 24, h: 2 }
        links:
          links:
            - label: "View User Activity Dashboard"
              dashboard: "user-activity-dashboard-id"
```

**Linking to an External URL:**

```yaml
dashboards:
  - name: "Main Overview"
    panels:
      - title: "External Resources"
        grid: { x: 24, y: 0, w: 24, h: 2 }
        links:
          links:
            - label: "Project Documentation"
              url: "https://docs.example.com/project-alpha"
              new_tab: true # Open this external link in a new tab
```

## Complex Configuration Example

This example demonstrates a Links panel with multiple link types, a vertical layout, and specific options for how links behave.

```yaml
dashboards:
  - name: "Operations Hub"
    panels:
      - title: "Quick Access"
        description: "Links to key operational dashboards and tools."
        grid: { x: 0, y: 0, w: 48, h: 3 }
        links:
          layout: "vertical" # Display links one above the other
          links:
          - label: "Service Health Dashboard"
            dashboard: "service-health-monitor-v2"
            with_time: true      # Carry over current time range
            with_filters: true   # Carry over current filters
            new_tab: false       # Open in the same tab
          - label: "System Logs (Last 1 Hour)"
            dashboard: "system-logs-deep-dive"
            # This link will use the target dashboard's default time/filters
          - label: "Runbook Wiki"
            url: "https://internal.wiki/ops/runbooks"
            new_tab: true
            encode: false # If the URL should not be encoded
          - label: "Grafana Metrics"
            url: "https://grafana.example.com/d/abcdef/service-metrics"
            new_tab: true
```

## Full Configuration Options

### Links Panel

Defines the main container for a list of links. It inherits from the [Base Panel Configuration](./base.md).

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](./base.md#grid-object-configuration). | N/A | Yes |
| `links` | `Links` object | Configuration for the links panel. | N/A | Yes |

**Links Object Configuration:**

| YAML Key | Data Type | Description | Kibana Default | Required |
| ----------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| `layout` | `Literal['horizontal', 'vertical']` | The layout of the links in the panel. | `horizontal` | No |
| `links` | `list of LinkTypes` | A list of link objects to be displayed. Each object can be a [Dashboard Link](#dashboard-link) or a [URL Link](#url-link). | `[]` (empty list) | Yes |

### Link Types

Each item in the `links` list will be one of the following types. They share common base fields.

#### Base Link Fields (Common to DashboardLink and UrlLink)

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| `id` | `string` | An optional unique identifier for the individual link item. Not typically needed. | Generated ID | No |
| `label` | `string` | The text displayed for the link. If not provided for a URL link, Kibana may show the URL itself. For dashboard links, a label is recommended. | `None` | No |

#### Dashboard Link

Represents a link to another Kibana dashboard.

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------------- | --------- | ---------------------------------------------------------------------------------------------------------- | -------------- | -------- |
| `dashboard` | `string` | The ID of the target Kibana dashboard. | N/A | Yes |
| `id` | `string` | An optional unique identifier for this link item. | Generated ID | No |
| `label` | `string` | The display text for the link. | `None` | No |
| `new_tab` | `boolean` | If `true`, the linked dashboard will open in a new browser tab. | `false` | No |
| `with_time` | `boolean` | If `true`, the linked dashboard will inherit the current time range from the source dashboard. | `true` | No |
| `with_filters` | `boolean` | If `true`, the linked dashboard will inherit the current filters from the source dashboard. | `true` | No |

#### URL Link

Represents a link to an external web URL.

| YAML Key | Data Type | Description | Kibana Default | Required |
| --------- | --------- | ---------------------------------------------------------------------------------------------------------- | -------------- | -------- |
| `url` | `string` | The full web URL that the link points to (e.g., `https://www.example.com`). | N/A | Yes |
| `id` | `string` | An optional unique identifier for this link item. | Generated ID | No |
| `label` | `string` | The display text for the link. If not set, Kibana defaults to showing the URL. | `None` | No |
| `encode` | `boolean` | If `true`, the URL will be URL-encoded before navigation. | `true` | No |
| `new_tab` | `boolean` | If `true`, the link will open in a new browser tab. | `false` | No |

## Programmatic Usage (Python)

You can create Links panels programmatically using Python:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.links.config import LinksPanel, LinksPanelConfig, UrlLink

panel = LinksPanel(
    grid=Grid(x=0, y=0, w=24, h=10),
    links=LinksPanelConfig(
        links=[
            UrlLink(
                label='Documentation',
                url='https://example.com/docs',
            ),
            UrlLink(
                label='API Reference',
                url='https://example.com/api',
            ),
        ],
    ),
)
```

To create a panel with links defined programmatically, build the list of links and pass it to the `LinksPanelConfig`:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.links.config import LinksPanel, LinksPanelConfig, UrlLink

links = [
    UrlLink(label='Docs', url='https://example.com/docs'),
    UrlLink(label='API', url='https://example.com/api'),
]

panel = LinksPanel(
    grid=Grid(x=0, y=0, w=24, h=10),
    links=LinksPanelConfig(links=links),
)
```

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
