"""Permissive raw Pydantic models for parsing Kibana saved-object JSON."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class KbnRawBase(BaseModel):
    """Base permissive model for raw Kibana payload fragments."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)


class KbnReference(KbnRawBase):
    """Raw reference item from saved-object references arrays."""

    name: str | None = None
    type: str | None = None
    id: str | None = None


class KbnGridData(KbnRawBase):
    """Raw panel grid-data object."""

    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None
    section_id: str | None = Field(default=None, alias='sectionId')


class KbnVisualizationLayer(KbnRawBase):
    """Raw visualization layer object containing accessor ids."""

    layer_id: str | None = Field(default=None, alias='layerId')
    accessors: list[object] | None = None
    x_accessor: str | None = Field(default=None, alias='xAccessor')
    split_accessor: str | None = Field(default=None, alias='splitAccessor')


class KbnVisualization(KbnRawBase):
    """Raw visualization block from lens state."""

    preferred_series_type: str | None = Field(default=None, alias='preferredSeriesType')
    shape: str | None = None
    layer_id: str | None = Field(default=None, alias='layerId')
    metric_accessor: str | None = Field(default=None, alias='metricAccessor')
    secondary_accessor: str | None = Field(default=None, alias='secondaryAccessor')
    accessor: str | None = None
    accessors: list[object] | None = None
    layers: list[KbnVisualizationLayer] | None = None


class KbnState(KbnRawBase):
    """Raw panel state block containing query, datasource, and visualization."""

    visualization: KbnVisualization | None = None
    datasource_states: dict[str, Any] | None = Field(default=None, alias='datasourceStates')
    query: dict[str, Any] | None = None


class KbnEmbeddableAttributes(KbnRawBase):
    """Raw embeddable attributes block."""

    state: KbnState | None = None
    visualization_type: str | None = Field(default=None, alias='visualizationType')
    references: list[KbnReference | object] | None = None


class KbnSavedVis(KbnRawBase):
    """Raw saved visualization metadata from visualization panels."""

    type: str | None = None


class KbnEmbeddableConfig(KbnRawBase):
    """Raw embeddable config block for a panel."""

    title: str | None = None
    attributes: KbnEmbeddableAttributes | None = None
    references: list[KbnReference | object] | None = None
    saved_vis: KbnSavedVis | None = Field(default=None, alias='savedVis')


class KbnPanel(KbnRawBase):
    """Raw dashboard panel object."""

    panel_index: str | None = Field(default=None, alias='panelIndex')
    title: str | None = None
    type: str | None = None
    grid_data: KbnGridData | None = Field(default=None, alias='gridData')
    embeddable_config: KbnEmbeddableConfig | None = Field(default=None, alias='embeddableConfig')


class KbnDashboardAttributes(KbnRawBase):
    """Raw dashboard attributes object."""

    title: str | None = None
    description: str | None = None
    time_from: str | None = Field(default=None, alias='timeFrom')
    time_to: str | None = Field(default=None, alias='timeTo')
    options_json: str | dict[str, Any] | list[Any] | None = Field(default=None, alias='optionsJSON')
    panels_json: str | dict[str, Any] | list[Any] | None = Field(default=None, alias='panelsJSON')
    kibana_saved_object_meta: dict[str, Any] | None = Field(default=None, alias='kibanaSavedObjectMeta')
    control_group_input: dict[str, Any] | None = Field(default=None, alias='controlGroupInput')


class KbnDashboard(KbnRawBase):
    """Raw saved dashboard object envelope."""

    id: str | None = None
    attributes: KbnDashboardAttributes | None = None
    references: list[KbnReference | object] | None = None
