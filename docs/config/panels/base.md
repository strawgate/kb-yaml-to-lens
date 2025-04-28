# Base Panel Object

All panel types share a common base structure defined by the `panel` object.

```yaml
- panel:
    id: string            # (Optional) Unique identifier for the panel.
    title: string         # (Required) The title displayed on the panel. Can be empty.
    description: string   # (Optional) A description for the panel. Defaults to "".
    type: string          # (Required) The type of panel.
    grid: object          # (Required) Defines the panel's position and size on the dashboard grid.
    hide_title: boolean   # (Optional) Whether to hide the panel title. Defaults to false.
    # --- Panel Type Specific Fields Below ---
```

## Fields

*   `id` (optional, string): A unique identifier for the panel. If not provided, Kibana will generate one.
*   `title` (required, string): The title displayed on the panel header. Can be an empty string.
*   `description` (optional, string): A brief description of the panel. Defaults to an empty string.
*   `type` (required, string): The type of panel. This determines the specific configuration options available. See [Panel Types](#panel-types) for valid values.
*   `grid` (required, object): Defines the panel's position and size on the dashboard grid. See [Grid Object](#grid-object) for more details.
*   `hide_title` (optional, boolean): If set to `true`, the panel title will be hidden. Defaults to `false`.

## Example

```yaml
- panel:
    title: My Panel
    type: markdown # Example type
    grid: { x: 0, y: 0, w: 12, h: 10 }
    hide_title: true
    # ... type-specific fields ...
```

## Panel Types

*   [Search Panel](./search.md)
*   [Markdown Panel](./markdown.md)
*   [Map Panel](./map.md)
*   [Links Panel](./links.md)
*   [Lens Panel](./lens.md)