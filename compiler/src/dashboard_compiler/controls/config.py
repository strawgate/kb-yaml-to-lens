"""Configuration schema for controls used in a dashboard."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from dashboard_compiler.controls.types import ESQLVariableType
from dashboard_compiler.shared.config import BaseCfgModel

type ControlTypes = (
    RangeSliderControl
    | OptionsListControl
    | TimeSliderControl
    | ESQLValueControl
    | ESQLFieldControl
    | ESQLStaticSingleSelectControl
    | ESQLStaticMultiSelectControl
    | ESQLQueryControl
)


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

    wait_for_results: bool | None = Field(default=None)
    """If set to true, delay the display of the list of values until the results are fully loaded."""

    preselected: list[str] = Field(default_factory=list)
    """A list of options that are preselected when the control is initialized."""

    singular: bool | None = Field(default=None, deprecated=True)
    """DEPRECATED: Use 'multiple' instead. If true, the control allows only a single selection from the options list."""

    multiple: bool | None = Field(default=None)
    """If false, allows only single selection. If true, allows multiple selections. Takes precedence over 'singular'."""

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
    """Represents a Time Slider control.

    This control allows users to select a time range to filter data
    by adjusting start and end offsets within the global time range.
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


class ESQLValueControl(BaseControl):
    """Represents an ES|QL control for value selection.

    Supports both static values (via choices) and query-driven values (via query).
    Used for VALUES, MULTI_VALUES, and TIME_LITERAL variable types.
    """

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """The name of the ES|QL variable (e.g., 'status_code')."""

    variable_type: Literal[ESQLVariableType.VALUES, ESQLVariableType.MULTI_VALUES, ESQLVariableType.TIME_LITERAL] = Field(
        default=ESQLVariableType.VALUES
    )
    """The type of variable (values, multi_values, or time_literal)."""

    choices: list[str] | None = Field(default=None)
    """The static list of available values. Mutually exclusive with 'query'."""

    query: str | None = Field(default=None, min_length=1)
    """The ES|QL query that returns available values. Mutually exclusive with 'choices'."""

    default: str | list[str] | None = Field(default=None)
    """Default selected value(s). Must be a string for single-select, list for multi-select."""

    multiple: bool | None = Field(default=None)
    """If true, allow multiple selection from the options."""

    @model_validator(mode='after')
    def validate_choices_xor_query(self) -> Self:
        """Ensure that exactly one of choices or query is provided."""
        if self.choices is None and self.query is None:
            msg = "Either 'choices' or 'query' must be provided"
            raise ValueError(msg)

        if self.choices is not None and self.query is not None:
            msg = "Only one of 'choices' or 'query' can be provided, not both"
            raise ValueError(msg)

        return self

    @model_validator(mode='after')
    def validate_defaults(self) -> Self:
        """Validate that default value(s) exist in choices if using static mode."""
        if self.default is None or self.choices is None:
            return self

        # Normalize default to list for validation
        default_values = [self.default] if isinstance(self.default, str) else self.default

        # Check all default values exist in choices
        invalid = set(default_values) - set(self.choices)
        if len(invalid) > 0:
            msg = f'default contains options not in choices: {invalid}'
            raise ValueError(msg)

        return self

    @model_validator(mode='after')
    def validate_default_type_matches_multiple(self) -> Self:
        """Ensure default type matches the multiple setting."""
        if self.default is None:
            return self

        is_list_default = isinstance(self.default, list)
        is_multi_select = self.multiple is True

        if is_list_default and not is_multi_select:
            msg = 'default must be a string when multiple is False or None'
            raise ValueError(msg)

        if not is_list_default and is_multi_select:
            msg = 'default must be a list when multiple is True'
            raise ValueError(msg)

        return self


class ESQLFieldControl(BaseControl):
    """Represents an ES|QL control for field selection.

    Only supports static values (via choices).
    Used for FIELDS and FUNCTIONS variable types.
    """

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """The name of the ES|QL variable (e.g., 'field_name')."""

    variable_type: Literal[ESQLVariableType.FIELDS, ESQLVariableType.FUNCTIONS] = Field(default=ESQLVariableType.FIELDS)
    """The type of variable (fields or functions)."""

    choices: list[str] = Field(...)
    """The static list of available fields or functions."""

    default: str | list[str] | None = Field(default=None)
    """Default selected field(s). Must be a string for single-select, list for multi-select."""

    multiple: bool | None = Field(default=None)
    """If true, allow multiple selection from the options."""

    @model_validator(mode='after')
    def validate_defaults(self) -> Self:
        """Validate that default value(s) exist in choices."""
        if self.default is None:
            return self

        # Normalize default to list for validation
        default_values = [self.default] if isinstance(self.default, str) else self.default

        # Check all default values exist in choices
        invalid = set(default_values) - set(self.choices)
        if len(invalid) > 0:
            msg = f'default contains options not in choices: {invalid}'
            raise ValueError(msg)

        return self

    @model_validator(mode='after')
    def validate_default_type_matches_multiple(self) -> Self:
        """Ensure default type matches the multiple setting."""
        if self.default is None:
            return self

        is_list_default = isinstance(self.default, list)
        is_multi_select = self.multiple is True

        if is_list_default and not is_multi_select:
            msg = 'default must be a string when multiple is False or None'
            raise ValueError(msg)

        if not is_list_default and is_multi_select:
            msg = 'default must be a list when multiple is True'
            raise ValueError(msg)

        return self


class ESQLStaticSingleSelectControl(BaseControl):
    """Represents an ES|QL control with static values for single selection.

    This control allows users to select a single value from a predefined list
    to filter ES|QL visualizations via variables.
    """

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """The name of the ES|QL variable (e.g., 'status_code')."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)
    """The type of variable ('time_literal', 'fields', 'values', 'multi_values', 'functions')."""

    choices: list[str] = Field(...)
    """The static list of available values for this control."""

    default: str | None = Field(default=None)
    """Default selected value."""

    multiple: Literal[False] | None = Field(default=None)
    """If true, allow multiple selection. Must be None or False for this control type."""

    @model_validator(mode='after')
    def validate_defaults(self) -> Self:
        """Validate that default value exists in choices."""
        if self.default is not None and self.default not in self.choices:
            msg = f'default contains options not in choices: {{{self.default}}}'
            raise ValueError(msg)
        return self


class ESQLStaticMultiSelectControl(BaseControl):
    """Represents an ES|QL control with static values for multiple selection.

    This control allows users to select multiple values from a predefined list
    to filter ES|QL visualizations via variables.
    """

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """The name of the ES|QL variable (e.g., 'status_code')."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)
    """The type of variable ('time_literal', 'fields', 'values', 'multi_values', 'functions')."""

    choices: list[str] = Field(...)
    """The static list of available values for this control."""

    default: list[str] | None = Field(default=None)
    """Default selected values."""

    multiple: Literal[True] = Field(default=True)
    """Must be True for this control type."""

    @model_validator(mode='after')
    def validate_defaults(self) -> Self:
        """Validate that default values exist in choices."""
        if self.default is not None:
            invalid = set(self.default) - set(self.choices)
            if len(invalid) > 0:
                msg = f'default contains options not in choices: {invalid}'
                raise ValueError(msg)
        return self


class ESQLQueryControl(BaseControl):
    """Represents an ES|QL control with query-driven values.

    This control dynamically fetches available values from an ES|QL query
    to filter ES|QL visualizations via variables.
    """

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """The name of the ES|QL variable (e.g., 'status_code')."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)
    """The type of variable ('time_literal', 'fields', 'values', 'multi_values', 'functions')."""

    query: str = Field(..., min_length=1)
    """The ES|QL query that returns the available values for this control."""

    multiple: bool | None = Field(default=None)
    """If true, allow multiple selection from the options."""
