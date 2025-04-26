from pydantic import BaseModel, Field
from typing import Any


class Filter(BaseModel):
    """Represents a filter object within a Lens panel or metric in the YAML schema."""

    field: str = Field(..., description="(Required) Field to filter on.")
    type: str = Field(..., description="(Required) Filter type (e.g., phrase, phrases).")
    value: Any = Field(..., description="(Required) Value(s) for the filter.")
    negate: bool = Field(False, description="(Optional) Whether to negate the filter. Defaults to false.")
