"""Helper functions for compiling chart base components."""

from dashboard_compiler.panels.charts.base.view import (
    KBN_DEFAULT_COLOR_MAPPING_COLOR_MODE_TYPE,
    KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE,
    KBN_DEFAULT_COLOR_MAPPING_PALETTE_ID,
    KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE,
    KBN_DEFAULT_COLOR_MAPPING_TOUCHED,
    KbnLayerColorMapping,
    KbnLayerColorMappingColor,
    KbnLayerColorMappingRule,
    KbnLayerColorMappingSpecialAssignment,
)


def create_default_color_mapping(palette_id: str | None = None) -> KbnLayerColorMapping:
    """Create a KbnLayerColorMapping with default values.

    Args:
        palette_id: Optional palette ID to use. If None, uses the default palette.

    Returns:
        A KbnLayerColorMapping instance with default values.

    """
    return KbnLayerColorMapping(
        assignments=[],
        specialAssignments=[
            KbnLayerColorMappingSpecialAssignment(
                rule=KbnLayerColorMappingRule(type=KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE),
                color=KbnLayerColorMappingColor(type=KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE),
                touched=KBN_DEFAULT_COLOR_MAPPING_TOUCHED,
            ),
        ],
        paletteId=palette_id or KBN_DEFAULT_COLOR_MAPPING_PALETTE_ID,
        colorMode={'type': KBN_DEFAULT_COLOR_MAPPING_COLOR_MODE_TYPE},
    )
