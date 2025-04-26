from typing import Literal
from pydantic import BaseModel, Field


class Sort(BaseModel):
    """Represents the sort configuration for a control in the YAML schema."""

    by: str = Field(..., description="(Required) Field to sort by.")
    direction: Literal["asc", "desc"] = Field(..., description="(Required) Sort direction ('asc' or 'desc').")
