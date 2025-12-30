# Links Panel Configuration

The `links` panel type is used to display a collection of hyperlinks on your dashboard. These links can point to other Kibana dashboards or external web URLs. This panel is useful for creating navigation hubs or providing quick access to related resources.

## A Poem for the Navigation Navigators

_For those who build the bridges between dashboards:_

```text
Click here, click there, the journey starts,
Links connecting dashboard parts.
Horizontal rows or vertical stacks,
Helping users stay on track.

Dashboard links with time preserved,
Filters carried through, well-served.
External URLs in new tabs born,
Wiki pages, docs, and forms.

"with_time: true" keeps context flowing,
"with_filters" helps users knowing,
What they selected stays the same,
As they navigate the dashboard game.

From operations hub to service views,
Your links provide the helpful clues.
No more searching, lost and vexed,
Just click to find what should come next!
```

---

## Minimal Configuration Examples

**Linking to another Dashboard:**

```yaml
dashboards:
  - name: "Main Overview"
    panels:
      - type: links
        title: "Navigate to User Details"
        grid: { x: 0, y: 0, w: 6, h: 2 }
        links:
          - label: "View User Activity Dashboard"
            dashboard: "user-activity-dashboard-id"
```

**Linking to an External URL:**

```yaml
dashboards:
  - name: "Main Overview"
    panels:
      - type: links
        title: "External Resources"
        grid: { x: 6, y: 0, w: 6, h: 2 }
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
      - type: links
        title: "Quick Access"
        description: "Links to key operational dashboards and tools."
        grid: { x: 0, y: 0, w: 12, h: 3 }
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
| `type` | `Literal['links']` | Specifies the panel type. | `links` | Yes |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | A brief description of the panel. Inherited from BasePanel. | `""` (empty string, if `None`) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. See [Grid Object Configuration](./base.md#grid-object-configuration). | N/A | Yes |
| `layout` | `Literal['horizontal', 'vertical']` | The layout of the links in the panel. | `horizontal` | No |
| `links` | `list of LinkTypes` | A list of link objects to be displayed. Each object can be a [Dashboard Link](#dashboard-link) or a [URL Link](#url-link). | `[]` (empty list) | Yes |

### Link Types

Each item in the `links` list will be one of the following types. They share common base fields.

#### Base Link Fields (Common to DashboardLink and UrlLink)

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| `id` | `string` | An optional unique identifier for the individual link item. Not typically needed. | Generated ID | No |
| `label` | `string` | The text displayed for the link. If not provided for a URL link, Kibana may show the URL itself. For dashboard links, a label is recommended. | `None` (or URL for URL links) | No |

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
| `label` | `string` | The display text for the link. If not set, Kibana defaults to showing the URL. | `""` (empty string) or URL | No |
| `encode` | `boolean` | If `true`, the URL will be URL-encoded before navigation. | `true` | No |
| `new_tab` | `boolean` | If `true`, the link will open in a new browser tab. | `false` | No |

## Programmatic Usage (Python)

You can create Links panels programmatically using Python:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.links.config import LinksPanel, UrlLink

panel = LinksPanel(
    grid=Grid(x=0, y=0, w=24, h=10),
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
)
```

The `LinksPanel` model includes an `add_link(link: LinkTypes)` method for adding links dynamically:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.links.config import LinksPanel, UrlLink

panel = LinksPanel(
    grid=Grid(x=0, y=0, w=24, h=10),
    links=[],
)

panel.add_link(UrlLink(label='Docs', url='https://example.com/docs'))
panel.add_link(UrlLink(label='API', url='https://example.com/api'))
```

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Dashboard Configuration](../dashboard/dashboard.md)
