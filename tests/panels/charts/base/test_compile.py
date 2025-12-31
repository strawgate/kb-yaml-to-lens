
from dashboard_compiler.panels.charts.base.compile import compile_color_mapping
from dashboard_compiler.panels.charts.base.config import ColorMapping, ColorAssignment
from dashboard_compiler.panels.charts.base.view import (
    KbnLayerColorMapping,
)

def test_compile_color_mapping_defaults() -> None:
    """Test compilation with None config."""
    result = compile_color_mapping(None)
    assert isinstance(result, KbnLayerColorMapping)
    assert len(result.assignments) == 0
    assert result.paletteId == 'eui_amsterdam_color_blind'

def test_compile_color_mapping_single_value() -> None:
    """Test compilation with single value assignment."""
    config = ColorMapping(
        assignments=[
            ColorAssignment(value='foo', color='#ffffff')
        ]
    )
    result = compile_color_mapping(config)
    assert len(result.assignments) == 1
    assert result.assignments[0].rule.values == ['foo']
    assert result.assignments[0].color.colorCode == '#ffffff'

def test_compile_color_mapping_multiple_values() -> None:
    """Test compilation with multiple values assignment."""
    config = ColorMapping(
        assignments=[
            ColorAssignment(values=['foo', 'bar'], color='#ffffff')
        ]
    )
    result = compile_color_mapping(config)
    assert len(result.assignments) == 1
    assert result.assignments[0].rule.values == ['foo', 'bar']
    assert result.assignments[0].color.colorCode == '#ffffff'
