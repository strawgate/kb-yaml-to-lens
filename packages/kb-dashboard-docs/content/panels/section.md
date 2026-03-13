# Section Panel Configuration

The `section` panel type creates a collapsible section that groups panels under a named, expandable header. This is useful for organizing complex dashboards by allowing users to collapse groups of related panels to focus on specific areas.

## A Poem for the Section Architects

_For those who organize dashboards into collapsible realms:_

```text
When dashboards grow beyond the fold,
And metrics pile, both new and old,
Sections help you tame the sprawl—
Collapse them down, or show them all.

A header row spans edge to edge,
A gateway to content on the ledge.
Click to expand, click to hide,
Your nested panels safely reside.

"collapsed: true" starts them tucked away,
Until the user wants to play.
Inner panels in their own grid space,
Start at zero—their home base.

From overview to deep detail views,
Your sections give users the power to choose.
Organized dashboards, clean and bright—
Collapsible sections make it right.
```

---

## Collapsible Panel

::: kb_dashboard_core.panels.collapsible.CollapsiblePanel
    options:
      show_root_heading: false
      heading_level: 2

## Section Configuration

::: kb_dashboard_core.panels.collapsible.SectionConfig
    options:
      show_root_heading: false
      heading_level: 3

## Examples

### Basic Section with Panels

```yaml
dashboards:
  - name: "Dashboard with Sections"
    panels:
      - title: "Overview"
        size: { w: whole, h: 6 }
        markdown:
          content: "# System Overview"

      - title: "CPU Metrics"
        section:
          panels:
            - title: "CPU Usage"
              size: { w: half, h: 12 }
              lens:
                type: metric
                data_view: "metrics-*"
                primary:
                  aggregation: average
                  field: system.cpu.total.pct
            - title: "CPU History"
              size: { w: half, h: 12 }
              lens:
                type: line
                data_view: "metrics-*"
                metrics:
                  - aggregation: average
                    field: system.cpu.total.pct
                dimension:
                  field: "@timestamp"
                  type: date_histogram
```

### Collapsed by Default

Use `collapsed: true` to have a section start in a collapsed state:

```yaml
dashboards:
  - name: "Dashboard with Collapsed Section"
    panels:
      - title: "Summary"
        size: { w: whole, h: 8 }
        markdown:
          content: "# Quick Summary"

      - title: "Detailed Metrics (click to expand)"
        section:
          collapsed: true
          panels:
            - title: "Memory Usage"
              size: { w: quarter, h: 8 }
              lens:
                type: metric
                data_view: "metrics-*"
                primary:
                  aggregation: average
                  field: system.memory.used.pct
            - title: "Disk Usage"
              size: { w: quarter, h: 8 }
              lens:
                type: metric
                data_view: "metrics-*"
                primary:
                  aggregation: average
                  field: system.filesystem.used.pct
```

### Multiple Sections

Organize a dashboard into logical groups:

```yaml
dashboards:
  - name: "Infrastructure Dashboard"
    panels:
      - title: "Overview"
        size: { w: whole, h: 4 }
        markdown:
          content: "# Infrastructure Health"

      - title: "Compute Resources"
        section:
          panels:
            - title: "CPU"
              size: { w: third, h: 10 }
              lens:
                type: gauge
                data_view: "metrics-*"
                metric:
                  aggregation: average
                  field: system.cpu.total.pct
            - title: "Memory"
              size: { w: third, h: 10 }
              lens:
                type: gauge
                data_view: "metrics-*"
                metric:
                  aggregation: average
                  field: system.memory.used.pct

      - title: "Storage"
        section:
          collapsed: true
          panels:
            - title: "Disk Usage"
              size: { w: half, h: 10 }
              lens:
                type: bar
                data_view: "metrics-*"
                metrics:
                  - aggregation: average
                    field: system.filesystem.used.pct
                dimension:
                  field: host.name
                  type: values
```

## Important Notes

1. **Inner Panel Coordinates**: Panels inside a section use a **relative** coordinate space. Their `position.x` and `position.y` values (if specified) start at (0, 0) within the section body, independent of the section's position on the dashboard.

2. **Nesting Restriction**: Collapsible sections cannot be nested. A section's panels cannot contain another section panel.

3. **Default Size**: Section headers default to full width (48 grid units) and 1 row tall. The section expands vertically based on its inner panel content.

4. **Auto-Layout**: Inner panels support auto-layout. Omit the `position` field to let panels flow automatically within the section.

## Related Documentation

- [Base Panel Configuration](./base.md)
- [Auto-Layout Guide](./auto-layout.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
