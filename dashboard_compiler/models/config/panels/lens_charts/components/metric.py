from pydantic import BaseModel, Field
from typing import Optional


class Metric(BaseModel):
    """Represents a metric object within a Lens chart in the YAML schema."""

    type: str = Field(..., description="(Required) Aggregation type (e.g., count, max, average, unique_count, formula, last_value).")
    label: Optional[str] = Field(None, description="(Optional) Display label for the metric. Defaults to standard label (e.g., 'Count').")
    field: Optional[str] = Field(
        None, description="(Optional, required for most types except count) Field name. Use '___records___' for count."
    )
    formula: Optional[str] = Field(None, description="(Optional, for type: formula) The formula string.")
    sort_field: Optional[str] = Field(None, description="(Optional, for last_value) Field to determine the 'last' value.")
    filter: Optional[str] = Field(None, description="(Optional, for last_value) KQL filter applied before taking the last value.")
