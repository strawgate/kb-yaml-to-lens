"""Permissive raw Pydantic models for decompiler parse boundaries."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class RawBaseModel(BaseModel):
    """Base permissive model for raw Kibana payload fragments."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow', populate_by_name=True)


class RawReference(RawBaseModel):
    """Raw reference item from saved-object references arrays."""

    name: str | None = None
    type: str | None = None
    id: str | None = None


class RawGridData(RawBaseModel):
    """Raw panel grid-data object."""

    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None
    section_id: str | None = Field(default=None, alias='sectionId')


class RawVisualizationLayer(RawBaseModel):
    """Raw visualization layer object containing accessor ids."""

    layer_id: str | None = Field(default=None, alias='layerId')
    accessors: list[object] | None = None
    x_accessor: str | None = Field(default=None, alias='xAccessor')
    split_accessor: str | None = Field(default=None, alias='splitAccessor')


class RawVisualization(RawBaseModel):
    """Raw visualization block from lens state."""

    preferred_series_type: str | None = Field(default=None, alias='preferredSeriesType')
    shape: str | None = None
    layer_id: str | None = Field(default=None, alias='layerId')
    metric_accessor: str | None = Field(default=None, alias='metricAccessor')
    secondary_accessor: str | None = Field(default=None, alias='secondaryAccessor')
    accessor: str | None = None
    accessors: list[object] | None = None
    layers: list[RawVisualizationLayer] | None = None


class RawState(RawBaseModel):
    """Raw panel state block containing query, datasource, and visualization."""

    visualization: RawVisualization | None = None
    datasource_states: dict[str, Any] | None = Field(default=None, alias='datasourceStates')
    query: dict[str, Any] | None = None


class RawEmbeddableAttributes(RawBaseModel):
    """Raw embeddable attributes block."""

    state: RawState | None = None
    visualization_type: str | None = Field(default=None, alias='visualizationType')
    references: list[RawReference | object] | None = None


class RawSavedVis(RawBaseModel):
    """Raw saved visualization metadata from visualization panels."""

    type: str | None = None


class RawEmbeddableConfig(RawBaseModel):
    """Raw embeddable config block for a panel."""

    title: str | None = None
    attributes: RawEmbeddableAttributes | None = None
    references: list[RawReference | object] | None = None
    saved_vis: RawSavedVis | None = Field(default=None, alias='savedVis')


class RawPanel(RawBaseModel):
    """Raw dashboard panel object."""

    panel_index: str | None = Field(default=None, alias='panelIndex')
    title: str | None = None
    type: str | None = None
    grid_data: RawGridData | None = Field(default=None, alias='gridData')
    embeddable_config: RawEmbeddableConfig | None = Field(default=None, alias='embeddableConfig')


class RawDashboardAttributes(RawBaseModel):
    """Raw dashboard attributes object."""

    title: str | None = None
    description: str | None = None
    time_from: str | None = Field(default=None, alias='timeFrom')
    time_to: str | None = Field(default=None, alias='timeTo')
    options_json: str | dict[str, Any] | list[Any] | None = Field(default=None, alias='optionsJSON')
    panels_json: str | dict[str, Any] | list[Any] | None = Field(default=None, alias='panelsJSON')
    kibana_saved_object_meta: dict[str, Any] | None = Field(default=None, alias='kibanaSavedObjectMeta')
    control_group_input: dict[str, Any] | None = Field(default=None, alias='controlGroupInput')


class RawDashboard(RawBaseModel):
    """Raw saved dashboard object envelope."""

    id: str | None = None
    attributes: RawDashboardAttributes | None = None
    references: list[RawReference | object] | None = None
