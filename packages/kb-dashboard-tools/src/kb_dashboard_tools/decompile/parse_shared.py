"""Shared helpers for decompiler parse modules."""

import json
import logging
from typing import Any, cast

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
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def parse_json_field(raw: str | dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    """Parse a field that may be a JSON string or already-parsed object."""
    if raw is None:
        return None
    if isinstance(raw, str):
        try:
            parsed: dict[str, Any] | list[Any] = json.loads(raw)  # pyright: ignore[reportAny]
        except json.JSONDecodeError:
            logger.warning('Failed to decode JSON field in parse_json_field')
            return None
        return parsed
    return raw


def as_dict(value: object) -> dict[str, Any] | None:
    """Safely cast a value to dict if it is one, otherwise return None."""
    if isinstance(value, dict):
        return value  # pyright: ignore[reportUnknownVariableType]
    return None


def as_list(value: object) -> list[object] | None:
    """Safely cast a value to list if it is one, otherwise return None."""
    if isinstance(value, list):
        return cast('list[object]', value)
    return None


def get_dict(source: dict[str, Any], key: str) -> dict[str, Any] | None:
    """Extract a dict-valued key from a dict source."""
    return as_dict(source.get(key))


def get_list(source: dict[str, Any], key: str) -> list[object] | None:
    """Extract a list-valued key from a dict source."""
    return as_list(source.get(key))


def get_str(source: dict[str, Any], key: str) -> str | None:
    """Extract a string-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, str) else None


def get_int(source: dict[str, Any], key: str) -> int | None:
    """Extract an int-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def get_bool(source: dict[str, Any], key: str) -> bool | None:
    """Extract a bool-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, bool) else None


def get_number(source: dict[str, Any], key: str) -> int | float | None:
    """Extract a numeric (int or float, not bool) key from a dict source."""
    value = source.get(key)
    if isinstance(value, bool):
        return None
    return value if isinstance(value, (int, float)) else None


def validate_view_model(model_cls: type[Any], data: object) -> object | None:
    """Best-effort validation into an existing Kbn* view model."""
    try:
        return model_cls.model_validate(  # pyright: ignore[reportAny]
            data,
            strict=False,
            extra='ignore',
        )
    except ValidationError:
        return None


VISUALIZATION_VIEW_MODEL_MAP: dict[str, type[Any]] = {
    'lnsXY': KbnXYVisualizationState,
    'lnsGauge': KbnGaugeVisualizationState,
    'lnsHeatmap': KbnHeatmapVisualizationState,
    'lnsDatatable': KbnDatatableVisualizationState,
    'lnsTagcloud': KbnTagcloudVisualizationState,
}

SIMPLE_PANEL_VIEW_MODEL_MAP: dict[str, type[Any]] = {
    'search': KbnSearchPanel,
    'links': KbnLinksPanel,
    'image': KbnImagePanel,
    'vega': KbnVegaPanel,
    'markdown': KbnMarkdownPanel,
}


def visualization_model_type(visualization_type: str | None, visualization: dict[str, Any], *, is_esql: bool) -> type[Any] | None:
    """Resolve the target view-model class for a Lens visualization payload."""
    if visualization_type == 'lnsMetric':
        return KbnESQLMetricVisualizationState if is_esql else KbnMetricVisualizationState
    if visualization_type == 'lnsPie':
        shape = visualization.get('shape')
        if shape == 'mosaic':
            return KbnMosaicVisualizationState
        if shape == 'waffle':
            return KbnWaffleVisualizationState
        return KbnPieVisualizationState
    return VISUALIZATION_VIEW_MODEL_MAP.get(visualization_type or '')
