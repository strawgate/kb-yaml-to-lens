from pydantic import BaseModel, Field

from dashboard_compiler.models.config.shared import Sort


class Dimension(BaseModel):
    """Represents a dimension object within a Lens chart in the YAML schema."""

    id: str = Field(default=None, description="(Optional) Unique identifier for the metric.")
    field: str = Field(..., description="(Required) Field name.")
    type: str = Field(..., description="(Required) Aggregation type (e.g., date_histogram, terms).")
    label: str | None = Field(None, description="(Optional) Display label for the dimension. Defaults to field name.")
    interval: str | None = Field(None, description="(Optional, for date_histogram) Time interval (e.g., auto, 1h, 1d). Defaults to 'auto'.")
    size: int | None = Field(None, description="(Optional, for terms) Number of terms to show.")
    sort: Sort | None = Field(None, description="(Optional, for terms) Sort configuration for the terms.")
