# Common Data Structures

This document describes common data structures used across various objects in the YAML schema.

## Grid Object

The `grid` object defines the position and size of a panel on the dashboard grid.

```yaml
grid:
  x: integer          # (Required) Horizontal starting position (0-based).
  y: integer          # (Required) Vertical starting position (0-based).
  w: integer          # (Required) Width of the panel in grid units.
  h: integer          # (Required) Height of the panel in grid units.
```

## Fields

*   `x` (required, integer): The horizontal starting position of the panel on the grid (0-based).
*   `y` (required, integer): The vertical starting position of the panel on the grid (0-based).
*   `w` (required, integer): The width of the panel in grid units.
*   `h` (required, integer): The height of the panel in grid units.

## Example

```yaml
grid: { x: 0, y: 0, w: 12, h: 10 }
```

## Style Object (for Map Layers)

The `style` object is used within map layers to define the visual appearance of data points.

```yaml
style:
  type: string    # (e.g., circle, marker) Symbol type.
  size: integer   # (e.g., 6) Symbol size.
  color: string   # (e.g., "#54B399") Symbol color (hex).
```

## Fields

*   `type` (string): The type of symbol to use for data points (e.g., `circle`, `marker`).
*   `size` (integer): The size of the symbol.
*   `color` (string): The hex color code for the symbol (e.g., `#RRGGBB`).

## Example

```yaml
style:
  type: circle
  size: 8
  color: "#E74C3C"
```

## Sort Object

The `sort` object is used to define sorting configuration, primarily for terms aggregations in Lens charts and options lists in controls.

```yaml
sort:
  by: string      # (Required) Field to sort by.
  direction: string # (Required) Sort direction ('asc' or 'desc').
```

## Fields

*   `by` (required, string): The field or metric to sort by. For terms aggregations, you can often use `_count` to sort by the document count in each term bucket.
*   `direction` (required, string): The sort direction. Must be either `asc` (ascending) or `desc` (descending).

## Example

```yaml
sort:
  by: "_count"
  direction: desc