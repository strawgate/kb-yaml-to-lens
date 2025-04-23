from typing import Any, Dict
from pydantic import BaseModel, Field, model_serializer, model_validator
import uuid


class Grid(BaseModel):
    """Represents the grid layout for a panel in a dashboard.

    In the context of a dashboard, the grid defines the position and size of a panel.

    Commonly seen as:
    "gridData": {
        "x": 0,  # Horizontal position in the grid
        "y": 0,  # Vertical position in the grid
        "w": 24, # Width of the panel in grid units
        "h": 15, # Height of the panel in grid units
        "i": "780e08fc-1a39-401b-849f-703b951bc243"
    }
    """

    x: int
    y: int
    w: int
    h: int
    i: str | None = None

    def set_i(self, i: str) -> "Grid":
        """Set the unique identifier for the grid."""
        self.i = i
        return self


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
    panel_index: str = Field(default_factory=lambda: str(uuid.uuid4()))
    grid: Grid
    title: str
    description: str | None = None

    @model_validator(mode="after")
    def set_grid_data_id(self) -> "Panel":
        """Ensure gridData has a unique ID."""
        self.grid.set_i(self.panel_index)

        return self

    @model_serializer()
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "visualization",
            "panelIndex": self.panel_index,
            "gridData": self.grid,
            "embeddableConfig": {},
        }
