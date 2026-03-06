"""Compilation logic for gauge chart visualizations."""

from typing import TYPE_CHECKING

from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_metric
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric, ESQLMetricTypes, ESQLStaticValue
from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
from kb_dashboard_core.panels.charts.gauge.config import (
    ESQLGaugeChart,
    GaugeAppearance,
    GaugeColorStop,
    GaugePalette,
    LensGaugeChart,
)
from kb_dashboard_core.panels.charts.gauge.view import (
    KbnGaugeColorStop,
    KbnGaugePalette,
    KbnGaugePaletteParams,
    KbnGaugeVisualizationState,
)
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.lens.metrics.config import LensStaticValue
from kb_dashboard_core.queries.config import ESQLQuery
from kb_dashboard_core.shared.compile import normalize_static_metric

if TYPE_CHECKING:
    from kb_dashboard_core.panels.charts.lens.columns.view import KbnLensColumnTypes


def _format_esql_numeric(value: int | float) -> str:
    """Format a numeric value for inclusion in ESQL ``EVAL`` clauses."""
    return str(value) if isinstance(value, int) else repr(value)


def _compile_gauge_color_stops(stops: list[GaugeColorStop]) -> list[KbnGaugeColorStop]:
    """Compile gauge color stops from config to view model."""
    return [KbnGaugeColorStop(color=stop.color, stop=stop.stop) for stop in stops]


def _derive_lower_bound_color_stops(
    upper_stops: list[KbnGaugeColorStop],
    range_min: int | float | None,
) -> list[KbnGaugeColorStop]:
    """Derive ``colorStops`` from upper-bound ``stops``.

    Kibana expects both upper-bound ``stops`` and lower-bound ``colorStops`` for custom
    palettes. If lower-bound stops are omitted in YAML, derive them by shifting each
    band boundary.
    """
    if len(upper_stops) == 0:
        return []

    lower_bound = 0 if range_min is None else range_min
    derived = [KbnGaugeColorStop(color=upper_stops[0].color, stop=lower_bound)]

    for idx in range(1, len(upper_stops)):
        prev_stop = upper_stops[idx - 1]
        curr_stop = upper_stops[idx]
        derived.append(KbnGaugeColorStop(color=curr_stop.color, stop=prev_stop.stop))

    return derived


def _compile_gauge_palette(
    appearance: GaugeAppearance | None,
    color_mode: str | None,
) -> KbnGaugePalette | None:
    """Compile gauge palette configuration.

    When ``color_mode`` is ``palette`` but no explicit palette is provided, emit Kibana's
    built-in ``status`` palette for sensible default red/yellow/green banding.
    """
    if color_mode != 'palette':
        return None

    palette_cfg: GaugePalette | None = appearance.palette if appearance is not None else None
    if palette_cfg is None:
        return KbnGaugePalette(
            type='palette',
            name='status',
            params=KbnGaugePaletteParams(
                name='status',
                reverse=False,
                rangeType='percent',
                rangeMin=0,
                rangeMax=100,
                continuity='above',
                steps=4,
                maxSteps=5,
                stops=[],
                colorStops=[],
            ),
        )

    stops = _compile_gauge_color_stops(palette_cfg.stops) if palette_cfg.stops is not None else None
    color_stops = _compile_gauge_color_stops(palette_cfg.color_stops) if palette_cfg.color_stops is not None else None

    if color_stops is None and stops is not None:
        color_stops = _derive_lower_bound_color_stops(stops, palette_cfg.range_min)

    params = KbnGaugePaletteParams(
        name=palette_cfg.name,
        reverse=palette_cfg.reverse,
        rangeType=palette_cfg.range_type,
        continuity=palette_cfg.continuity,
        progression=palette_cfg.progression,
        rangeMin=palette_cfg.range_min,
        rangeMax=palette_cfg.range_max,
        stops=stops,
        colorStops=color_stops,
        steps=palette_cfg.steps,
        maxSteps=palette_cfg.max_steps,
    )
    params_model: KbnGaugePaletteParams | None = params if len(params.model_dump(exclude_none=True)) > 0 else None

    return KbnGaugePalette(
        type=palette_cfg.type,
        name=palette_cfg.name,
        params=params_model,
    )


def _esql_static_to_metric_column(metric: ESQLStaticValue, role: str) -> tuple[ESQLMetric, str]:
    """Convert ESQL static gauge value to a generated ESQL field plus EVAL assignment."""
    field_name = f'__kb_gauge_{role}_{metric.get_id().replace("-", "_")}'
    label = metric.label if metric.label is not None else str(metric.value)
    return (
        ESQLMetric(
            id=metric.get_id(),
            field=field_name,
            label=label,
        ),
        f'{field_name} = {_format_esql_numeric(metric.value)}',
    )


def prepare_esql_gauge_chart(
    esql_gauge_chart: ESQLGaugeChart,
    query: ESQLQuery | None = None,
) -> tuple[ESQLGaugeChart, ESQLQuery | None]:
    """Rewrite static ESQL gauge values into query-backed fields.

    Kibana's text-based datasource does not support literal static value columns. Static
    values for metric/min/max/goal are converted into generated fields via an appended
    ``EVAL`` clause so that all gauge accessors reference actual query output columns.
    """
    updates: dict[str, object] = {}
    eval_assignments: list[str] = []

    normalized_metric = normalize_static_metric(esql_gauge_chart.metric, ESQLStaticValue)
    if isinstance(normalized_metric, ESQLStaticValue):
        metric_column, eval_assignment = _esql_static_to_metric_column(normalized_metric, role='metric')
        updates['metric'] = metric_column
        eval_assignments.append(eval_assignment)

    def _rewrite_optional_metric(
        value: ESQLMetricTypes | int | float | None,
        role: str,
    ) -> ESQLMetric | None:
        if value is None:
            return None
        normalized = normalize_static_metric(value, ESQLStaticValue)
        if isinstance(normalized, ESQLStaticValue):
            metric_column, eval_assignment = _esql_static_to_metric_column(normalized, role=role)
            eval_assignments.append(eval_assignment)
            return metric_column
        return normalized

    minimum_metric = _rewrite_optional_metric(esql_gauge_chart.minimum, role='min')
    if minimum_metric is not None:
        updates['minimum'] = minimum_metric

    maximum_metric = _rewrite_optional_metric(esql_gauge_chart.maximum, role='max')
    if maximum_metric is not None:
        updates['maximum'] = maximum_metric

    goal_metric = _rewrite_optional_metric(esql_gauge_chart.goal, role='goal')
    if goal_metric is not None:
        updates['goal'] = goal_metric

    if len(updates) == 0 and len(eval_assignments) == 0:
        return esql_gauge_chart, query

    prepared_chart = esql_gauge_chart.model_copy(update=updates) if len(updates) > 0 else esql_gauge_chart

    if query is None or len(eval_assignments) == 0:
        return prepared_chart, query

    prepared_query = ESQLQuery(root=f'{query.root}\n| EVAL {", ".join(eval_assignments)}')
    return prepared_chart, prepared_query


def compile_gauge_chart_visualization_state(  # noqa: PLR0913
    layer_id: str,
    metric_id: str,
    chart: LensGaugeChart | ESQLGaugeChart,
    min_id: str | None = None,
    max_id: str | None = None,
    goal_id: str | None = None,
) -> KbnGaugeVisualizationState:
    """Compile a gauge chart config object into a Kibana Lens Gauge visualization state.

    Args:
        layer_id (str): The ID of the layer.
        metric_id (str): The ID of the primary metric.
        chart (LensGaugeChart | ESQLGaugeChart): The gauge chart config object.
        min_id (str | None): The ID of the minimum value metric.
        max_id (str | None): The ID of the maximum value metric.
        goal_id (str | None): The ID of the goal metric.

    Returns:
        KbnGaugeVisualizationState: The compiled visualization state.

    """
    # Extract appearance settings with defaults
    appearance = chart.appearance
    shape = appearance.shape if appearance is not None and appearance.shape is not None else 'arc'
    ticks_position = appearance.ticks_position if appearance is not None and appearance.ticks_position is not None else 'auto'
    label_major = appearance.label_major if appearance is not None else None
    label_minor = appearance.label_minor if appearance is not None else None
    color_mode = appearance.color_mode if appearance is not None else None
    palette = _compile_gauge_palette(appearance, color_mode)

    label_major_mode = 'custom' if label_major is not None else 'auto'

    return KbnGaugeVisualizationState(
        layerId=layer_id,
        metricAccessor=metric_id,
        minAccessor=min_id,
        maxAccessor=max_id,
        goalAccessor=goal_id,
        shape=shape,
        ticksPosition=ticks_position,
        labelMajor=label_major,
        labelMinor=label_minor,
        labelMajorMode=label_major_mode,
        colorMode=color_mode,
        palette=palette,
    )


def compile_lens_gauge_chart(
    lens_gauge_chart: LensGaugeChart,
) -> tuple[str, dict[str, 'KbnLensColumnTypes'], KbnGaugeVisualizationState]:
    """Compile a LensGaugeChart config object into a Kibana Lens Gauge visualization state.

    Args:
        lens_gauge_chart (LensGaugeChart): The LensGaugeChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnGaugeVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnGaugeVisualizationState): The compiled visualization state.

    """
    metric_id: str
    min_id: str | None = None
    max_id: str | None = None
    goal_id: str | None = None

    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {}

    # Compile primary metric
    result = compile_lens_metric(lens_gauge_chart.metric)
    metric_id = result.primary_id
    metric_column = result.primary_column
    kbn_columns_by_id[metric_id] = metric_column
    kbn_columns_by_id.update(result.helper_columns)

    # Compile optional min/max/goal - handle both static values and metrics
    if lens_gauge_chart.minimum is not None:
        minimum_metric = normalize_static_metric(lens_gauge_chart.minimum, LensStaticValue)
        min_result = compile_lens_metric(minimum_metric)
        min_id = min_result.primary_id
        min_column = min_result.primary_column
        kbn_columns_by_id[min_id] = min_column
        kbn_columns_by_id.update(min_result.helper_columns)

    if lens_gauge_chart.maximum is not None:
        maximum_metric = normalize_static_metric(lens_gauge_chart.maximum, LensStaticValue)
        max_result = compile_lens_metric(maximum_metric)
        max_id = max_result.primary_id
        max_column = max_result.primary_column
        kbn_columns_by_id[max_id] = max_column
        kbn_columns_by_id.update(max_result.helper_columns)

    if lens_gauge_chart.goal is not None:
        goal_metric = normalize_static_metric(lens_gauge_chart.goal, LensStaticValue)
        goal_result = compile_lens_metric(goal_metric)
        goal_id = goal_result.primary_id
        goal_column = goal_result.primary_column
        kbn_columns_by_id[goal_id] = goal_column
        kbn_columns_by_id.update(goal_result.helper_columns)

    layer_id = lens_gauge_chart.get_id()

    return (
        layer_id,
        kbn_columns_by_id,
        compile_gauge_chart_visualization_state(
            layer_id=layer_id,
            metric_id=metric_id,
            chart=lens_gauge_chart,
            min_id=min_id,
            max_id=max_id,
            goal_id=goal_id,
        ),
    )


def compile_esql_gauge_chart(
    esql_gauge_chart: ESQLGaugeChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnGaugeVisualizationState]:
    """Compile an ESQL GaugeChart config object into a Kibana Lens Gauge visualization state.

    Args:
        esql_gauge_chart (ESQLGaugeChart): The ESQLGaugeChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnGaugeVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnGaugeVisualizationState): The compiled visualization state.

    """
    kbn_columns: list[KbnESQLColumnTypes] = []

    # Compile primary metric
    metric_column = compile_esql_metric(esql_gauge_chart.metric)
    metric_id: str = metric_column.columnId
    kbn_columns.append(metric_column)

    layer_id = esql_gauge_chart.get_id()

    # Compile optional min/max/goal - handle both static values and metrics
    min_id: str | None = None
    if esql_gauge_chart.minimum is not None:
        minimum_metric = normalize_static_metric(esql_gauge_chart.minimum, ESQLStaticValue)
        min_column = compile_esql_metric(minimum_metric)
        min_id = min_column.columnId
        kbn_columns.append(min_column)

    max_id: str | None = None
    if esql_gauge_chart.maximum is not None:
        maximum_metric = normalize_static_metric(esql_gauge_chart.maximum, ESQLStaticValue)
        max_column = compile_esql_metric(maximum_metric)
        max_id = max_column.columnId
        kbn_columns.append(max_column)

    goal_id: str | None = None
    if esql_gauge_chart.goal is not None:
        goal_metric = normalize_static_metric(esql_gauge_chart.goal, ESQLStaticValue)
        goal_column = compile_esql_metric(goal_metric)
        goal_id = goal_column.columnId
        kbn_columns.append(goal_column)

    return (
        layer_id,
        kbn_columns,
        compile_gauge_chart_visualization_state(
            layer_id=layer_id,
            metric_id=metric_id,
            chart=esql_gauge_chart,
            min_id=min_id,
            max_id=max_id,
            goal_id=goal_id,
        ),
    )
