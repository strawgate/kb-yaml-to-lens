from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Any, Literal

from dashboard_compiler.panels.charts.view import KbnBaseStateVisualization, KbnLayerColorMapping



class SeriesTypeEnum(StrEnum):
    line = 'line'
    bar = 'bar'
    area = 'area'
    area_stacked = 'area_stacked'
    bar_stacked = 'bar_stacked'
    area_percentage_stacked = 'area_percentage_stacked'
    bar_percentage_stacked = 'bar_percentage_stacked'


class LabelsOrientationConfig(BaseModel):
    x: float | None = None
    yLeft: float | None = None
    yRight: float | None = None


class YAxisMode(BaseModel):
    # Define fields based on actual Kibana structure if needed, using object for now
    name: str  # Added name field based on usage in compile logic


class AxisConfig(BaseModel):
    # Define fields based on actual Kibana structure if needed, using object for now
    pass


class YConfig(BaseModel):
    forAccessor: str
    color: str | None = None
    icon: str | None = None
    lineWidth: float | None = None
    lineStyle: Any | None = None
    fill: Any | None = None
    iconPosition: Any | None = None
    textVisibility: bool | None = None
    axisMode: YAxisMode | None = None


class XYDataLayerConfig(BaseModel):
    layerId: str
    accessors: list[str]
    layerType: Literal['data']
    seriesType: SeriesTypeEnum
    xAccessor: str | None = None
    simpleView: bool | None = None
    yConfig: list[YConfig] | None = None
    splitAccessor: str | None = None
    palette: Any | None = None
    collapseFn: Literal['sum', 'avg', 'min', 'max'] | None = None
    xScaleType: Any | None = None
    isHistogram: bool | None = None
    columnToLabel: str | None = None
    colorMapping: KbnLayerColorMapping | None = None


class XYReferenceLineLayerConfig(BaseModel):
    layerId: str
    accessors: list[str]
    yConfig: list[YConfig] | None = None
    layerType: Literal['referenceLine']


class XYAnnotationLayerConfigCachedMetadata(BaseModel):
    title: str
    description: str
    tags: list[str]


class XYByValueAnnotationLayerConfig(BaseModel):
    layerId: str
    layerType: Literal['annotations']
    annotations: list[Any]
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None


class XYByReferenceAnnotationLayerConfig(BaseModel):
    layerId: str
    layerType: Literal['annotations']
    annotations: list[Any]
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None
    annotationGroupId: str
    __lastSaved: Any # type: ignore


# Subclass Kbnfor XY visualizations state (JSON structure)
class KbnXYVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for XY charts (bar, line, area) in the Kibana JSON structure."""

    preferredSeriesType: SeriesTypeEnum | None = None
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