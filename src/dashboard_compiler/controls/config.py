"""Configuration schema for controls used in a dashboard."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from dashboard_compiler.shared.config import BaseCfgModel

type ControlTypes = RangeSliderControl | OptionsListControl | TimeSliderControl


class ControlSettings(BaseCfgModel):
    """Settings for controls in a dashboard, defining their behavior and appearance."""

    label_position: Literal['inline', 'above'] | None = Field(default=None)
    """The position of the control label, either 'inline' or 'above'. Defaults to 'inline' if not set."""

    apply_global_filters: bool | None = Field(default=None)
    """Whether to apply global filters to the control. Defaults to true if not set."""

    apply_global_timerange: bool | None = Field(default=None)
    """Whether to apply the global time range to the control. Defaults to true if not set."""

    ignore_zero_results: bool | None = Field(default=None)
    """Whether to ignore controls that return zero results. Defaults to true if not set."""

    chain_controls: bool | None = Field(default=None)
    """Whether to chain controls together, allowing one control's selection to filter the next. Defaults to true if not set."""

    click_to_apply: bool | None = Field(default=None)
    """Whether to require users to click the apply button before applying changes. Defaults to false if not set."""


class BaseControl(BaseCfgModel):
    """Base class for defining controls within the YAML schema.

    These controls are used to filter data or adjust visualization settings
    on a dashboard.
    """

    id: str | None = Field(default=None)
    """A unique identifier for the control. If not provided, one may be generated."""

    width: Literal['small', 'medium', 'large'] | None = Field(default=None)
    """The width of the control in the dashboard layout. If not set, defaults to 'medium'."""

    label: str | None = Field(default=None)
    """The display label for the control. If not provided, a label may be inferred."""


class MatchTechnique(StrEnum):
    """Enumeration for match techniques used in options list controls."""

    PREFIX = 'prefix'
    """Match technique that filters options starting with the input text."""

    CONTAINS = 'contains'
    """Match technique that filters options containing the input text."""

    EXACT = 'exact'
    """Match technique that filters options matching the input text exactly."""


class OptionsListControl(BaseControl):
    """Represents an Options List control.

    This control allows users to select one or more values from a list
    to filter data.
    """

    type: Literal['options'] = 'options'

    field: str = Field(...)
    """The name of the field within the data view that the control is associated with."""

    fill_width: bool = Field(default=False)
    """If true, the control will automatically adjust its width to fill available space."""

    match_technique: MatchTechnique | None = Field(default=None, strict=False)  # strict=False for enum coercion
    """The search technique used for filtering options (e.g., 'prefix', 'contains', 'exact')."""

    wait_for_results: bool = Field(default=False)
    """If set to true, delay the display of the list of values until the results are fully loaded."""

    preselected: list[str] = Field(default_factory=list)
    """A list of options that are preselected when the control is initialized."""

    singular: bool = Field(default=False)
    """If true, the control allows only a single selection from the options list."""

    data_view: str = Field(...)
    """The ID or title of the data view (index pattern) the control operates on."""


class RangeSliderControl(BaseControl):
    """Represents a Range Slider control.

    This control allows users to select a range of numeric or date values
    to filter data.
    """

    type: Literal['range'] = 'range'

    fill_width: bool = Field(default=False)
    """If true, the control will automatically adjust its width to fill available space."""

    field: str = Field(...)
    """The name of the field within the data view that the control is associated with."""

    step: int | float | None = Field(default=None)
    """The step value for the range, defining the granularity of selections."""

    data_view: str = Field(...)
    """The ID or title of the data view (index pattern) the control operates on."""


class TimeSliderControl(BaseControl):
    """Represents a Range Slider control.

    This control allows users to select a range of numeric or date values
    to filter data.
    """

    type: Literal['time'] = 'time'

    start_offset: float | None = Field(default=None, ge=0, le=1)
    """The start offset for the time range as a %, defining the beginning of the selection."""

    end_offset: float | None = Field(default=None, ge=0, le=1)
    """The end offset for the time range as a %, defining the end of the selection."""

    @model_validator(mode='after')
    def validate_offsets(self) -> Self:
        """Ensure that start_offset is less than end_offset."""
        if self.start_offset is not None and self.end_offset is not None and self.start_offset > self.end_offset:
            msg = 'start_offset must be less than end_offset'
            raise ValueError(msg)

        return self
