from pydantic import BaseModel, Field


class Grid(BaseModel):
    """Represents the 'grid' object in the YAML schema."""

    x: int = Field(..., description="(Required) Horizontal starting position (0-based).")
    y: int = Field(..., description="(Required) Vertical starting position (0-based).")
    w: int = Field(..., description="(Required) Width of the panel in grid units.")
    h: int = Field(..., description="(Required) Height of the panel in grid units.")

    def __repr__(self):
        return f"Grid(x={self.x}, y={self.y}, w={self.w}, h={self.h})"


class BasePanel(BaseModel):
    """Base model for panel objects in the YAML schema."""

    id: str | None = Field(default=None, description="(Optional) Unique identifier for the panel.")
    title: str = Field("", description="(Required) The title displayed on the panel. Can be empty.")
    description: str = Field("", description="(Optional) A description for the panel.")
    type: str = Field(..., description="(Required) The type of panel.")
    grid: Grid = Field(..., description="(Required) Defines the panel's position and size on the dashboard grid.")
    hide_title: bool | None = Field(None, description="(Optional) Whether to hide the panel title. Defaults to None (not hidden).")
