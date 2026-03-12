"""Tests for color mapping compilation utilities."""

import pytest
from inline_snapshot import snapshot
from pydantic import ValidationError

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


class TestColorValueAssignmentValidation:
    """Tests for ColorValueAssignment validation."""

    def test_rejects_assignment_without_value_or_values(self) -> None:
        """Test that assignment requires at least one of value or values."""
        with pytest.raises(ValidationError, match="At least one of 'value' or 'values' must be provided"):
            ColorValueAssignment(color='#FF0000')

    def test_rejects_assignment_with_empty_values_list(self) -> None:
        """Test that assignment rejects empty values list when value is also None."""
        with pytest.raises(ValidationError, match="At least one of 'value' or 'values' must be provided"):
            ColorValueAssignment(values=[], color='#FF0000')


class TestColorRangeMappingValidation:
    """Tests for ColorRangeMapping validation."""

    def test_rejects_unsorted_stops(self) -> None:
        """Test that stops must be in ascending order."""
        with pytest.raises(ValidationError, match='sorted in ascending order'):
            ColorRangeMapping(
                range_type='number',
                stops=[
                    ColorRangeStop(stop=80, color='#00BF6F'),
                    ColorRangeStop(stop=50, color='#FFA500'),
                ],
            )

    def test_rejects_percent_stop_above_100(self) -> None:
        """Test that percent-based stops cannot exceed 100."""
        with pytest.raises(ValidationError, match='between 0 and 100'):
            ColorRangeMapping(
                range_type='percent',
                stops=[
                    ColorRangeStop(stop=0, color='#00BF6F'),
                    ColorRangeStop(stop=150, color='#BD271E'),
                ],
            )

    def test_rejects_percent_stop_below_zero(self) -> None:
        """Test that percent-based stops cannot be negative."""
        with pytest.raises(ValidationError, match='between 0 and 100'):
            ColorRangeMapping(
                range_type='percent',
                stops=[
                    ColorRangeStop(stop=-10, color='#00BF6F'),
                    ColorRangeStop(stop=50, color='#BD271E'),
                ],
            )

    def test_rejects_empty_stops(self) -> None:
        """Test that at least one stop is required."""
        with pytest.raises(ValidationError):
            ColorRangeMapping(range_type='number', stops=[])

    def test_accepts_single_stop(self) -> None:
        """Test that a single stop is valid."""
        mapping = ColorRangeMapping(
            range_type='percent',
            stops=[ColorRangeStop(stop=50, color='#FFA500')],
        )
        assert len(mapping.stops) == 1

    def test_accepts_valid_ascending_stops(self) -> None:
        """Test that valid ascending stops are accepted."""
        mapping = ColorRangeMapping(
            range_type='number',
            stops=[
                ColorRangeStop(stop=0, color='#00BF6F'),
                ColorRangeStop(stop=50, color='#FFA500'),
                ColorRangeStop(stop=100, color='#BD271E'),
            ],
        )
        assert len(mapping.stops) == 3

    def test_accepts_valid_percent_stops_within_bounds(self) -> None:
        """Test that valid percent stops within 0-100 are accepted."""
        mapping = ColorRangeMapping(
            range_type='percent',
            stops=[
                ColorRangeStop(stop=0, color='#00BF6F'),
                ColorRangeStop(stop=50, color='#FFA500'),
                ColorRangeStop(stop=100, color='#BD271E'),
            ],
        )
        assert len(mapping.stops) == 3

    def test_number_type_allows_values_outside_percent_bounds(self) -> None:
        """Test that number range type allows values outside 0-100."""
        mapping = ColorRangeMapping(
            range_type='number',
            stops=[
                ColorRangeStop(stop=-50, color='#00BF6F'),
                ColorRangeStop(stop=200, color='#BD271E'),
            ],
        )
        assert len(mapping.stops) == 2


class TestCompileColorRangeMapping:
    """Tests for compile_color_range_mapping function."""

    def test_returns_none_when_no_range_mapping(self) -> None:
        """Test that no range config compiles to no palette."""
        result = compile_color_range_mapping(None)
        assert result is None

    def test_compiles_number_range_mapping(self) -> None:
        """Test number-based range mapping compilation.

        The last stop in 'stops' (band endpoints) equals the last user-provided
        stop value for number ranges, resulting in a zero-width final band. This is
        intentional to match Kibana's expected format.
        """
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
                    'maxSteps': 3,
                },
            }
        )

    def test_compiles_percent_range_mapping(self) -> None:
        """Test percent-based range mapping caps the last stop at 100."""
        color_config = ColorRangeMapping(
            range_type='percent',
            stops=[
                ColorRangeStop(stop=0, color='#00BF6F'),
                ColorRangeStop(stop=60, color='#FFA500'),
                ColorRangeStop(stop=85, color='#BD271E'),
            ],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.rangeType == 'percent'
        assert result.params.stops[-1].stop == 100.0
        assert result.params.maxSteps == 3
        # colorStops reflect the user's input directly
        assert result.params.colorStops[0].stop == 0.0
        assert result.params.colorStops[1].stop == 60.0
        assert result.params.colorStops[2].stop == 85.0

    def test_compiles_single_stop(self) -> None:
        """Test compilation with a single stop."""
        color_config = ColorRangeMapping(
            range_type='percent',
            stops=[ColorRangeStop(stop=50, color='#FFA500')],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.steps == 1
        assert result.params.rangeMin == 50.0
        assert len(result.params.stops) == 1
        assert len(result.params.colorStops) == 1
        assert result.params.stops[0].stop == 100.0
        assert result.params.colorStops[0].stop == 50.0
