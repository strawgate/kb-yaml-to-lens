from typing import Literal

from pydantic import BaseModel, Field  # Removed Literal from pydantic import

from dashboard_compiler.models.config.shared import Sort  # Import Literal from typing


class BaseControl(BaseModel):
    """Base class for controls in the YAML schema."""

    id: str = Field(default=None, description="(Optional) Unique identifier for the control.")
    type: Literal["optionsList", "rangeSlider"] = Field(..., description="(Required) Type of the control.")
    width: Literal["small", "medium", "large"] = Field("medium", description="(Optional) Width of the control. Default is 'medium'.")
    label: str | None = Field(None, description="(Optional) Display label for the control.")
    data_view: str = Field(..., description="(Required) Index pattern for the control.")
    field: str = Field(..., description="(Required) Field name for the control.")


class OptionsListControl(BaseControl):
    """Represents an Options List control in the YAML schema."""

    type: Literal["optionsList"] = "optionsList"
    search_technique: str | None = Field(None, description="(Optional) Search technique (e.g., 'prefix').")
    sort: Sort | None = Field(None, description="(Optional) Sort configuration.")


class RangeSliderControl(BaseControl):
    """Represents a Range Slider control in the YAML schema."""

    type: Literal["rangeSlider"] = "rangeSlider"
    step: int | float | None = Field(None, description="(Optional) Step value for the slider.")


# type ControlTypes = OptionsListControl | RangeSliderControl


# class Controls(BaseModel):
#     """Represents a Controls panel in the YAML schema."""

#     type: Literal["controls"] = "controls"
#     controls: List[ControlTypes] = Field(..., description="(Required) List of control objects.")
