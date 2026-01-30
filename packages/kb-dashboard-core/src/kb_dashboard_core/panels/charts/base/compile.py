"""Compilation utilities for base chart components."""

from kb_dashboard_core.panels.charts.base.config import ColorMapping
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
