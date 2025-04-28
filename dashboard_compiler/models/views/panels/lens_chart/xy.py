# ignore: N815
from typing import Any, Literal

from pydantic import BaseModel, Field

from dashboard_compiler.models.views.panels.lens import KbnBaseStateVisualization

# Define nested models based on reference/transpiled/lens/public/visualizations/xy/types.py

type SeriesType = Literal["line", "bar", "area", "area_stacked", "bar_stacked", "area_percentage_stacked", "bar_percentage_stacked"]


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
    lineStyle: Any | None = None  # Use Any for now, refine if needed
    fill: Any | None = None  # Use Any for now, refine if needed
    iconPosition: Any | None = None  # Use Any for now, refine if needed
    textVisibility: bool | None = None
    axisMode: YAxisMode | None = None


class XYDataLayerConfig(BaseModel):  # Renamed from KbnXYVisualizationLayer
    layerId: str
    accessors: list[str]
    layerType: Literal["data"]
    seriesType: SeriesType
    xAccessor: str | None = None
    simpleView: bool | None = None
    yConfig: list[YConfig] | None = None
    splitAccessor: str | None = None
    palette: Any | None = None  # Use Any for now, refine if needed
    collapseFn: Literal["sum"] | Literal["avg"] | Literal["min"] | Literal["max"] | None = None
    xScaleType: Any | None = None  # Use Any for now, refine if needed
    isHistogram: bool | None = None
    columnToLabel: str | None = None
    colorMapping: Any | None = None  # Use Any for now, refine if needed


class XYReferenceLineLayerConfig(BaseModel):
    layerId: str
    accessors: list[str]
    yConfig: list[YConfig] | None = None
    layerType: Literal["referenceLine"]


class XYAnnotationLayerConfigCachedMetadata(BaseModel):
    title: str
    description: str
    tags: list[str]


class XYByValueAnnotationLayerConfig(BaseModel):
    layerId: str
    layerType: Literal["annotations"]
    annotations: list[Any]  # Use Any for now, refine if needed
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None


class XYByReferenceAnnotationLayerConfig(BaseModel):
    layerId: str
    layerType: Literal["annotations"]
    annotations: list[Any]  # Use Any for now, refine if needed
    indexPatternId: str
    ignoreGlobalFilters: bool
    cachedMetadata: XYAnnotationLayerConfigCachedMetadata | None = None
    annotationGroupId: str
    __lastSaved: Any  # Use Any for now, refine if needed


class ValidXYDataLayerConfig(BaseModel):
    xAccessor: str
    layerId: str
    accessors: list[str]
    layerType: Literal["data"]
    seriesType: SeriesType
    simpleView: bool | None = None
    yConfig: list[YConfig] | None = None
    splitAccessor: str | None = None
    palette: Any | None = None  # Use Any for now, refine if needed
    collapseFn: Literal["sum"] | Literal["avg"] | Literal["min"] | Literal["max"] | None = None
    xScaleType: Any | None = None  # Use Any for now, refine if needed
    isHistogram: bool | None = None
    columnToLabel: str | None = None
    colorMapping: Any | None = None  # Use Any for now, refine if needed


# Subclass Kbnfor XY visualizations state (JSON structure)
class KbnXYVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for XY charts (bar, line, area) in the Kibana JSON structure."""

    preferredSeriesType: SeriesType | None = None
    legend: Any  # Use Any for now, refine if needed
    valueLabels: Literal["hide"] | Literal["show"] | None = None
    fittingFunction: Any | None = None  # Use Any for now, refine if needed
    emphasizeFitting: bool | None = None
    endValue: Any | None = None  # Use Any for now, refine if needed
    xExtent: Any | None = None  # Use Any for now, refine if needed
    yLeftExtent: Any | None = None  # Use Any for now, refine if needed
    yRightExtent: Any | None = None  # Use Any for now, refine if needed
    layers: list[XYDataLayerConfig | XYReferenceLineLayerConfig | XYByValueAnnotationLayerConfig, XYByReferenceAnnotationLayerConfig] = (
        Field(default_factory=list)
    )
    xTitle: str | None = None
    yTitle: str | None = None
    yRightTitle: str | None = None
    yLeftScale: Any | None = None  # Use Any for now, refine if needed
    yRightScale: Any | None = None  # Use Any for now, refine if needed
    axisTitlesVisibilitySettings: Any | None = None  # Use Any for now, refine if needed
    tickLabelsVisibilitySettings: Any | None = None  # Use Any for now, refine if needed
    gridlinesVisibilitySettings: Any | None = None  # Use Any for now, refine if needed
    labelsOrientation: LabelsOrientationConfig | None = None
    curveType: Any | None = None  # Use Any for now, refine if needed
    fillOpacity: float | None = None
    minBarHeight: float | None = None
    hideEndzones: bool | None = None
    showCurrentTimeMarker: bool | None = None


# Note: ValidLayer is not directly used in the main State model, so not included here for now.
