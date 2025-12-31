from dashboard_compiler.panels.charts.base.compile import compile_color_mapping
from dashboard_compiler.panels.charts.base.config import ColorAssignment, ColorMapping
from dashboard_compiler.panels.charts.base.view import (
    KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE_COLOR_CODE,
    KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE,
    KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE_MATCH_EXACTLY,
)


def test_compile_color_mapping_defaults() -> None:
    """Test compilation with default/empty color mapping."""
    result = compile_color_mapping(None)
    assert result.paletteId == 'eui_amsterdam_color_blind'
    assert result.assignments == []
    assert len(result.specialAssignments) == 1
    assert result.specialAssignments[0].rule.type == KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE
    assert result.specialAssignments[0].color.type == 'loop'


def test_compile_color_mapping_with_assignments() -> None:
    """Test compilation with explicit color assignments."""
    config = ColorMapping(
        palette='custom_palette',
        assignments=[
            ColorAssignment(value='foo', color='#FF0000'),
            ColorAssignment(values=['bar', 'baz'], color='#00FF00'),
        ],
    )
    result = compile_color_mapping(config)
    assert result.paletteId == 'custom_palette'
    assert len(result.assignments) == 2

    # Check first assignment (single value)
    assert result.assignments[0].rule.type == KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE_MATCH_EXACTLY
    assert result.assignments[0].rule.values == ['foo']
    assert result.assignments[0].color.type == KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE_COLOR_CODE
    assert result.assignments[0].color.colorCode == '#FF0000'

    # Check second assignment (multiple values)
    assert result.assignments[1].rule.type == KBN_DEFAULT_COLOR_MAPPING_RULE_TYPE_MATCH_EXACTLY
    assert result.assignments[1].rule.values == ['bar', 'baz']
    assert result.assignments[1].color.type == KBN_DEFAULT_COLOR_MAPPING_COLOR_TYPE_COLOR_CODE
    assert result.assignments[1].color.colorCode == '#00FF00'
