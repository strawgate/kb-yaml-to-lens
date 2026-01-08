"""View models for Kibana controls used in dashboards."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import Field, field_serializer

from dashboard_compiler.shared.model import BaseModel
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone, RootDict

# The following is an example of the JSON structure that these models represent. Do not remove:
# "controlGroupInput": {                                <-- KbnControlGroupInput
#     "chainingSystem": "HIERARCHICAL",
#     "controlStyle": "oneLine",
#     "ignoreParentSettingsJSON": {
#         "ignoreFilters": false,
#         "ignoreQuery": false,
#         "ignoreTimerange": false,
#         "ignoreValidations": false
#     },
#     "panelsJSON": {                                   <-- KbnControlPanelsJson -- this needs to end up as stringified JSON
#         "0086b299-caf9-4d42-a574-31eec9226a48": {     <-- KbnOptionsListControl
#             "grow": false,
#             "order": 0,
#             "type": "optionsListControl",
#             "width": "medium",
#             "explicitInput": {                        <-- KbnOptionsListControlExplicitInput
#                 "dataViewId": "metrics-*",
#                 "fieldName": "host.architecture",
#                 "searchTechnique": "prefix",
#                 "selectedOptions": [],
#                 "sort": {                             <-- KbnControlSort
#                     "by": "_count",
#                     "direction": "desc"
#                 }
#             }
#         },
#         "4094a542-c799-47ba-9d20-e1ad557924f6": {     <-- KbnRangeSliderControl
#             "grow": false,
#             "order": 1,
#             "type": "rangeSliderControl",
#             "width": "medium",
#             "explicitInput": {                        <-- KbnRangeSliderControlExplicitInput
#                 "dataViewId": "metrics-*",
#                 "fieldName": "severity_number",
#                 "step": 1
#             }
#         }
#     },
#     "showApplySelections": false
# },

KBN_DEFAULT_CONTROL_WIDTH = 'medium'
KBN_DEFAULT_SEARCH_TECHNIQUE = 'prefix'


class KbnControlSort(BaseVwModel):
    """Sorting configuration for options in a control."""

    by: str = Field(...)
    """The field by which to sort the options."""

    direction: Literal['asc', 'desc'] = Field(...)
    """The direction of the sort, either 'asc' or 'desc'."""


class KbnBaseControlExplicitInput(BaseVwModel):
    """Base class for the `explicitInput` part of Kbn controls."""

    id: str = Field(...)
    """The unique identifier for the control."""


class SearchTechnique(str, Enum):
    """Enumeration for Search techniques used in options list controls."""

    PREFIX = 'prefix'
    """Search technique that filters options starting with the input text."""

    WILDCARD = 'wildcard'
    """Search technique that filters options containing the input text."""

    EXACT = 'exact'
    """Search technique that filters options matching the input text exactly."""


class KbnOptionsListControlExplicitInput(KbnBaseControlExplicitInput):
    """Explicit input for options list controls."""

    dataViewId: str = Field(...)
    """The ID of the data view (index pattern) the control operates on."""

    fieldName: str = Field(...)
    """The name of the field within the data view that the control is associated with."""

    title: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The label for the control."""

    searchTechnique: SearchTechnique = Field(...)
    """The search technique used for filtering options."""

    selectedOptions: Annotated[list[str], OmitIfNone()] = Field(...)
    """A list of options that are preselected when the control is initialized."""

    singleSelect: Annotated[bool | None, OmitIfNone()] = Field(...)

    sort: KbnControlSort = Field(...)
    """Sorting configuration for the options in the control."""

    runPastTimeout: Annotated[bool | None, OmitIfNone()] = Field(...)
    """If set to true, delay the display of the list of values until the results are fully loaded."""


class KbnRangeSliderControlExplicitInput(KbnBaseControlExplicitInput):
    """Explicit input for range slider controls."""

    dataViewId: str = Field(...)
    """The ID of the data view (index pattern) the control operates on."""

    fieldName: str = Field(...)
    """The name of the field within the data view that the control is associated with."""

    title: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The label for the control."""

    step: int | float | None = Field(...)
    """The step size for the range slider, if applicable. If not set, defaults to 1."""


class KbnBaseControl(BaseVwModel):
    """Base class for Kibana controls."""

    grow: bool = Field(...)
    """If true, the control will expand to fill available space."""

    order: int = Field(...)
    """The order of the control in the dashboard layout."""

    width: Literal['small', 'medium', 'large'] = Field(...)
    """The width of the control in the dashboard layout, e.g., 'small', 'medium', 'large'."""


class KbnRangeSliderControl(KbnBaseControl):
    """Range slider control for a Kibana Dashboard."""

    type: Literal['rangeSliderControl'] = Field(default='rangeSliderControl')

    explicitInput: KbnRangeSliderControlExplicitInput = Field(...)
    """The actual definition of the slider control."""


class KbnOptionsListControl(KbnBaseControl):
    """Options list control for a Kibana Dashboard."""

    type: Literal['optionsListControl'] = Field(default='optionsListControl')

    explicitInput: KbnOptionsListControlExplicitInput
    """The actual definition of the options list control."""


class KbnTimeSliderControlExplicitInput(KbnBaseControlExplicitInput):
    """Explicit input for time slider controls."""

    timesliceStartAsPercentageOfTimeRange: float = Field(...)
    """The start of the timeslice as a percentage of the total time range."""

    timesliceEndAsPercentageOfTimeRange: float = Field(...)
    """The end of the timeslice as a percentage of the total time range."""


class KbnTimeSliderControl(KbnBaseControl):
    """Time slider control for a Kibana Dashboard."""

    type: Literal['timeSlider'] = Field(default='timeSlider')

    explicitInput: KbnTimeSliderControlExplicitInput = Field(...)
    """The actual definition of the time slider control."""


class KbnESQLControlExplicitInput(KbnBaseControlExplicitInput):
    """Explicit input for ES|QL controls."""

    variableName: str = Field(...)
    """The name of the ES|QL variable."""

    variableType: str = Field(...)
    """The type of variable ('time_literal', 'fields', 'values', 'multi_values', 'functions')."""

    esqlQuery: str = Field(...)
    """The ES|QL query string."""

    controlType: str = Field(...)
    """The control type ('STATIC_VALUES' or 'VALUES_FROM_QUERY')."""

    title: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """Display title for the control."""

    selectedOptions: list[str] = Field(default_factory=list)
    """Currently selected options."""

    singleSelect: Annotated[bool | None, OmitIfNone()] = Field(default=None)
    """Whether to allow only single selection."""

    availableOptions: Annotated[list[str] | None, OmitIfNone()] = Field(default=None)
    """For STATIC_VALUES controls, the list of available options."""


class KbnESQLControl(KbnBaseControl):
    """ES|QL control for a Kibana Dashboard."""

    type: Literal['esqlControl'] = Field(default='esqlControl')

    explicitInput: KbnESQLControlExplicitInput = Field(...)
    """The actual definition of the ES|QL control."""


class KbnIgnoreParentSettingsJson(BaseVwModel):
    """Settings that control whether to ignore inherited values from the dashboard."""

    ignoreFilters: bool = Field(...)
    ignoreQuery: bool = Field(...)
    ignoreTimerange: bool = Field(...)
    ignoreValidations: bool = Field(...)


type KbnControlTypes = KbnRangeSliderControl | KbnOptionsListControl | KbnTimeSliderControl | KbnESQLControl


class KbnControlPanelsJson(RootDict[KbnControlTypes]):
    """A dictionary mapping control IDs to their respective control configurations."""


class ControlStyleEnum(str, Enum):
    """Enumeration for control styles in Kibana dashboards."""

    ONE_LINE = 'oneLine'
    """Control style where controls are displayed in a single line."""

    TWO_LINE = 'twoLine'
    """Control style where controls are displayed in two lines."""


class ChainingSystemEnum(str, Enum):
    """Enumeration for chaining systems in Kibana dashboards."""

    HIERARCHICAL = 'HIERARCHICAL'
    """Chaining system where controls filter the values of other controls."""

    NONE = 'NONE'
    """No chaining system applied to the controls."""


class KbnControlGroupInput(BaseModel):
    """Definition for the Controls part of a Kibana Dashboard."""

    chainingSystem: ChainingSystemEnum = Field(...)
    """The chaining system applied to the controls, e.g., 'HIERARCHICAL' or 'NONE'."""

    controlStyle: ControlStyleEnum = Field(...)
    """The style of the controls, e.g., 'oneLine' or 'twoLine'."""

    ignoreParentSettingsJSON: KbnIgnoreParentSettingsJson
    panelsJSON: KbnControlPanelsJson
    showApplySelections: bool

    @field_serializer('ignoreParentSettingsJSON', when_used='always')
    def serialize_parent_settings_json(self, value: KbnIgnoreParentSettingsJson) -> str:
        """Serialize the ignoreParentSettingsJSON field to a stringified JSON.

        Args:
            value (KbnIgnoreParentSettingsJson): The ignore parent settings JSON to serialize.

        Returns:
            str: The stringified JSON representation of the ignore parent settings.

        """
        return value.model_dump_json()

    @field_serializer('panelsJSON', when_used='always')
    def serialize_panels_json(self, value: KbnControlPanelsJson) -> str:
        """Serialize the panelsJSON field to a stringified JSON.

        Args:
            value (KbnControlPanelsJson): The control panels JSON to serialize.

        Returns:
            str: The stringified JSON representation of the control panels.

        """
        return value.model_dump_json()
