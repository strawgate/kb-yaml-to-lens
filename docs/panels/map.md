# Map Panel Configuration

The `map` panel type displays geospatial data using interactive maps with customizable layers, zoom levels, and navigation controls.

## Overview

Map panels reference saved Elastic Maps objects and provide an interactive geographic visualization interface. They support various layer types including vector tiles, documents, and heatmaps, making them ideal for location-based analytics and geographic data visualization.

---

## Minimal Configuration Example

To add a Map panel, you need to specify its `type`, `grid` position, and the `saved_map_id` that references an existing saved map object in Kibana.

```yaml
dashboards:
  - name: "Geographic Dashboard"
    panels:
      - type: map
        title: "Sales by Region"
        grid:
          x: 0
          y: 0
          w: 24
          h: 18
        saved_map_id: "my-sales-map-id-12345"
```

## Complex Configuration Example

This example demonstrates a Map panel with custom map center coordinates, zoom level, layer visibility controls, and table of contents settings.

```yaml
dashboards:
  - name: "Geographic Analytics Dashboard"
    panels:
      - type: map
        title: "Traffic by Region"
        grid:
          x: 0
          y: 0
          w: 24
          h: 18
        saved_map_id: "traffic-map-id-12345"
        is_layer_toc_open: false  # Keep layer controls collapsed
        hidden_layers: ["layer-1-id", "layer-2-id"]  # Hide specific layers by default
        map_center:
          lat: 37.7749  # Latitude
          lon: -122.4194  # Longitude
          zoom: 10  # Zoom level
        open_toc_details: []  # No expanded table of contents sections
```

## Full Configuration Options

Map panels inherit from the [Base Panel Configuration](./base.md) and have the following specific fields:

| YAML Key | Data Type | Description | Kibana Default | Required |
| -------------------- | -------------------------- | ---------------------------------------------------------------------- | ------------------------------- | -------- |
| `type` | `Literal['map']` | Specifies the panel type. | `map` | Yes |
| `id` | `string` | A unique identifier for the panel. Inherited from BasePanel. | Generated ID | No |
| `title` | `string` | The title displayed on the panel header. Inherited from BasePanel. | `""` (empty string) | No |
| `hide_title` | `boolean` | If `true`, the panel title will be hidden. Inherited from BasePanel. | `false` | No |
| `description` | `string` | Panel description. Inherited from BasePanel. | `""` (empty string) | No |
| `grid` | `Grid` object | Defines the panel's position and size. Inherited from BasePanel. | N/A | Yes |
| `saved_map_id` | `string` | The ID of the saved map object to display in this panel. | N/A | Yes |
| `is_layer_toc_open` | `boolean` | If `true`, the layer table of contents will be open by default. | `false` | No |
| `hidden_layers` | `list[string]` | List of layer IDs to hide by default. | `[]` (empty list) | No |
| `map_center` | `MapCenter` object | Initial map center coordinates and zoom level. | Saved map's default view | No |
| `open_toc_details` | `list[string]` | List of TOC detail section IDs that should be expanded by default. | `[]` (empty list) | No |

### MapCenter Object

The `map_center` object configures the initial viewport of the map:

| YAML Key | Data Type | Description | Required |
| ---------- | --------- | ----------------------------------- | -------- |
| `lat` | `float` | Latitude of the map center. | Yes |
| `lon` | `float` | Longitude of the map center. | Yes |
| `zoom` | `float` | Zoom level (higher = more zoomed in). | Yes |

## Creating Saved Maps

Before using a Map panel, you need to create a saved map object in Kibana:

1. Navigate to **Maps** in the Kibana sidebar
2. Create a new map or open an existing one
3. Configure your layers, data sources, and styling
4. Save the map with a memorable name
5. Use the saved map's ID in your YAML configuration as `saved_map_id`

You can find the saved map's ID by:

* Opening the saved map in Kibana and checking the URL (e.g., `/app/maps/map/<map-id>`)
* Using the Kibana Saved Objects API
* Exporting the saved object and inspecting the `id` field

## Programmatic Usage (Python)

You can create Map panels programmatically using Python:

```python
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.maps.config import MapCenter, MapPanel

# Basic map panel
panel = MapPanel(
    grid=Grid(x=0, y=0, w=24, h=18),
    saved_map_id='my-map-id-12345',
)

# Map panel with custom viewport
panel_with_center = MapPanel(
    grid=Grid(x=0, y=0, w=24, h=18),
    saved_map_id='my-map-id-12345',
    map_center=MapCenter(
        lat=37.7749,
        lon=-122.4194,
        zoom=10,
    ),
    is_layer_toc_open=False,
    hidden_layers=['layer-1', 'layer-2'],
)
```

## Related Documentation

* [Base Panel Configuration](./base.md)
* [Kibana Maps Documentation](https://www.elastic.co/guide/en/kibana/current/maps.html)
* [Dashboard Configuration](../dashboard/dashboard.md)
