"""Configuration for a Map Panel in a dashboard."""

from typing import Literal

from pydantic import Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.shared.config import BaseCfgModel


class MapCenter(BaseCfgModel):
    """Map center and zoom configuration."""

    lat: float = Field(..., description='Latitude of the map center.')
    lon: float = Field(..., description='Longitude of the map center.')
    zoom: float = Field(..., description='Zoom level of the map.')


class MapPanel(BasePanel):
    """Represents a Map panel configuration.

    Map panels display geospatial data on interactive maps with layers. The panel
    references a saved map object that contains layer definitions and data sources.
    """

    type: Literal['map'] = 'map'
    saved_map_id: str = Field(
        ...,
        description='The ID of the saved map object to display in this panel.',
    )
    is_layer_toc_open: bool | None = Field(
        default=None,
        description='If true, the layer table of contents will be open. Defaults to false if not set.',
    )
    hidden_layers: list[str] | None = Field(
        default=None,
        description='List of layer IDs to hide by default. Defaults to an empty list if not set.',
    )
    map_center: MapCenter | None = Field(
        default=None,
        description='Initial map center and zoom level. If not provided, uses the saved map defaults.',
    )
    open_toc_details: list[str] | None = Field(
        default=None,
        description='List of TOC detail section IDs that should be expanded. Defaults to an empty list if not set.',
    )
