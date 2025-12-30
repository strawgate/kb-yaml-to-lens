import json

from pydantic import BaseModel, Field, field_serializer

from dashboard_compiler.controls.view import KbnControlGroupInput
from dashboard_compiler.panels.view import KbnBasePanel, KbnSavedObjectMeta
from dashboard_compiler.shared.view import KbnReference


class KbnDashboardOptions(BaseModel):
    """Represents the global options for a Kibana dashboard."""

    useMargins: bool
    """Whether to put space between panels in the dashboard."""
    syncColors: bool
    """Applies the same color palette to all panels on the dashboard."""
    syncCursor: bool
    'When you hover your cursor over a time series chart or a heatmap, the cursor on all other related dashboard charts appears.'
    syncTooltips: bool
    'When you hover your cursor over a Lens chart, the tooltips on all other related dashboard charts automatically appear.'
    hidePanelTitles: bool
    'Displays the titles in the panel headers'


class KbnDashboardAttributes(BaseModel):
    title: str
    description: str
    panelsJSON: list[KbnBasePanel]
    optionsJSON: KbnDashboardOptions
    kibanaSavedObjectMeta: KbnSavedObjectMeta
    timeRestore: bool
    version: int
    controlGroupInput: KbnControlGroupInput | None = None

    @field_serializer('panelsJSON', when_used='always')
    def panels_json_stringified(self, panelsJSON: list[KbnBasePanel]) -> str:
        """Kibana wants this field to be stringified JSON."""
        panels_json = [panel.model_dump() for panel in panelsJSON]
        return json.dumps(panels_json)

    @field_serializer('optionsJSON', when_used='always')
    def options_json_stringified(self, optionsJSON: KbnDashboardOptions) -> str:
        """Kibana wants this field to be stringified JSON."""
        return optionsJSON.model_dump_json(by_alias=True)


class KbnDashboard(BaseModel):
    """Represents the top-level Kibana dashboard JSON structure."""

    attributes: KbnDashboardAttributes
    coreMigrationVersion: str
    created_at: str
    created_by: str
    id: str
    managed: bool
    references: list[KbnReference] = Field(default_factory=list)
    type: str
    typeMigrationVersion: str
    updated_at: str
    updated_by: str
    version: str
