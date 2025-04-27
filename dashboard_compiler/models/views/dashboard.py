import json

from pydantic import BaseModel, Field, field_serializer

# Import view panel models
from dashboard_compiler.models.views.base import KbnBasePanel, KbnSavedObjectMeta
from dashboard_compiler.models.views.panels.controls import KbnControlGroupInput  # Controls are special
from dashboard_compiler.models.views.panels.lens import KbnReference  # For top-level references


class KbnDashboardOptions(BaseModel):
    useMargins: bool
    syncColors: bool
    syncCursor: bool
    syncTooltips: bool
    hidePanelTitles: bool

    # def from_dashboard(cls, dashboard: Dashboard):
    #     """Create options from a dashboard object."""
    #     return cls(
    #         useMargins=True,
    #         syncColors=True,
    #         syncCursor=True,
    #         syncTooltips=True,
    #         hidePanelTitles=True,
    #     )


# Define nested models for Dashboard attributes based on samples
class KbnDashboardAttributes(BaseModel):
    title: str
    description: str
    panelsJSON: list[KbnBasePanel]
    optionsJSON: KbnDashboardOptions
    kibanaSavedObjectMeta: KbnSavedObjectMeta
    timeRestore: bool
    version: int
    controlGroupInput: KbnControlGroupInput | None = None

    @field_serializer("panelsJSON", when_used="always")
    def panels_json_stringified(self, panelsJSON: list[KbnBasePanel]):
        """Kibana wants this field to be stringified JSON."""
        panels_json = [panel.model_dump(serialize_as_any=True, exclude_none=True) for panel in panelsJSON]
        return json.dumps(panels_json)

    @field_serializer("optionsJSON", when_used="always")
    def options_json_stringified(self, optionsJSON: KbnDashboardOptions):
        """Kibana wants this field to be stringified JSON."""
        return json.dumps(optionsJSON.model_dump(serialize_as_any=True, exclude_none=True))

    # def from_dashboard(cls, dashboard: Dashboard):
    #     """Create options from a dashboard object."""
    #     return cls(
    #         title=dashboard.title,
    #         description=dashboard.description,
    #         panelsJSON=KbnBasePanel.from_panels(dashboard.panels),
    #         optionsJSON=KbnDashboardOptions.from_dashboard(dashboard),
    #         timeRestore=False,
    #         version=1,
    #         controlGroupInput=None,
    #     )


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

    # def from_dashboard(cls, dashboard: Dashboard,):
    #     """Create a KbnDashboard from a Dashboard object."""
    #     return cls(
    #         attributes=KbnDashboardAttributes.from_dashboard(dashboard),
    #         coreMigrationVersion="8.0.0",
    #         created_at="2023-10-01T00:00:00Z",
    #         created_by="admin",
    #         id=dashboard.id,
    #         managed=False,
    #         references=[],
    #         type="dashboard",
    #         typeMigrationVersion="8.0.0",
    #         updated_at="2023-10-01T00:00:00Z",
    #         updated_by="admin",
    #         version="WzEwLDFd",
    #     )
