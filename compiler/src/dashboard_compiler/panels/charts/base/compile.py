"""Compilation utilities for base chart components."""

from typing import Literal

from dashboard_compiler.panels.charts.base.config import ColorMapping, LegendVisibleEnum
from dashboard_compiler.panels.charts.base.view import (
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
)


def compile_color_mapping(color_config: ColorMapping | None) -> KbnLayerColorMapping:
    """Compile a ColorMapping config object into a Kibana color mapping view model.

    Args:
        color_config: The color configuration from YAML, or None for default color mapping.

    Returns:
        KbnLayerColorMapping: The compiled Kibana color mapping view model with defaults if no config provided.

    """
    # Use default ColorMapping if none provided
    if color_config is None:
        color_config = ColorMapping()

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


def compile_legend_visibility(
    visible: LegendVisibleEnum | None,
) -> bool | None:
    """Convert a LegendVisibleEnum value to a boolean visibility state.

    Maps legend visibility enum values to Kibana's expected boolean representation:
    - SHOW -> True (always show legend)
    - HIDE -> False (always hide legend)
    - AUTO/None -> None (omit field, let Kibana decide based on series count)

    Args:
        visible: The legend visibility enum value, or None for auto.

    Returns:
        True to show, False to hide, or None to let Kibana auto-determine.
    """
    if visible is None:
        return None

    match visible:
        case LegendVisibleEnum.SHOW:
            return True
        case LegendVisibleEnum.HIDE:
            return False
        case LegendVisibleEnum.AUTO:
            return None
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unknown legend visibility value: {visible}'
            raise ValueError(msg)  # pyright: ignore[reportUnreachable]


LegendPosition = Literal['top', 'bottom', 'left', 'right']


def compile_legend_position(
    position: LegendPosition | None,
    default: LegendPosition = 'right',
) -> LegendPosition:
    """Get the legend position, using a default if not specified.

    Args:
        position: The configured legend position, or None.
        default: The default position to use if not specified.

    Returns:
        The legend position string.
    """
    return position if position is not None else default
