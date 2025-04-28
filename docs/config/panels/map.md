# Map Panel

The `map` panel is used to display geographical data on a map.

```yaml
- panel:
    type: map
    # Common panel fields (id, title, description, grid, hide_title) also apply
    layers: list          # (Required) List of map layers.
      - type: string      # (Required) Type of the layer (e.g., vector_tile, geojson_vector).
        label: string     # (Optional) Label for the layer.
        # --- Layer Type Specific Fields Below ---
        # Example for geojson_vector:
        index_pattern: string # (Required for data layers) Index pattern to use.
        query: string     # (Optional) KQL query specific to this layer.
        geo_field: string # (Required for geo layers) Field containing geo data (e.g., source.geo.location).
        style: object     # (Optional) Styling options.
          type: string    # (e.g., circle, marker) Symbol type.
          size: integer   # (e.g., 6) Symbol size.
          color: string   # (e.g., "#54B399") Symbol color (hex).
        tooltip_fields: list # (Optional) List of fields (strings) to show in the tooltip.
```

## Fields

*   `type` (required, string): Must be `map`.
*   `layers` (required, list of objects): Defines the layers to be displayed on the map. Each object in the list represents a single layer.
    *   `type` (required, string): The type of map layer (e.g., `vector_tile` for base maps, `geojson_vector` for data layers).
    *   `label` (optional, string): A label for the layer.
    *   **Data Layer Specific Fields (e.g., for `geojson_vector` type):**
        *   `index_pattern` (required, string): The index pattern to use for the data layer.
        *   `query` (optional, string): A KQL query specific to this layer to filter the data.
        *   `geo_field` (required, string): The name of the field containing geographical data.
        *   `style` (optional, object): Defines the visual appearance of the data points on the map. See [Style Object](#style-object) for more details.
        *   `tooltip_fields` (optional, list of strings): A list of field names whose values will be displayed in tooltips when hovering over data points.

## Example

```yaml
dashboard:
  title: Dashboard with Map
  panels:
    - panel:
        type: map
        grid: { x: 0, y: 0, w: 48, h: 25 }
        title: User Locations
        layers:
          - type: vector_tile
            label: Base Map
          - type: geojson_vector
            label: User Data
            index_pattern: users-*
            query: 'status: active'
            geo_field: user.location
            style:
              type: circle
              size: 8
              color: "#E74C3C"
            tooltip_fields:
              - user.name
              - user.city
```

## Related Structures

*   [Style Object](#style-object)