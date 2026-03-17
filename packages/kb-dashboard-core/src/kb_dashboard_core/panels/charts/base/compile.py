"""Compilation utilities for base chart components."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from kb_dashboard_core.panels.charts.base.config import (
    PERCENT_MAX,
    ColorRangeMapping,
    ColorValueMapping,
    LegendVisibleEnum,
    LegendWidthEnum,
)
from kb_dashboard_core.panels.charts.base.view import (
    KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE,
    KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE_COLOR_CODE,
    KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE,
    KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE_MATCH_EXACTLY,
    KBN_DEFAULT_COLOR_MAPPING_TOUCHED,
    KbnLayerColorMapping,
    KbnLayerColorMappingAssignment,
    KbnLayerColorMappingColor,
    KbnLayerColorMappingRule,
    KbnLayerColorMappingSpecialAssignment,
    KbnLegendSize,
    KbnRangePalette,
    KbnRangePaletteParams,
    KbnRangePaletteStop,
)


def map_legend_size(size: LegendWidthEnum | None) -> KbnLegendSize | None:
    """Map YAML legend sizes to Kibana legend sizes."""
    match size:
        case None:
            return None
        case LegendWidthEnum.SMALL:
            return 'small'
        case LegendWidthEnum.MEDIUM:
            return 'medium'
        case LegendWidthEnum.LARGE:
            return 'large'
        case LegendWidthEnum.EXTRA_LARGE:
            return 'xlarge'


class PartitionLegendModel(Protocol):
    """Structural interface for partition chart legend config models.

    All partition chart legends (``PieLegend``, ``TreemapLegend``,
    ``MosaicLegend``, ``WaffleLegend``) satisfy this protocol.
    """

    visible: LegendVisibleEnum | None
    position: Literal['top', 'right', 'bottom', 'left'] | None
    width: LegendWidthEnum | None
    truncate_labels: int | None
    nested: bool | None
    show_single_series: bool | None


@dataclass(frozen=True)
class PartitionLegendOptions:
    """Compiled legend options for partition chart visualization layers."""

    legend_display: str
    legend_position: Literal['top', 'right', 'bottom', 'left'] | None
    legend_size: KbnLegendSize | None
    truncate_legend: bool | None
    legend_max_lines: int | None
    nested_legend: bool | None
    show_single_series: bool | None


def compile_partition_number_display(values_format: str | None) -> str:
    """Compile a partition chart number-display value from a values format string.

    Args:
        values_format: The ``appearance.values.format`` field, or ``None`` for default behaviour.

    Returns:
        The Kibana ``numberDisplay`` value (``'percent'``, ``'value'``, ``'hidden'``, or the raw format string).

    """
    if values_format is None:
        return 'percent'
    if values_format == 'integer':
        return 'value'
    return 'hidden' if values_format == 'hide' else values_format


def compile_partition_category_display(position: str | None) -> str:
    """Compile a partition chart category-display value from a position string.

    Args:
        position: The ``appearance.categories.position`` field, or ``None`` for default behaviour.

    Returns:
        The Kibana ``categoryDisplay`` value (``'default'``, ``'inside'``, ``'hide'``, or the raw position string).

    """
    if position is None:
        return 'default'
    return 'default' if position in ('auto', 'show') else position


def compile_partition_legend_options(legend: PartitionLegendModel | None) -> PartitionLegendOptions:
    """Compile partition chart legend options from a legend config model.

    Args:
        legend: The legend config model, or ``None`` when the chart has no legend section.

    Returns:
        Compiled legend options with Kibana-compatible defaults.

    """
    legend_display = 'default'
    legend_size: KbnLegendSize | None = None
    truncate_legend: bool | None = None
    legend_max_lines: int | None = None
    nested_legend: bool | None = None
    show_single_series: bool | None = None
    legend_position: Literal['top', 'right', 'bottom', 'left'] | None = None

    if legend is not None:
        if legend.visible is not None:
            legend_display = 'default' if legend.visible == 'auto' else legend.visible
        if legend.width is not None:
            legend_size = map_legend_size(legend.width)
        if legend.truncate_labels is not None:
            # Kibana mapping: 0 explicitly disables truncation (truncateLegend=False),
            # otherwise set legendMaxLines and let Kibana use its default truncation behavior
            if legend.truncate_labels == 0:
                truncate_legend = False
            else:
                legend_max_lines = legend.truncate_labels
        if legend.nested is not None:
            nested_legend = legend.nested
        if legend.show_single_series is not None:
            show_single_series = legend.show_single_series
        if legend.position is not None:
            legend_position = legend.position

    return PartitionLegendOptions(
        legend_display=legend_display,
        legend_position=legend_position,
        legend_size=legend_size,
        truncate_legend=truncate_legend,
        legend_max_lines=legend_max_lines,
        nested_legend=nested_legend,
        show_single_series=show_single_series,
    )


def compile_color_value_mapping(color_config: ColorValueMapping | None) -> KbnLayerColorMapping:
    """Compile a ColorValueMapping config object into a Kibana color mapping view model.

    Args:
        color_config: The color configuration from YAML, or None for default color mapping.

    Returns:
        KbnLayerColorMapping: The compiled Kibana color mapping view model with defaults if no config provided.

    """
    # Use default ColorValueMapping if none provided
    if color_config is None:
        color_config = ColorValueMapping()

    # Build manual color assignments
    kbn_assignments: list[KbnLayerColorMappingAssignment] = []

    for assignment in color_config.assignments:
        # Determine which values to use
        values_to_assign: list[str] = []
        if assignment.value is not None:
            values_to_assign = [assignment.value]
        elif assignment.values is not None and len(assignment.values) > 0:
            values_to_assign = assignment.values

        if len(values_to_assign) > 0:
            kbn_rule = KbnLayerColorMappingRule(
                type=KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE_MATCH_EXACTLY,
                values=values_to_assign,
            )
            kbn_color = KbnLayerColorMappingColor(
                type=KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE_COLOR_CODE,
                colorCode=assignment.color,
            )
            kbn_assignments.append(
                KbnLayerColorMappingAssignment(
                    rule=kbn_rule,
                    color=kbn_color,
                    touched=KBN_DEFAULT_COLOR_MAPPING_TOUCHED,
                )
            )

    # Build special assignments (fallback colors)
    special_assignments = [
        KbnLayerColorMappingSpecialAssignment(
            rule=KbnLayerColorMappingRule(type=KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE),
            color=KbnLayerColorMappingColor(type=KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE),
            touched=KBN_DEFAULT_COLOR_MAPPING_TOUCHED,
        )
    ]

    # Color mode is always categorical (gradients are not supported)
    color_mode = {'type': 'categorical'}

    return KbnLayerColorMapping(
        paletteId=color_config.palette,
        colorMode=color_mode,
        assignments=kbn_assignments,
        specialAssignments=special_assignments,
    )


def build_collapse_fns(dimension_collapses: Sequence[tuple[str, str | None]]) -> dict[str, str] | None:
    """Build a collapse function mapping for chart dimensions."""
    collapse_fns = {dimension_id: str(collapse) for dimension_id, collapse in dimension_collapses if collapse is not None}
    return collapse_fns or None


def compile_color_range_mapping(color_config: ColorRangeMapping | None) -> KbnRangePalette | None:
    """Compile a range-based color config into Kibana range palette format.

    Kibana uses two parallel arrays in the palette params:
    - ``stops``: each entry marks the END of a color band
    - ``colorStops``: each entry marks the START of the same color band
    """
    if color_config is None:
        return None

    user_thresholds = color_config.thresholds

    range_min = color_config.range_min
    range_max = color_config.range_max

    # Build stops (END of each band) from user thresholds.
    stops = [KbnRangePaletteStop(color=entry.color, stop=entry.up_to) for entry in user_thresholds]
    percent_max = float(PERCENT_MAX)
    if range_max is not None:
        range_max_value = float(range_max)
        last_stop = stops[-1].stop
        if last_stop is not None and last_stop < range_max_value:
            stops.append(KbnRangePaletteStop(color=stops[-1].color, stop=range_max_value))
    elif color_config.range_type == 'percent' and stops[-1].stop != percent_max:
        stops.append(KbnRangePaletteStop(color=stops[-1].color, stop=percent_max))

    # colorStops carries the lower bound for each band.
    # Example:
    #   range_min=0, stops=[25, 50, 75]
    #   colorStops=[0, 25, 50]
    lower_bound = range_min
    color_stops: list[KbnRangePaletteStop] = []
    for entry in stops:
        color_stops.append(KbnRangePaletteStop(color=entry.color, stop=lower_bound))
        lower_bound = entry.stop
    n = len(stops)

    return KbnRangePalette(
        params=KbnRangePaletteParams(
            steps=n,
            rangeType=color_config.range_type,
            rangeMin=range_min,
            rangeMax=range_max,
            stops=stops,
            colorStops=color_stops,
            continuity='above',
            maxSteps=n,
        ),
    )
