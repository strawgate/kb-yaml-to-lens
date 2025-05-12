from typing import Annotated, Any, Literal

from pydantic import Field

from dashboard_compiler.panels.charts.view import KbnBaseStateVisualization, KbnLayerColorMapping
from dashboard_compiler.shared.view import BaseVwModel, OmitIfNone


class LabelsOrientationConfig(BaseVwModel):
    x: float | None = None
    yLeft: float | None = None
    yRight: float | None = None


class YAxisMode(BaseVwModel):
    # Define fields based on actual Kibana structure if needed, using object for now
    name: str  # Added name field based on usage in compile logic


class AxisConfig(BaseVwModel):
    # Define fields based on actual Kibana structure if needed, using object for now
    pass


class YConfig(BaseVwModel):
    forAccessor: str
    color: str | None = None
    icon: str | None = None
    lineWidth: float | None = None
    lineStyle: Any | None = None
    fill: Any | None = None
    iconPosition: Any | None = None
    textVisibility: bool | None = None
    axisMode: YAxisMode | None = None


class XYDataLayerConfig(BaseVwModel):
    layerId: str
    accessors: list[str]
    layerType: Literal['data']
    seriesType: str
    xAccessor: str | None = None
    position: Literal['top'] | None = None
    showGridlines: bool
    simpleView: Annotated[bool | None, OmitIfNone()] = None
    yConfig: Annotated[list[YConfig] | None, OmitIfNone()] = None
    splitAccessor: str | None = None
    palette: Annotated[Any | None, OmitIfNone()] = None
    collapseFn: Annotated[Literal['sum', 'avg', 'min', 'max'] | None, OmitIfNone()] = None
    xScaleType: Annotated[Any | None, OmitIfNone()] = None
    isHistogram: Annotated[bool | None, OmitIfNone()] = None
    columnToLabel: Annotated[str | None, OmitIfNone()] = None
    colorMapping: KbnLayerColorMapping | None = None


class XYReferenceLineLayerConfig(BaseVwModel):
    layerId: str
    accessors: list[str]
    yConfig: list[YConfig] | None = None
    layerType: Literal['referenceLine']


class XYAnnotationLayerConfigCachedMetadata(BaseVwModel):
    title: str
    description: str
    tags: list[str]


class XYByValueAnnotationLayerConfig(BaseVwModel):
    layerId: str
    layerType: Literal['annotations']
    annotations: list[Any]
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None


class XYByReferenceAnnotationLayerConfig(BaseVwModel):
    layerId: str
    layerType: Literal['annotations']
    annotations: list[Any]
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None
    annotationGroupId: str
    __lastSaved: Any  # type: ignore


# Subclass Kbnfor XY visualizations state (JSON structure)
class KbnXYVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for XY charts (bar, line, area) in the Kibana JSON structure."""

    preferredSeriesType: str | None = None
    legend: Any
    valueLabels: Literal['hide', 'show'] | None = None
    fittingFunction: Any | None = None
    emphasizeFitting: bool | None = None
    endValue: Any | None = None
    xExtent: Any | None = None
    yLeftExtent: Any | None = None
    yRightExtent: Any | None = None
    layers: list[XYDataLayerConfig | XYReferenceLineLayerConfig | XYByValueAnnotationLayerConfig | XYByReferenceAnnotationLayerConfig] = (
        Field(default_factory=list)
    )
    xTitle: str | None = None
    yTitle: str | None = None
    yRightTitle: str | None = None
    yLeftScale: Any | None = None
    yRightScale: Any | None = None
    axisTitlesVisibilitySettings: Any | None = None
    tickLabelsVisibilitySettings: Any | None = None
    gridlinesVisibilitySettings: Any | None = None
    labelsOrientation: LabelsOrientationConfig | None = None
    curveType: Any | None = None
    fillOpacity: float | None = None
    minBarHeight: float | None = None
    hideEndzones: bool | None = None
    showCurrentTimeMarker: bool | None = None


# Note: ValidLayer is not di
