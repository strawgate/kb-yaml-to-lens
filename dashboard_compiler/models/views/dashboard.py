from pydantic import BaseModel, Field
from typing import List, Optional

# Import view panel models
from dashboard_compiler.models.views.base import KbnBasePanel
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
    kibanaSavedObjectMeta: dict = {"searchSourceJSON": '{"filter":[],"query":{"query":"","language":"kuery"}}'}
    timeRestore: bool
    version: int
    controlGroupInput: Optional[KbnControlGroupInput] = None

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
    references: List[KbnReference] = Field(default_factory=list)
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
