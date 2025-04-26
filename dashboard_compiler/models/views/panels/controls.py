from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

# Model Relationships:
# - KbnControlGroupInput
#   - key: KbnControl
#     - kbnRangeSliderControlExplicitInput
#   - key: KbnControl
#     - kbnOptionsListControlExplicitInput


class KbnControlSort(BaseModel):
    by: str
    direction: str


class KbnBaseControlExplicitInput(BaseModel):
    dataViewId: str
    fieldName: str


class KbnOptionsListControlExplicitInput(KbnBaseControlExplicitInput):
    searchTechnique: str
    selectedOptions: List[Any] = Field(default_factory=list)
    sort: Optional[KbnControlSort] = None


class KbnRangeSliderControlExplicitInput(KbnBaseControlExplicitInput):
    step: int | float


KbnControlExplicitInput = Union[KbnOptionsListControlExplicitInput, KbnRangeSliderControlExplicitInput]


class KbnControl(BaseModel):
    grow: bool
    order: int
    type: str  # e.g., "optionsListControl", "rangeSliderControl"
    width: str
    explicitInput: KbnControlExplicitInput


# Note: The Controls panel itself in the JSON sample doesn't follow the standard KbnBasePanel structure.
# The controls are defined within controlGroupInput.panelsJSON at the dashboard level.
# This model represents the structure found within that panelsJSON string.
# The top-level dashboard view model will need to include JsonControlGroupInput.
# This might require revisiting the KbnBasePanel definition or how Controls are handled.
# For now, we define the structure found within panelsJSON.

# This model represents the dictionary within controlGroupInput.panelsJSON
KbnControlPanelsJson = Dict[str, KbnControl]


# This model represents the controlGroupInput object at the dashboard attributes level
class KbnControlGroupInput(BaseModel):
    chainingSystem: str
    controlStyle: str
    ignoreParentSettingsJSON: str
    panelsJSON: KbnControlPanelsJson
    showApplySelections: bool


# We won't define a JsonControlsPanel inheriting from KbnBasePanel directly
# because the JSON structure doesn't match the standard panel format.
# The compilation process will need to build JsonControlGroupInput and
# serialize KbnControlPanelsJson.

# No to_json or to_dict methods here - these models are for representing JSON output
