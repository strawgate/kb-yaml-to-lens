"""Tests for color mapping compilation utilities."""

from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.base.compile import compile_color_mapping
from dashboard_compiler.panels.charts.base.config import ColorAssignment, ColorMapping


class TestCompileColorMapping:
    """Tests for compile_color_mapping function."""

    def test_compiles_default_color_mapping_when_none_provided(self) -> None:
        """Test that compile_color_mapping creates default mapping when None is provided."""
        result = compile_color_mapping(None)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_compiles_empty_color_mapping(self) -> None:
        """Test that compile_color_mapping handles empty ColorMapping."""
        color_config = ColorMapping()
        result = compile_color_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_compiles_color_mapping_with_custom_palette(self) -> None:
        """Test that compile_color_mapping preserves custom palette."""
        color_config = ColorMapping(palette='kibana_palette')
        result = compile_color_mapping(color_config)
        assert result.paletteId == 'kibana_palette'

    def test_compiles_color_mapping_with_single_value_assignment(self) -> None:
        """Test that compile_color_mapping handles single value assignment."""
        color_config = ColorMapping(
            assignments=[
                ColorAssignment(value='Error', color='#FF0000'),
            ]
        )
        result = compile_color_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [
                    {
                        'rule': {'type': 'matchExactly', 'values': ['Error']},
                        'color': {'type': 'colorCode', 'colorCode': '#FF0000'},
                        'touched': False,
                    }
                ],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_compiles_color_mapping_with_multiple_values_assignment(self) -> None:
        """Test that compile_color_mapping handles multiple values assignment."""
        color_config = ColorMapping(
            assignments=[
                ColorAssignment(values=['Error', 'Critical'], color='#FF0000'),
            ]
        )
        result = compile_color_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [
                    {
                        'rule': {'type': 'matchExactly', 'values': ['Error', 'Critical']},
                        'color': {'type': 'colorCode', 'colorCode': '#FF0000'},
                        'touched': False,
                    }
                ],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_compiles_color_mapping_with_multiple_assignments(self) -> None:
        """Test that compile_color_mapping handles multiple color assignments."""
        color_config = ColorMapping(
            assignments=[
                ColorAssignment(value='Error', color='#FF0000'),
                ColorAssignment(value='Warning', color='#FFA500'),
                ColorAssignment(value='Info', color='#0000FF'),
            ]
        )
        result = compile_color_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [
                    {
                        'rule': {'type': 'matchExactly', 'values': ['Error']},
                        'color': {'type': 'colorCode', 'colorCode': '#FF0000'},
                        'touched': False,
                    },
                    {
                        'rule': {'type': 'matchExactly', 'values': ['Warning']},
                        'color': {'type': 'colorCode', 'colorCode': '#FFA500'},
                        'touched': False,
                    },
                    {
                        'rule': {'type': 'matchExactly', 'values': ['Info']},
                        'color': {'type': 'colorCode', 'colorCode': '#0000FF'},
                        'touched': False,
                    },
                ],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_value_takes_precedence_over_values(self) -> None:
        """Test that single value takes precedence when both value and values are provided."""
        color_config = ColorMapping(
            assignments=[
                ColorAssignment(value='Error', values=['Warning', 'Info'], color='#FF0000'),
            ]
        )
        result = compile_color_mapping(color_config)
        assert len(result.assignments) == 1
        assert result.assignments[0].rule.values == ['Error']

    def test_all_assignments_have_correct_structure(self) -> None:
        """Test that all assignments have the correct structure with rule, color, and touched."""
        color_config = ColorMapping(
            assignments=[
                ColorAssignment(value='Test', color='#123456'),
            ]
        )
        result = compile_color_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [
                    {
                        'rule': {'type': 'matchExactly', 'values': ['Test']},
                        'color': {'type': 'colorCode', 'colorCode': '#123456'},
                        'touched': False,
                    }
                ],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_special_assignments_always_present(self) -> None:
        """Test that special assignments are always present in the result."""
        color_config = ColorMapping()
        result = compile_color_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )
