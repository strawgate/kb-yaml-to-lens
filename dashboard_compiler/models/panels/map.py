from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Optional
import json
import uuid

from dashboard_compiler.models.panels.base import Panel


class MapLayerStyle(BaseModel):
    type: str
    size: Optional[int] = None
    color: Optional[str] = None


class MapLayer(BaseModel):
    type: str
    label: Optional[str] = None
    index_pattern: Optional[str] = None
    query: Optional[str] = None
    geo_field: Optional[str] = None
    style: Optional[MapLayerStyle] = None
    tooltip_fields: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        json_data = {
            "type": self.type,
            "label": self.label,
        }
        if self.index_pattern:
            json_data["sourceDescriptor"] = {
                "type": "ES_SEARCH",  # Assuming ES_SEARCH for data layers
                "indexPatternRefName": "placeholder",  # Need to handle reference names
            }
            json_data["index_pattern"] = self.index_pattern  # This might be redundant depending on final JSON structure
        elif self.type == "vector_tile":
            json_data["sourceDescriptor"] = {
                "type": "EMS_TMS",  # Assuming EMS_TMS for vector_tile
                "isAutoSelect": True,  # Common for base maps
            }

        if self.query:
            json_data["query"] = {"language": "kuery", "query": self.query}

        if self.geo_field:
            if "sourceDescriptor" not in json_data:
                json_data["sourceDescriptor"] = {}
            json_data["sourceDescriptor"]["geoField"] = self.geo_field

        if self.style:
            json_data["style"] = self.style.model_dump(exclude_none=True)

        if self.tooltip_fields is not None:
            if "sourceDescriptor" not in json_data:
                json_data["sourceDescriptor"] = {}
            json_data["sourceDescriptor"]["tooltipProperties"] = [{"field": field} for field in self.tooltip_fields]  # Assuming this format

        # Remove None values and empty lists/dicts
        json_data = {k: v for k, v in json_data.items() if v is not None and v != {} and v != []}

        return json_data


class MapPanel(Panel):
    layers: List[MapLayer]
    type: Literal["map"] = "map"  # Added type literal for consistency

    def to_dict(self) -> Dict[str, Any]:
        # Structure for a map panel in JSON
        panel_id = str(uuid.uuid4())  # Generate UUID
        grid_data = self.grid.model_dump(exclude_none=True)
        grid_data["i"] = panel_id  # Add UUID to gridData

        return {
            "type": "map",
            "panelIndex": panel_id,  # Use generated UUID
            "gridData": grid_data,
            "embeddableConfig": {
                "attributes": {
                    "title": self.title,
                    "description": "",  # Map panels in samples have empty description
                    "layerListJSON": json.dumps([layer.to_dict() for layer in self.layers]),
                    "mapStateJSON": "{}",  # Placeholder map state
                    "uiStateJSON": "{}",  # Placeholder ui state
                },
                "enhancements": {},
                "hiddenLayers": [],  # Assuming no hidden layers for now
                "isLayerTOCOpen": False,  # Default
                "mapBuffer": {},  # Placeholder map buffer
                "mapCenter": {},  # Placeholder map center
                "openTOCDetails": [],  # Default
            },
            "version": "8.7.1",  # Placeholder version
        }
