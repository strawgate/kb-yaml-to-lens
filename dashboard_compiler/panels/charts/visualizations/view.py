from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Any, TypeVar

from pydantic import Field, RootModel

from dashboard_compiler.panels.charts.columns.view import KbnColumnTypes
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone

if TYPE_CHECKING:
    from .pie.view import KbnPieVisualizationState
    from .metric.view import KbnMetricVisualizationState

type KbnStateVisualizationType = KbnPieVisualizationState | KbnMetricVisualizationState


class KbnLayerDataSourceState(BaseVwModel):
    """Represents the datasource state for a single layer within a Lens panel in the Kibana JSON structure."""

    columns: dict[str, KbnColumnTypes] = Field(default_factory=dict)
    columnOrder: list[str] = Field(default_factory=list)
    incompleteColumns: dict[str, Any] = Field(default_factory=dict)
    sampling: int
    indexPatternId: str | None = None


class KbnLayerDataSourceStateById(RootModel):
    """Represents a mapping of layer IDs to their corresponding KbnLayerDataSourceState objects."""

    root: dict[str, KbnLayerDataSourceState] = Field(default_factory=dict)


class KbnFormBasedDataSourceState(BaseVwModel):
    layers: KbnLayerDataSourceStateById = Field(default_factory=KbnLayerDataSourceStateById)
    currentIndexPatternId: str | None = None


class KbnTextBasedDataSourceState(BaseVwModel):
    layers: KbnLayerDataSourceStateById = Field(default_factory=KbnLayerDataSourceStateById)


class KbnIndexPatternDataSourceState(BaseVwModel):
    layers: KbnLayerDataSourceStateById = Field(default_factory=KbnLayerDataSourceStateById)


class KbnDataSourceState(BaseVwModel):
    """Represents the overall datasource states for a Lens panel in the Kibana JSON structure."""

    formBased: KbnFormBasedDataSourceState = Field(
        default_factory=KbnFormBasedDataSourceState,
    )  # Structure: formBased -> layers -> {layerId: KbnLayerDataSourceState}
    indexpattern: KbnIndexPatternDataSourceState = Field(
        default_factory=KbnIndexPatternDataSourceState,
    )  # Structure: indexpattern -> layers -> {layerId: KbnLayerDataSourceState}
    textBased: KbnTextBasedDataSourceState = Field(
        default_factory=KbnTextBasedDataSourceState,
    )  # Structure: textBased -> layers -> {layerId: KbnLayerDataSourceState}


class KbnLayerColorMappingRule(BaseVwModel):
    type: str = 'other'


class KbnLayerColorMappingColor(BaseVwModel):
    type: str = 'loop'


class KbnLayerColorMappingSpecialAssignment(BaseVwModel):
    rule: KbnLayerColorMappingRule = Field(default_factory=KbnLayerColorMappingRule)
    color: KbnLayerColorMappingColor = Field(default_factory=KbnLayerColorMappingColor)
    touched: bool = False


class KbnLayerColorMapping(BaseVwModel):
    assignments: list[Any] = Field(default_factory=list)
    specialAssignments: list[KbnLayerColorMappingSpecialAssignment] = Field(
        default_factory=lambda: [KbnLayerColorMappingSpecialAssignment()],
    )
    paletteId: str = 'eui_amsterdam_color_blind'
    colorMode: dict[str, str] = Field(default_factory=lambda: {'type': 'categorical'})


class KbnBaseStateVisualizationLayer(BaseVwModel):
    layerId: str
    layerType: str
    colorMapping: Annotated[KbnLayerColorMapping | None, OmitIfNone()] = None

class KbnBaseStateVisualization(BaseVwModel):
    layers: list[KbnBaseStateVisualizationLayer] = Field(...)


class KbnVisualizationTypeEnum(StrEnum):
    XY = 'lnsXY'
    PIE = 'lnsPie'
    METRIC = 'lnsMetric'
    DATATABLE = 'lnsDatatable'


    # syncColors: bool = Field(
    #     default=False,
    #     description="(Optional) Whether to sync colors across visualizations. Defaults to False.",
    # )
    # syncCursor: bool = Field(
    #     default=True,
    #     description="(Optional) Whether to sync cursor across visualizations. Defaults to True.",
    # )
    # syncTooltips: bool = Field(
    #     default=False,
    #     description="(Optional) Whether to sync tooltips across visualizations. Defaults to False.",
    # )
    # filters: list = Field(
    #     default_factory=list,
    #     description="(Optional) List of filters applied to the Lens visualization. Defaults to empty list.",
    # )
    # query: dict[str, Any] = Field(
    #     default_factory=lambda: {"query": "", "language": "kuery"},
    #     description="(Optional) Query object for the Lens visualization. Defaults to empty query with 'kuery' language.",
    # )


