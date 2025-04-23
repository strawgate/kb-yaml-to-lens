from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Literal, Optional, Union
import json
import uuid # Import uuid
from .base import Grid # Import base models

DEFAULT_MARKDOWN_FONT_SIZE = 12
DEFAULT_MARKDOWN_OPEN_LINKS_IN_NEW_TAB = False


class Panel(BaseModel):
    """Base class for all panel types in a dashboard.
    
    Ensures we serialize common attributes and methods for all panels.

    {
        "type": "visualization",
        "embeddableConfig": {}
        "panelIndex": uuid,
        "gridData": {}
    }
    
    """
    type: str
    panel_index: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Generate a unique panel index
    grid: Grid
    title: str
    description: Optional[str] = None

    @model_validator(mode='after')
    def set_grid_data_id(self) -> 'Panel':
        """Ensure gridData has a unique ID."""
        if not hasattr(self.grid, "i"):
            self.grid.set_i(self.panel_index)

        return self

    # @model_validator(mode='before')
    # @classmethod
    # def set_model_type(cls, data: Any) -> Any:
    #     if not isinstance(data, dict):
    #         return data
    #     panel_type = data.get('type')
    #     if panel_type == 'search':
    #         return SearchPanel(**data)
    #     elif panel_type == 'markdown':
    #         return MarkdownPanel(**data)
    #     elif panel_type == 'map':
    #         return MapPanel(**data)
    #     elif panel_type == 'lens':
    #         return LensPanel(**data)
    #     return data

    def to_dict(self) -> Dict[str, Any]:
        # This will be overridden by subclasses
        return {
            "type": self.type,
            "panelIndex": self.panel_index,
            "gridData": self.grid.model_dump(exclude_none=True),
            "embeddableConfig": {},
        }

class SearchPanel(Panel):
    saved_search_id: str
    type: Literal["search"] = "search"

    def to_dict(self) -> Dict[str, Any]:
        # Basic structure for a search panel in JSON
        panel_id = str(uuid.uuid4()) # Generate UUID
        grid_data = self.grid.model_dump(exclude_none=True)
        grid_data["i"] = panel_id # Add UUID to gridData

        return {
            "type": "search",
            "panelIndex": panel_id, # Use generated UUID
            "gridData": grid_data,
            "embeddableConfig": {
                "enhancements": {} # Default enhancements for search
            },
            "version": "8.7.1" # Placeholder version
        }

class MarkdownPanel(Panel):
    content: str
    type: Literal["markdown"] = "markdown"
    font_size: Optional[int] = 12
    open_links_in_new_tab: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        # Structure for a markdown panel (visualization type in JSON)
        panel_id = str(uuid.uuid4()) # Generate UUID
        grid_data = self.grid.model_dump(exclude_none=True)
        grid_data["i"] = panel_id # Add UUID to gridData

        return {
            "type": "visualization", # Outer type for JSON
            "panelIndex": panel_id, # Use generated UUID
            "gridData": grid_data,
            "embeddableConfig": {
                "savedVis": {
                    "description": self.description,
                    #"id": "",
                    "params": {
                        "fontSize": DEFAULT_MARKDOWN_FONT_SIZE,
                        "openLinksInNewTab": DEFAULT_MARKDOWN_OPEN_LINKS_IN_NEW_TAB,
                        "markdown": self.content
                    },
                    "title": self.title,
                    "type": "markdown", # Kibana visualization type
                    "uiState": {}
                }
            }
        }

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
                "type": "ES_SEARCH", # Assuming ES_SEARCH for data layers
                "indexPatternRefName": "placeholder" # Need to handle reference names
            }
            json_data["index_pattern"] = self.index_pattern # This might be redundant depending on final JSON structure
        elif self.type == "vector_tile":
             json_data["sourceDescriptor"] = {
                "type": "EMS_TMS", # Assuming EMS_TMS for vector_tile
                "isAutoSelect": True # Common for base maps
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
             json_data["sourceDescriptor"]["tooltipProperties"] = [{"field": field} for field in self.tooltip_fields] # Assuming this format

        # Remove None values and empty lists/dicts
        json_data = {k: v for k, v in json_data.items() if v is not None and v != {} and v != []}

        return json_data


class MapPanel(Panel):
    layers: List[MapLayer]
    type: Literal["map"] = "map" # Added type literal for consistency

    def to_dict(self) -> Dict[str, Any]:
        # Structure for a map panel in JSON
        panel_id = str(uuid.uuid4()) # Generate UUID
        grid_data = self.grid.model_dump(exclude_none=True)
        grid_data["i"] = panel_id # Add UUID to gridData

        return {
            "type": "map",
            "panelIndex": panel_id, # Use generated UUID
            "gridData": grid_data,
            "embeddableConfig": {
                "attributes": {
                    "title": self.title,
                    "description": "", # Map panels in samples have empty description
                    "layerListJSON": json.dumps([layer.to_dict() for layer in self.layers]),
                    "mapStateJSON": "{}", # Placeholder map state
                    "uiStateJSON": "{}" # Placeholder ui state
                },
                "enhancements": {},
                "hiddenLayers": [], # Assuming no hidden layers for now
                "isLayerTOCOpen": False, # Default
                "mapBuffer": {}, # Placeholder map buffer
                "mapCenter": {}, # Placeholder map center
                "openTOCDetails": [] # Default
            },
            "version": "8.7.1" # Placeholder version
        }

# Placeholder for LensPanel - will be moved here later
class LensPanel(Panel):
     # This will be populated in a later step
     pass