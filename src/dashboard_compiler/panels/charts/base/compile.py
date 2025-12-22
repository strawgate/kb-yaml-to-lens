"""Compilation utilities for base chart components."""

from dashboard_compiler.panels.charts.base.config import ColorMapping
from dashboard_compiler.panels.charts.base.view import (
    KbnLayerColorMapping,
    KbnLayerColorMappingAssignment,
    KbnLayerColorMappingColor,
    KbnLayerColorMappingRule,
)


def compile_color_mapping(color_config: ColorMapping | None) -> KbnLayerColorMapping:
    """Compile a ColorMapping config object into a Kibana color mapping view model.

    Args:
        color_config: The color configuration from YAML, or None for defaults.

    Returns:
        KbnLayerColorMapping: The compiled Kibana color mapping view model.

    """
    if not color_config:
        return KbnLayerColorMapping()

    # Build manual color assignments
    kbn_assignments: list[KbnLayerColorMappingAssignment] = []

    for assignment in color_config.assignments:
        # Determine which values to use
        values_to_assign: list[str] = []
        if assignment.value:
            values_to_assign = [assignment.value]
        elif assignment.values:
            values_to_assign = assignment.values

        if values_to_assign:
            kbn_rule = KbnLayerColorMappingRule(
                type='matchExactly',
                values=values_to_assign,
            )
            kbn_color = KbnLayerColorMappingColor(
                type='colorCode',
                colorCode=assignment.color,
            )
            kbn_assignments.append(
                KbnLayerColorMappingAssignment(
                    rule=kbn_rule,
                    color=kbn_color,
                    touched=False,
                )
            )

    # Build color mode
    color_mode = {'type': color_config.mode}

    return KbnLayerColorMapping(
        paletteId=color_config.palette,
        colorMode=color_mode,
        assignments=kbn_assignments,
    )
