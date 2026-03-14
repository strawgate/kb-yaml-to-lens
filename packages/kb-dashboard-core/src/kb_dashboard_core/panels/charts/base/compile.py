"""Compilation utilities for base chart components."""

from collections.abc import Sequence

from kb_dashboard_core.panels.charts.base.config import ColorRangeMapping, ColorValueMapping
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
    KbnRangePalette,
    KbnRangePaletteParams,
    KbnRangePaletteStop,
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
    - ``colorStops``: each entry marks the START of a color band
    - ``stops``: each entry marks the END of a color band

    User-provided stops are interpreted as band END points. START points are
    derived by shifting endpoints down by one and anchoring the first band to
    ``range_min``.
    """
    if color_config is None:
        return None

    user_stops = color_config.stops
    n = len(user_stops)

    range_min = color_config.range_min
    range_max = color_config.range_max

    # Build stops (END of each band) from user input.
    stops = [KbnRangePaletteStop(color=entry.color, stop=entry.stop) for entry in user_stops]
    if color_config.range_type == 'percent':
        stops[-1] = KbnRangePaletteStop(color=stops[-1].color, stop=100.0)

    # Build colorStops (START of each band) by shifting endpoints down by one.
    color_stops: list[KbnRangePaletteStop] = []
    for i, entry in enumerate(user_stops):
        start = range_min if i == 0 else user_stops[i - 1].stop
        color_stops.append(KbnRangePaletteStop(color=entry.color, stop=start))

    return KbnRangePalette(
        params=KbnRangePaletteParams(
            steps=n,
            rangeType=color_config.range_type,
            rangeMin=range_min,
            rangeMax=range_max,
            stops=stops,
            colorStops=color_stops,
            continuity=color_config.continuity,
            maxSteps=n,
        ),
    )
