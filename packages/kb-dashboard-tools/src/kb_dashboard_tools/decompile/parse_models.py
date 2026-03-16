"""Typed intermediate structures for decompiler parse phase."""

from dataclasses import dataclass, field
from typing import Any

from kb_dashboard_core.controls.view import (
    KbnESQLControl,
    KbnOptionsListControl,
    KbnRangeSliderControl,
    KbnTimeSliderControl,
)
from kb_dashboard_core.dashboard.view import KbnDashboardOptions
from kb_dashboard_core.filters.view import KbnFilter
from kb_dashboard_core.panels.charts.datatable.view import KbnDatatableVisualizationState
from kb_dashboard_core.panels.charts.gauge.view import KbnGaugeVisualizationState
from kb_dashboard_core.panels.charts.heatmap.view import KbnHeatmapVisualizationState
from kb_dashboard_core.panels.charts.metric.view import KbnESQLMetricVisualizationState, KbnMetricVisualizationState
from kb_dashboard_core.panels.charts.mosaic.view import KbnMosaicVisualizationState
from kb_dashboard_core.panels.charts.pie.view import KbnPieVisualizationState
from kb_dashboard_core.panels.charts.tagcloud.view import KbnTagcloudVisualizationState
from kb_dashboard_core.panels.charts.waffle.view import KbnWaffleVisualizationState
from kb_dashboard_core.panels.charts.xy.view import KbnXYVisualizationState
from kb_dashboard_core.panels.images.view import KbnImagePanel
from kb_dashboard_core.panels.links.view import KbnLinksPanel
from kb_dashboard_core.panels.markdown.view import KbnMarkdownPanel
from kb_dashboard_core.panels.search.view import KbnSearchPanel
from kb_dashboard_core.panels.vega.view import KbnVegaPanel

type VisualizationViewModel = (
    KbnXYVisualizationState
    | KbnGaugeVisualizationState
    | KbnHeatmapVisualizationState
    | KbnDatatableVisualizationState
    | KbnTagcloudVisualizationState
    | KbnMetricVisualizationState
    | KbnESQLMetricVisualizationState
    | KbnPieVisualizationState
    | KbnMosaicVisualizationState
    | KbnWaffleVisualizationState
)

type SimplePanelViewModel = KbnSearchPanel | KbnLinksPanel | KbnImagePanel | KbnVegaPanel | KbnMarkdownPanel

type ControlViewModel = KbnOptionsListControl | KbnRangeSliderControl | KbnTimeSliderControl | KbnESQLControl


@dataclass
class ParsedReference:
    """A resolved reference from the dashboard references array."""

    name: str
    ref_type: str
    ref_id: str


@dataclass
class ParsedGridData:
    """Parsed panel grid layout."""

    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None
    section_id: str | None = None


@dataclass
class ParsedColumn:
    """A single parsed datasource column (form-based)."""

    column_id: str
    operation_type: str
    source_field: str | None = None
    label: str | None = None
    custom_label: bool = False
    is_bucketed: bool = False
    data_type: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    filter_query: str | None = None
    filter_language: str | None = None


@dataclass
class ParsedESQLColumn:
    """A single parsed ES|QL column."""

    column_id: str
    field_name: str
    label: str | None = None
    custom_label: bool = False
    meta_type: str | None = None


@dataclass
class ParsedFormLayer:
    """A parsed form-based datasource layer."""

    layer_id: str
    columns: dict[str, ParsedColumn] = field(default_factory=dict)
    column_order: list[str] = field(default_factory=list)
    index_pattern_id: str | None = None


@dataclass
class ParsedESQLLayer:
    """A parsed ES|QL datasource layer."""

    layer_id: str
    query: str
    columns: list[ParsedESQLColumn] = field(default_factory=list)
    time_field: str = '@timestamp'


@dataclass
class ParsedVisualizationLayerRole:
    """Accessor roles for a single visualization layer."""

    layer_id: str
    metric_ids: list[str] = field(default_factory=list)
    dimension_id: str | None = None
    breakdown_id: str | None = None
    accessors: list[str] = field(default_factory=list)


@dataclass
class ParsedVisualizationState:
    """Parsed visualization state with resolved chart type."""

    raw_type: str | None = None
    preferred_series_type: str | None = None
    shape: str | None = None
    layer_roles: dict[str, ParsedVisualizationLayerRole] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    view_model: VisualizationViewModel | None = None


@dataclass
class ParsedLensPanel:
    """A fully parsed Lens/ES|QL panel ready for inference."""

    panel_type: str  # 'lens' or 'esql'
    visualization_type: str | None = None
    visualization_state: ParsedVisualizationState | None = None
    form_layers: dict[str, ParsedFormLayer] = field(default_factory=dict)
    esql_layers: dict[str, ParsedESQLLayer] = field(default_factory=dict)
    data_view_id: str | None = None
    esql_query: str | None = None
    references: list[ParsedReference] = field(default_factory=list)
    view_visualization: VisualizationViewModel | None = None


@dataclass
class ParsedSimplePanel:
    """A parsed non-chart panel (markdown, search, links, image, vega)."""

    panel_type: str
    raw: dict[str, Any] = field(default_factory=dict)
    embeddable_config: dict[str, Any] = field(default_factory=dict)
    embeddable_attributes: dict[str, Any] = field(default_factory=dict)
    view_panel: SimplePanelViewModel | None = None


@dataclass
class ParsedPanel:
    """Wrapper around all parsed panel types."""

    panel_index: str | None = None
    title: str = ''
    grid: ParsedGridData | None = None
    hide_title: bool | None = None
    description: str | None = None

    lens: ParsedLensPanel | None = None
    simple: ParsedSimplePanel | None = None
    error: str | None = None


@dataclass
class ParsedDashboardSettings:
    """Parsed dashboard-level settings."""

    margins: bool | None = None
    sync_colors: bool | None = None
    sync_cursor: bool | None = None
    sync_tooltips: bool | None = None
    hide_panel_titles: bool | None = None
    view_options: KbnDashboardOptions | None = None


@dataclass
class ParsedFilter:
    """A parsed dashboard-level filter."""

    raw: dict[str, Any]
    meta: dict[str, Any]
    key: str
    filter_type: str | None = None
    view_filter: KbnFilter | None = None


@dataclass
class ParsedControl:
    """A parsed dashboard control."""

    raw: dict[str, Any]
    control_type: str | None = None
    field_name: str | None = None
    title: str | None = None
    data_view_id: str | None = None
    view_control: ControlViewModel | None = None


@dataclass
class ParsedDashboard:
    """Top-level parsed dashboard."""

    dashboard_id: str | None = None
    title: str = 'Untitled Dashboard'
    description: str | None = None
    time_from: str | None = None
    time_to: str | None = None
    settings: ParsedDashboardSettings | None = None
    query: dict[str, str] | None = None
    filters: list[ParsedFilter] = field(default_factory=list)
    controls: list[ParsedControl] = field(default_factory=list)
    panels: list[ParsedPanel] = field(default_factory=list)
    reference_lookup: dict[str, str] = field(default_factory=dict)
