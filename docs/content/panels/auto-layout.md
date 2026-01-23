# Auto-Layout Guide

This guide explains how to use the automatic panel layout system to position panels on your dashboard without manually specifying coordinates.

## Overview

Instead of manually calculating x and y coordinates for every panel, you can use auto-layout to automatically position panels on the dashboard grid. Auto-layout works by:

1. Defining panel **size** (width and height) without position
2. Choosing a **layout algorithm** to determine how panels are arranged
3. Letting the compiler calculate optimal positions for all panels

## Quick Start

### Basic Auto-Layout Example

```yaml
dashboards:
  - name: "Auto-Layout Dashboard"
    settings:
      layout_algorithm: up-left  # Optional, defaults to 'up-left'
    panels:
      # Panel 1: Quarter-width panel (12 units wide)
      - markdown:
          content: "First panel"
        title: "Panel 1"
        size:
          w: quarter  # Semantic width - 12 units
          h: 8        # Height in grid units
        # No position specified - will be auto-positioned

      # Panel 2: Another quarter-width panel
      - markdown:
          content: "Second panel"
        title: "Panel 2"
        size:
          w: quarter
          h: 8

      # Panel 3: Half-width panel
      - markdown:
          content: "Third panel"
        title: "Panel 3"
        size:
          w: half  # Semantic width - 24 units
          h: 8
```

This creates a dashboard where panels are automatically arranged in a 2x2 grid pattern.

## Panel Size Configuration

### The `size` Field

Instead of specifying a `grid` object with x, y, w, h coordinates, you can use separate `size` and `position` fields:

```yaml
panels:
  - markdown:
      content: "My content"
    title: "My Panel"
    size:
      w: 24     # Width (or use semantic values)
      h: 8      # Height
    position:   # Optional - omit for auto-layout
      x: 0
      y: 0
```

### Semantic Width Values

The `w` (width) field accepts semantic values for common panel widths:

| Semantic Value | Grid Units | Description |
| -------------- | ---------- | ----------- |
| `whole` | 48 | Full dashboard width |
| `half` | 24 | Half width (2 panels per row) |
| `third` | 16 | One-third width (3 panels per row) |
| `quarter` | 12 | Quarter width (4 panels per row) |
| `sixth` | 8 | One-sixth width (6 panels per row) |
| `eighth` | 6 | One-eighth width (8 panels per row) |

You can also specify numeric values from 1 to 48.

### Default Size

If you omit the `size` field entirely, panels default to:

- Width: 12 units (quarter width)
- Height: 8 units

```yaml
panels:
  - markdown:
      content: "Uses default size"
    title: "Default Panel"
    # No size specified - uses w=12, h=8
```

## Layout Algorithms

The `layout_algorithm` setting in dashboard `settings` controls how panels are automatically positioned. Choose the algorithm that best fits your dashboard's content flow.

### `up-left` (Default)

Floats panels up first, then left. Creates compact, grid-like layouts.

**Best for:** Dashboards where you want panels to form neat grids.

```yaml
dashboards:
  - name: "Up-Left Example"
    settings:
      layout_algorithm: up-left
    panels:
      - markdown: { content: "A" }
        title: "Panel A"
        size: { w: quarter, h: 8 }

      - markdown: { content: "B" }
        title: "Panel B"
        size: { w: quarter, h: 8 }

      - markdown: { content: "C" }
        title: "Panel C"
        size: { w: quarter, h: 8 }

      - markdown: { content: "D" }
        title: "Panel D"
        size: { w: quarter, h: 8 }
```

**Result:** Forms a 2x2 grid with panels arranged like:

```text
[A][B]
[C][D]
```

### `left-right`

Fills rows from left to right before moving to the next row. Row height is determined by the tallest panel in that row.

**Best for:** Dashboards where you want panels to appear in reading order (left-to-right, top-to-bottom).

```yaml
dashboards:
  - name: "Left-Right Example"
    settings:
      layout_algorithm: left-right
    panels:
      - markdown: { content: "A" }
        size: { w: half, h: 8 }

      - markdown: { content: "B" }
        size: { w: half, h: 12 }  # Taller panel

      - markdown: { content: "C" }
        size: { w: third, h: 8 }

      - markdown: { content: "D" }
        size: { w: third, h: 8 }
```

**Result:**

```text
Row 1: [A (h=8)][B (h=12)]  <- Row height = 12
Row 2: [C (h=8)][D (h=8)]   <- Row height = 8
```

### `blocked`

Never fills gaps above the current bottom. Maintains strict top-to-bottom flow.

**Best for:** Dashboards where vertical ordering matters more than space efficiency.

```yaml
dashboards:
  - name: "Blocked Example"
    settings:
      layout_algorithm: blocked
    panels:
      - markdown: { content: "Tall panel" }
        size: { w: half, h: 20 }
        position: { x: 0, y: 0 }  # Locked position

      - markdown: { content: "Auto panel 1" }
        size: { w: half, h: 8 }
        # Will go to x=24, y=0 (right of tall panel)

      - markdown: { content: "Auto panel 2" }
        size: { w: half, h: 8 }
        # Will go to y=20 (below the tall panel, not filling the gap)
```

### `first-available-gap`

Scans the entire grid from top-left to find the first available gap. Maximizes space utilization.

**Best for:** Dashboards where minimizing vertical height is important.

```yaml
dashboards:
  - name: "First Available Gap Example"
    settings:
      layout_algorithm: first-available-gap
    panels:
      - markdown: { content: "Tall panel" }
        size: { w: half, h: 20 }
        position: { x: 0, y: 0 }

      - markdown: { content: "Small panel 1" }
        size: { w: half, h: 8 }
        # Will fill the gap at x=24, y=0

      - markdown: { content: "Small panel 2" }
        size: { w: half, h: 8 }
        # Will fill the gap at x=24, y=8
```

## Mixing Auto-Layout and Fixed Positions

You can mix panels with auto-layout and panels with fixed positions (called "locked panels"):

```yaml
dashboards:
  - name: "Mixed Layout"
    panels:
      # Locked panel - fixed position
      - markdown:
          content: "This stays at the top"
        title: "Header"
        size: { w: whole, h: 4 }
        position: { x: 0, y: 0 }

      # Auto-positioned panels will flow around the locked panel
      - markdown:
          content: "Auto panel 1"
        title: "Panel 1"
        size: { w: half, h: 8 }
        # No position - will be auto-positioned below the header

      - markdown:
          content: "Auto panel 2"
        title: "Panel 2"
        size: { w: half, h: 8 }
```

The auto-layout algorithm respects locked panels and positions auto panels around them.

## Field Aliases

Both `size` and `position` support verbose aliases for readability:

```yaml
size:
  width: 24   # Same as 'w'
  height: 12  # Same as 'h'

position:
  from_left: 0  # Same as 'x'
  from_top: 10  # Same as 'y'
```

## Common Patterns

### Full-Width Header with Grid Below

```yaml
panels:
  # Header
  - markdown: { content: "Dashboard Title" }
    title: "Header"
    size: { w: whole, h: 4 }

  # Grid of metrics (will auto-arrange in 2x2 grid)
  - lens: { type: metric, ... }
    size: { w: quarter }

  - lens: { type: metric, ... }
    size: { w: quarter }

  - lens: { type: metric, ... }
    size: { w: quarter }

  - lens: { type: metric, ... }
    size: { w: quarter }
```

### Two-Column Layout

```yaml
settings:
  layout_algorithm: left-right

panels:
  - markdown: { content: "Left column content" }
    size: { w: half, h: 20 }

  - markdown: { content: "Right column content" }
    size: { w: half, h: 20 }

  # These will form the second row
  - markdown: { content: "Bottom left" }
    size: { w: half, h: 10 }

  - markdown: { content: "Bottom right" }
    size: { w: half, h: 10 }
```

### Dashboard with Sidebar

```yaml
panels:
  # Fixed sidebar
  - links: { ... }
    title: "Navigation"
    size: { w: eighth, h: 40 }
    position: { x: 0, y: 0 }  # Lock to left side

  # Main content area (auto-positioned to the right)
  - lens: { type: xy, ... }
    title: "Main Chart"
    size: { w: 42, h: 20 }  # 48 - 6 = 42 remaining width

  - lens: { type: metric, ... }
    size: { w: 42, h: 20 }
```

## Related Documentation

- [Base Panel Configuration](./base.md) - Common panel fields
- [Dashboard Configuration](../dashboard/dashboard.md) - Dashboard settings
