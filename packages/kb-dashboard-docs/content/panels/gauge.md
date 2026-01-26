# Gauge Chart Panel Configuration

The Gauge chart panel displays a single metric value with optional min/max ranges and goal indicators, typically used for KPIs and progress tracking toward targets or thresholds.

## A Poem for the Progress Trackers

_For those who measure how close we are to the goal:_

```text
Not just a number on the screen,
But progress toward a target seen.
A gauge that fills from left to right,
From zero darkness into light.

Where are we now? How far to go?
The gauge will always let you know.
From minimum to maximum range,
Watch the colored needle change.

A goal line drawn across the way—
"You're almost there!" the markers say.
Arc or bullet, circle or bar:
The gauge reveals just where you are.

CPU usage, quota met,
Performance targets? Not a sweat.
Not just data, but direction clear—
The gauge tracks progress throughout the year.
```

---

## Lens Gauge Charts

::: kb_dashboard_core.panels.charts.gauge.config.LensGaugeChart
    options:
      show_root_heading: false
      heading_level: 3

## Gauge Appearance

::: kb_dashboard_core.panels.charts.gauge.config.GaugeAppearance
    options:
      show_root_heading: false
      heading_level: 3

## ES|QL Gauge Charts

::: kb_dashboard_core.panels.charts.gauge.config.ESQLGaugeChart
    options:
      show_root_heading: false
      heading_level: 3

## Related

- [Base Panel Configuration](./base.md)
- [Dashboard Configuration](../dashboard/dashboard.md)
- [Metric Charts](./metric.md)
