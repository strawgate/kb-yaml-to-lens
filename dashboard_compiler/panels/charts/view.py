from typing import Any, Literal

from pydantic import Field

from dashboard_compiler.filters.view import KbnFilter
from dashboard_compiler.panels.charts.visualizations.view import KbnBaseStateVisualization, KbnDataSourceState, KbnVisualizationTypeEnum
from dashboard_compiler.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.view import BaseVwModel, KbnReference


class KbnLensPanelState(BaseVwModel):
    """Represents the 'state' object within a Lens panel in the Kibana JSON structure."""

    visualization: KbnBaseStateVisualization
    query: KbnQuery = Field(...)
    filters: list[KbnFilter] = Field(...)
    datasourceStates: KbnDataSourceState = Field(...)
    internalReferences: list[Any] = Field(...)
    adHocDataViews: dict[str, Any] = Field(...)


class KbnLensPanelAttributes(BaseVwModel):
    title: str = ''
    visualizationType: KbnVisualizationTypeEnum
    type: Literal['lens'] = 'lens'
    references: list[KbnReference] = Field(...)
    state: KbnLensPanelState


class KbnLensPanelEmbeddableConfig(KbnBasePanelEmbeddableConfig):
    attributes: KbnLensPanelAttributes


class KbnLensPanel(KbnBasePanel):
    type: Literal['lens'] = 'lens'
    embeddableConfig: KbnLensPanelEmbeddableConfig
