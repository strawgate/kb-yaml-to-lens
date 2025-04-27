import json
from typing import Any

from pydantic import BaseModel, Field, field_serializer

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
    selectedOptions: list[Any] = Field(default_factory=list)
    sort: KbnControlSort | None = None


class KbnRangeSliderControlExplicitInput(KbnBaseControlExplicitInput):
    step: int | float


class KbnControl(BaseModel):
    grow: bool
    order: int
    type: str  # e.g., "optionsListControl", "rangeSliderControl"
    width: str
    explicitInput: KbnOptionsListControlExplicitInput | KbnRangeSliderControlExplicitInput


# Note: The Controls panel itself in the JSON sample doesn't follow the standard KbnBasePanel structure.
# The controls are defined within controlGroupInput.panelsJSON at the dashboard level.
# This model represents the structure found within that panelsJSON string.
# The top-level dashboard view model will need to include JsonControlGroupInput.
# This might require revisiting the KbnBasePanel definition or how Controls are handled.
# For now, we define the structure found within panelsJSON.

# This model represents the dictionary within controlGroupInput.panelsJSON
KbnControlPanelsJson = dict[str, KbnControl]


# This model represents the controlGroupInput object at the dashboard attributes level
class KbnControlGroupInput(BaseModel):
    chainingSystem: str
    controlStyle: str
    ignoreParentSettingsJSON: str
    panelsJSON: KbnControlPanelsJson
    showApplySelections: bool

    @field_serializer("panelsJSON", when_used="always")
    def panels_json_stringified(self, panelsJSON: KbnControlPanelsJson):
        """Kibana wants this field to be stringified JSON."""
        panels_json = {panel_key: panel.model_dump(serialize_as_any=True, exclude_none=True) for panel_key, panel in panelsJSON.items()}
        return json.dumps(panels_json)


# We won't define a JsonControlsPanel inheriting from KbnBasePanel directly
# because the JSON structure doesn't match the standard panel format.
# The compilation process will need to build JsonControlGroupInput and
# serialize KbnControlPanelsJson.

# No to_json or to_dict methods here - these models are for representing JSON output
