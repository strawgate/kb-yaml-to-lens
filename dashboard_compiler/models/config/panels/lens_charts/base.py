from pydantic import BaseModel, Field
from typing import Literal


class BaseLensChart(BaseModel):
    """Base model for the 'chart' object within a Lens panel in the YAML schema."""

    type: Literal["bar", "pie"] = Field(..., description="(Required) Visualization type (e.g., 'pie', 'bar_stacked').")
