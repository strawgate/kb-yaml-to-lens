from typing import Literal

from pydantic import BaseModel, Field


class BaseLensChart(BaseModel):
    """Base model for the 'chart' object within a Lens panel in the YAML schema."""

    id: str | None = Field(default=None, description="(Optional) Unique identifier for the chart.")
    type: Literal["bar", "pie"] = Field(..., description="(Required) Visualization type (e.g., 'pie', 'bar_stacked').")
