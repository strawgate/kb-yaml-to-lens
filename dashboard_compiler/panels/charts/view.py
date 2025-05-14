from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import Field, RootModel

from dashboard_compiler.filters.view import KbnFilter
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
from dashboard_compiler.panels.view import KbnBasePanel, KbnBasePanelEmbeddableConfig
from dashboard_compiler.queries.view import KbnESQLQuery, KbnQuery
from dashboard_compiler.shared.view import BaseVwModel, KbnReference, OmitIfNone
 
if TYPE_CHECKING:
    from .metric.view import KbnMetricVisualizationState
    from .pie.view import KbnPieVisualizationState
    from .xy.view import KbnXYVisualizationState

type KbnVisualizationStateTypes = KbnPieVisualizationState | KbnMetricVisualizationState | KbnXYVisualizationState

# region Form Data Source
## Form Based
# "formBased": {                                                <--- KbnFormBasedDataSourceState
#     "layers": {                                               <--- KbnFormBasedDataSourceStateById
#         "b38fc34e-2df5-41a4-913b-e3e182998ef4": {             <--- KbnFormBasedDataSourceStateLayer
#             "columns": {
#                 "c4ea489f-9a04-4120-b9ec-aaa7a3a2d865": {     <--- dict[str, KbnLensColumnTypes]
#                     ...
#                 },
#             },
#             "columnOrder": [
#                 "44777308-3ea7-4f72-86bf-b4defdf71a0c",
#             ],
#             "sampling": 1,
#             "ignoreGlobalFilters": false,
#             "incompleteColumns": {},
#             "indexPatternId": "27a3148b-d1d4-4455-8acf-e63c94071a5b"
#         }
#     },
#     "currentIndexPatternId": "27a3148b-d1d4-4455-8acf-e63c94071a5b"
# },


class KbnFormBasedDataSourceStateLayer(BaseVwModel):
    """Represents the datasource state for a single layer within a Lens panel in the Kibana JSON structure."""

    columns: dict[str, KbnLensColumnTypes] = Field(default_factory=dict)
    columnOrder: list[str] = Field(default_factory=list)
    incompleteColumns: dict[str, Any] = Field(default_factory=dict)
    sampling: int
    indexPatternId: Annotated[str | None, OmitIfNone()] = None


class KbnFormBasedDataSourceStateLayerById(RootModel):
    """Represents a mapping of layer IDs to their corresponding KbnLayerDataSourceState objects."""

    root: dict[str, KbnFormBasedDataSourceStateLayer] = Field(default_factory=dict)


class KbnFormBasedDataSourceState(BaseVwModel):
    """Represents the datasource state for a Lens panel in the Kibana JSON structure."""

    layers: KbnFormBasedDataSourceStateLayerById = Field(default_factory=KbnFormBasedDataSourceStateLayerById)
    currentIndexPatternId: Annotated[str | None, OmitIfNone()] = None


# endregion Form Data Source

# region Text Data Source
# "textBased": {                                                          <--- KbnTextBasedDataSourceState
#     "layers": {                                                         <--- KbnTextBasedDataSourceStateLayerById
#         "42607131-7dd7-4935-a1eb-c9bed5cd302c": {                       <--- KbnTextBasedDataSourceStateLayer
#             "index": "d3b7e528216ce7ef6....",
#             "query": {                                                  <--- KbnESQLQuery
#                 "esql": "FROM metrics-* | ..."
#             },
#             "columns": [                                                <--- list[KbnESQLColumnTypes]
#                 {
#                     "columnId": "0e4107a7-db0d-4a80-a2e6-f528bc71e9f3",
#                     "fieldName": "agent.name"
#                 },
#                 {
#                     "columnId": "ae78ca1b-bad2-47b3-aaaf-ecd8aa05761c",
#                     "fieldName": "count(*)"
#                 }
#             ]
#         }
#     },
#     "indexPatternRefs": [                                            <--- list[KbnIndexPatternRef]
#         {
#             "id": ".....",
#             "title": "metrics-*",
#             "timeField": "@timestamp"
#         }
#     ]
# }


class KbnTextBasedDataSourceStateLayer(BaseVwModel):
    # index: str
    query: KbnESQLQuery
    columns: list[KbnESQLColumnTypes]


class KbnTextBasedDataSourceStateLayerById(RootModel):
    root: dict[str, KbnTextBasedDataSourceStateLayer] = Field(default_factory=dict)


class KbnIndexPatternRef(BaseVwModel):
    id: str
    title: str
    timeField: str


class KbnTextBasedDataSourceState(BaseVwModel):
    layers: KbnTextBasedDataSourceStateLayerById | None = Field(default=None)
    indexPatternRefs: Annotated[list[KbnIndexPatternRef] | None, OmitIfNone()] = None


# endregion Text Data Source

# region Index Pattern


class KbnIndexPatternBasedDataSourceStateById(RootModel):
    root: dict[str, str] = Field(default_factory=dict)


class KbnIndexPatternBasedDataSourceState(BaseVwModel):
    """Index Pattern based datasource is not yet implemented."""

    layers: KbnIndexPatternBasedDataSourceStateById = Field(default_factory=KbnIndexPatternBasedDataSourceStateById)


# endregion Index Pattern


# region DataSourceState
class KbnDataSourceState(BaseVwModel):
    """Represents the overall datasource states for a Lens panel in the Kibana JSON structure."""

    formBased: KbnFormBasedDataSourceState = Field(
        default_factory=KbnFormBasedDataSourceState,
    )  # Structure: formBased -> layers -> {layerId: KbnFormBasedDataSourceStateLayer}
    indexpattern: KbnIndexPatternBasedDataSourceState = Field(
        default_factory=KbnIndexPatternBasedDataSourceState,
    )  # Structure: indexpattern -> layers -> {layerId: KbnIndexPatternBasedDataSourceStateLayer}
    # not implemented
    textBased: KbnTextBasedDataSourceState = Field(
        default_factory=KbnTextBasedDataSourceState,
    )  # Structure: textBased -> layers -> {layerId: KbnTextBasedDataSourceStateLayer}


# endregion DataSourceState


# region Color Mapping
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


# endregion Color Mapping

# region Visualization


# syncColors: bool = Field(
#     default=False,
#     description="(Optional) Whether to sync colors across visualizations. Defaults to False.",
# )
# syncCursor: bool = Field(
#     default=True,
#     description="(Optional) Whether to sync cursor across visualizations. Defaults to True.",
# )
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


class KbnLensPanelState(BaseVwModel):
    """Represents the 'state' object within a Lens panel in the Kibana JSON structure."""

    visualization: KbnBaseStateVisualization
    query: KbnQuery | KbnESQLQuery = Field(...)
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
    
    syncTooltips: bool = Field(
        default=False,
        description="(Optional) Whether to sync tooltips across visualizations. Defaults to False.",
    )

    syncColors: bool = Field(
        default=False,
        description="(Optional) Whether to sync colors across visualizations. Defaults to False.",
    )

    syncCursor: bool = Field(
        default=True,
        description="(Optional) Whether to sync cursor across visualizations. Defaults to True.",
    )

    filters: list = Field(
        default_factory=list,
        description="(Optional) List of filters applied to the Lens visualization. Defaults to empty list.",
    )

    query: KbnQuery = Field(
        ...,
        description="(Optional) Query object for the Lens visualization. Defaults to empty query with 'kuery' language.",
    )


class KbnLensPanel(KbnBasePanel):
    type: Literal['lens'] = 'lens'
    embeddableConfig: KbnLensPanelEmbeddableConfig

