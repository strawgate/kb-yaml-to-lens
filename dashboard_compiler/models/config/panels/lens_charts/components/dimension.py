from pydantic import BaseModel, Field
from typing import Optional

from dashboard_compiler.models.config.shared import Sort


class Dimension(BaseModel):
    """Represents a dimension object within a Lens chart in the YAML schema."""

    field: str = Field(..., description="(Required) Field name.")
    type: str = Field(..., description="(Required) Aggregation type (e.g., date_histogram, terms).")
    label: Optional[str] = Field(None, description="(Optional) Display label for the dimension. Defaults to field name.")
    interval: Optional[str] = Field(
        None, description="(Optional, for date_histogram) Time interval (e.g., auto, 1h, 1d). Defaults to 'auto'."
    )
    size: Optional[int] = Field(None, description="(Optional, for terms) Number of terms to show.")
    sort: Optional[Sort] = Field(None, description="(Optional, for terms) Sort configuration for the terms.")
