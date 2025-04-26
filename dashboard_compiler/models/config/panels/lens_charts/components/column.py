from pydantic import BaseModel, Field
from typing import Optional


class Column(BaseModel):
    """Represents a column object within a Lens table chart in the YAML schema."""

    field: Optional[str] = Field(None, description="(Required for dimension/metric columns) Field name. Use '___records___' for count.")
    type: str = Field(..., description="(Required) Aggregation type (e.g., terms, count, last_value, max, average).")
    label: Optional[str] = Field(None, description="(Optional) Display label for the column.")
    size: Optional[int] = Field(None, description="(Optional, for terms) Number of terms to show.")
    order_by_metric: Optional[str] = Field(
        None, description="(Optional, for terms) Label of the metric column to sort this term column by."
    )
    order_direction: str = Field("desc", description="(Optional, for terms) Sort direction: 'asc' or 'desc'. Defaults to 'desc'.")
    sort_field: Optional[str] = Field(None, description="(Optional, for last_value) Field to determine the 'last' value.")
    filter: Optional[str] = Field(None, description="(Optional, for last_value) KQL filter applied before taking the last value.")
