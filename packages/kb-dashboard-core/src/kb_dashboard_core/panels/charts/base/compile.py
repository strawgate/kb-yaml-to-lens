"""Compilation utilities for base chart components."""

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


def compile_color_range_mapping(color_config: ColorRangeMapping | None) -> KbnRangePalette | None:
    """Compile a range-based color config into Kibana range palette format.

    Kibana uses two parallel arrays in the palette params:
    - ``colorStops``: each entry marks the START of a color band
    - ``stops``: each entry marks the END of a color band

    Given user-provided stops ``[(0, green), (60, yellow), (85, red)]``:
    - colorStops = [{color: green, stop: 0}, {color: yellow, stop: 60}, {color: red, stop: 85}]
    - stops = [{color: green, stop: 60}, {color: yellow, stop: 85}, {color: red, stop: 100}]
      (last stop is capped at 100 for percent, or uses the last user value for number)
    """
    if color_config is None:
        return None

    user_stops = color_config.stops
    n = len(user_stops)

    # Build colorStops (START of each band) — directly from user input
    color_stops = [KbnRangePaletteStop(color=s.color, stop=s.stop) for s in user_stops]

    # Build stops (END of each band) — each band ends where the next begins;
    # the last band ends at 100 for percent ranges
    stops: list[KbnRangePaletteStop] = []
    for i in range(n):
        if i < n - 1:
            stops.append(KbnRangePaletteStop(color=user_stops[i].color, stop=user_stops[i + 1].stop))
        else:
            end = 100.0 if color_config.range_type == 'percent' else user_stops[i].stop
            stops.append(KbnRangePaletteStop(color=user_stops[i].color, stop=end))

    return KbnRangePalette(
        params=KbnRangePaletteParams(
            steps=n,
            rangeType=color_config.range_type,
            rangeMin=user_stops[0].stop,
            stops=stops,
            colorStops=color_stops,
            maxSteps=n,
        ),
    )
