"""Configuration schema for controls used in a dashboard."""

from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from dashboard_compiler.controls.types import ESQLVariableType
from dashboard_compiler.shared.config import BaseCfgModel, BaseIdentifiableModel


def validate_default_in_choices(default: str | list[str] | None, choices: list[str] | None) -> None:
    """Validate that all default values exist in choices.

    Args:
        default (str | list[str] | None): The default value(s) to validate.
        choices (list[str] | None): The available choices to validate against.

    Raises:
        ValueError: If any default value is not in choices.

    """
    if default is None or choices is None:
        return
    default_list = [default] if isinstance(default, str) else default
    invalid = [v for v in default_list if v not in choices]
    if len(invalid) > 0:
        msg = f'default contains options not in choices: {invalid}'
        raise ValueError(msg)


type ControlTypes = (
    RangeSliderControl
    | OptionsListControl
    | TimeSliderControl
    | ESQLFieldControl
    | ESQLFunctionControl
    | ESQLStaticSingleSelectControl
    | ESQLStaticMultiSelectControl
    | ESQLQuerySingleSelectControl
    | ESQLQueryMultiSelectControl
)


class ControlSettings(BaseCfgModel):
    """Global settings for dashboard controls."""

    label_position: Literal['inline', 'above'] | None = Field(default=None)
    """Label position. Defaults to 'inline'."""

    apply_global_filters: bool | None = Field(default=None)
    """Apply dashboard filters to controls. Defaults to true."""

    apply_global_timerange: bool | None = Field(default=None)
    """Apply dashboard time range to controls. Defaults to true."""

    ignore_zero_results: bool | None = Field(default=None)
    """Hide controls with no matching values. Defaults to true."""

    chain_controls: bool | None = Field(default=None)
    """Chain controls (selections filter subsequent controls). Defaults to true."""

    click_to_apply: bool | None = Field(default=None)
    """Require apply button click. Defaults to false."""


class BaseControl(BaseIdentifiableModel):
    """Base class for dashboard controls."""

    width: Literal['small', 'medium', 'large'] | None = Field(default=None)
    """Control width. Defaults to 'medium'."""

    label: str | None = Field(default=None)
    """Display label."""


class MatchTechnique(StrEnum):
    """Search match techniques for options list."""

    PREFIX = 'prefix'
    CONTAINS = 'contains'
    EXACT = 'exact'


class OptionsListControl(BaseControl):
    """Dropdown control for selecting field values."""

    type: Literal['options'] = 'options'

    field: str = Field(...)
    """Field to get values from."""

    fill_width: bool = Field(default=False)
    """Expand to fill available width."""

    match_technique: MatchTechnique | None = Field(default=None, strict=False)  # strict=False for enum coercion
    """Search technique (prefix, contains, exact)."""

    wait_for_results: bool | None = Field(default=None)
    """Delay display until results load."""

    preselected: list[str] = Field(default_factory=list)
    """Initially selected values."""

    multiple: bool | None = Field(default=None)
    """Allow multiple selection."""

    data_view: str = Field(...)
    """Data view for this control."""


class RangeSliderControl(BaseControl):
    """Slider control for selecting a numeric range."""

    type: Literal['range'] = 'range'

    fill_width: bool = Field(default=False)
    """Expand to fill available width."""

    field: str = Field(...)
    """Numeric field for the range."""

    step: int | float | None = Field(default=None)
    """Step increment for the slider."""

    data_view: str = Field(...)
    """Data view for this control."""


class TimeSliderControl(BaseControl):
    """Slider control for selecting a time window within the dashboard time range."""

    type: Literal['time'] = 'time'

    start_offset: float | None = Field(default=None, ge=0, le=1)
    """Start position as fraction (0.0-1.0) of dashboard time range."""

    end_offset: float | None = Field(default=None, ge=0, le=1)
    """End position as fraction (0.0-1.0) of dashboard time range."""

    @model_validator(mode='after')
    def validate_offsets(self) -> Self:
        """Ensure that start_offset is less than end_offset."""
        if self.start_offset is not None and self.end_offset is not None and self.start_offset >= self.end_offset:
            msg = 'start_offset must be less than end_offset'
            raise ValueError(msg)

        return self


class ESQLFieldControl(BaseControl):
    """ES|QL control for field selection (static choices)."""

    type: Literal['esql'] = 'esql'
    variable_name: str = Field(...)
    """Variable name (referenced as ??variable_name in queries)."""

    variable_type: Literal[ESQLVariableType.FIELDS] = Field(default=ESQLVariableType.FIELDS)

    choices: list[str] = Field(...)
    """Available field choices."""

    default: str | None = Field(default=None)
    """Default selection."""

    @model_validator(mode='after')
    def validate_default(self) -> Self:
        """Validate that default value exists in choices."""
        validate_default_in_choices(self.default, self.choices)
        return self


class ESQLFunctionControl(BaseControl):
    """ES|QL control for function selection (static choices)."""

    type: Literal['esql'] = 'esql'
    variable_name: str = Field(...)
    """Variable name (referenced as ??variable_name in queries)."""

    variable_type: Literal[ESQLVariableType.FUNCTIONS] = Field(default=ESQLVariableType.FUNCTIONS)

    choices: list[str] = Field(...)
    """Available function choices."""

    default: str | None = Field(default=None)
    """Default selection."""

    @model_validator(mode='after')
    def validate_default(self) -> Self:
        """Validate that default value exists in choices."""
        validate_default_in_choices(self.default, self.choices)
        return self


class ESQLStaticSingleSelectControl(BaseControl):
    """ES|QL control for single value selection (static choices)."""

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """Variable name (referenced as ?variable_name in queries)."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)

    choices: list[str] = Field(...)
    """Available value choices."""

    default: str | None = Field(default=None)
    """Default selection."""

    multiple: Literal[False] | None = Field(default=None)

    @model_validator(mode='after')
    def validate_defaults(self) -> Self:
        """Validate that default value exists in choices."""
        if self.default is not None and self.default not in self.choices:
            msg = f'default contains options not in choices: {{{self.default}}}'
            raise ValueError(msg)
        return self


class ESQLStaticMultiSelectControl(BaseControl):
    """ES|QL control for multiple value selection (static choices)."""

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """Variable name (referenced as ?variable_name in queries)."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)

    choices: list[str] = Field(...)
    """Available value choices."""

    default: list[str] | None = Field(default=None)
    """Default selections."""

    multiple: Literal[True] = Field(default=True)

    @model_validator(mode='after')
    def validate_defaults(self) -> Self:
        """Validate that default values exist in choices."""
        if self.default is not None:
            invalid = set(self.default) - set(self.choices)
            if len(invalid) > 0:
                msg = f'default contains options not in choices: {invalid}'
                raise ValueError(msg)
        return self


class ESQLQuerySingleSelectControl(BaseControl):
    """ES|QL control for single value selection (query-driven choices)."""

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """Variable name (referenced as ?variable_name in queries)."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)

    query: str = Field(..., min_length=1)
    """ES|QL query returning available values (must return single column)."""

    multiple: Literal[False] | None = Field(default=None)

    default: str | None = Field(default=None)
    """Default selection."""


class ESQLQueryMultiSelectControl(BaseControl):
    """ES|QL control for multiple value selection (query-driven choices)."""

    type: Literal['esql'] = 'esql'

    variable_name: str = Field(...)
    """Variable name (referenced as ?variable_name in queries)."""

    variable_type: ESQLVariableType = Field(default=ESQLVariableType.VALUES, strict=False)

    query: str = Field(..., min_length=1)
    """ES|QL query returning available values (must return single column)."""

    multiple: Literal[True] = Field(default=True)

    default: list[str] | None = Field(default=None)
    """Default selections."""
