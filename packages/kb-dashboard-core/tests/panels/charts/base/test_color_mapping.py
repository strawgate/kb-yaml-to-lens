"""Tests for color mapping compilation utilities."""

from inline_snapshot import snapshot

from kb_dashboard_core.panels.charts.base.compile import compile_color_range_mapping, compile_color_value_mapping
from kb_dashboard_core.panels.charts.base.config import (
    ColorRangeMapping,
    ColorRangeStop,
    ColorValueAssignment,
    ColorValueMapping,
)


class TestCompileColorValueMapping:
    """Tests for compile_color_value_mapping function."""

    def test_compiles_default_color_mapping_when_none_provided(self) -> None:
        """Test that compile_color_value_mapping creates default mapping when None is provided."""
        result = compile_color_value_mapping(None)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_compiles_empty_color_mapping(self) -> None:
        """Test that compile_color_value_mapping handles empty ColorValueMapping."""
        color_config = ColorValueMapping()
        result = compile_color_value_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )

    def test_compiles_color_mapping_with_custom_palette(self) -> None:
        """Test that compile_color_value_mapping preserves custom palette."""
        color_config = ColorValueMapping(palette='kibana_palette')
        result = compile_color_value_mapping(color_config)
        assert result.paletteId == 'kibana_palette'

    def test_compiles_color_mapping_with_single_value_assignment(self) -> None:
        """Test that compile_color_value_mapping handles single value assignment."""
        color_config = ColorValueMapping(
            assignments=[
                ColorValueAssignment(value='Error', color='#FF0000'),
            ]
        )
        result = compile_color_value_mapping(color_config)
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
        """Test that compile_color_value_mapping handles multiple values assignment."""
        color_config = ColorValueMapping(
            assignments=[
                ColorValueAssignment(values=['Error', 'Critical'], color='#FF0000'),
            ]
        )
        result = compile_color_value_mapping(color_config)
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
        """Test that compile_color_value_mapping handles multiple color assignments."""
        color_config = ColorValueMapping(
            assignments=[
                ColorValueAssignment(value='Error', color='#FF0000'),
                ColorValueAssignment(value='Warning', color='#FFA500'),
                ColorValueAssignment(value='Info', color='#0000FF'),
            ]
        )
        result = compile_color_value_mapping(color_config)
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
        color_config = ColorValueMapping(
            assignments=[
                ColorValueAssignment(value='Error', values=['Warning', 'Info'], color='#FF0000'),
            ]
        )
        result = compile_color_value_mapping(color_config)
        assert len(result.assignments) == 1
        assert result.assignments[0].rule.values == ['Error']

    def test_all_assignments_have_correct_structure(self) -> None:
        """Test that all assignments have the correct structure with rule, color, and touched."""
        color_config = ColorValueMapping(
            assignments=[
                ColorValueAssignment(value='Test', color='#123456'),
            ]
        )
        result = compile_color_value_mapping(color_config)
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
        color_config = ColorValueMapping()
        result = compile_color_value_mapping(color_config)
        assert result.model_dump() == snapshot(
            {
                'paletteId': 'eui_amsterdam_color_blind',
                'colorMode': {'type': 'categorical'},
                'assignments': [],
                'specialAssignments': [{'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}],
            }
        )


class TestCompileColorRangeMapping:
    """Tests for compile_color_range_mapping function."""

    def test_returns_none_when_no_range_mapping(self) -> None:
        """Test that no range config compiles to no palette."""
        result = compile_color_range_mapping(None)
        assert result is None

    def test_compiles_range_mapping_to_gauge_palette(self) -> None:
        """Test range mapping compilation to Kibana gauge palette format."""
        color_config = ColorRangeMapping(
            range_type='number',
            stops=[
                ColorRangeStop(stop=0, color='#00BF6F'),
                ColorRangeStop(stop=80, color='#FFA500'),
                ColorRangeStop(stop=95, color='#BD271E'),
            ],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.model_dump() == snapshot(
            {
                'name': 'custom',
                'type': 'palette',
                'params': {
                    'steps': 3,
                    'name': 'custom',
                    'reverse': False,
                    'rangeType': 'number',
                    'rangeMin': 0.0,
                    'rangeMax': None,
                    'progression': 'fixed',
                    'stops': [
                        {'color': '#00BF6F', 'stop': 80.0},
                        {'color': '#FFA500', 'stop': 95.0},
                        {'color': '#BD271E', 'stop': 95.0},
                    ],
                    'colorStops': [
                        {'color': '#00BF6F', 'stop': 0.0},
                        {'color': '#FFA500', 'stop': 80.0},
                        {'color': '#BD271E', 'stop': 95.0},
                    ],
                    'continuity': 'above',
                    'maxSteps': 5,
                },
            }
        )
