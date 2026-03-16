"""Compilation utilities for base chart components."""

from collections.abc import Sequence

from kb_dashboard_core.panels.charts.base.config import PERCENT_MAX, ColorRangeMapping, ColorValueMapping, LegendWidthEnum
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
