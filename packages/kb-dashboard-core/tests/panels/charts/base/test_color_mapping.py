"""Tests for color mapping compilation utilities."""

import pytest
from inline_snapshot import snapshot
from pydantic import ValidationError

from kb_dashboard_core.panels.charts.base.compile import (
    build_collapse_fns,
    compile_color_range_mapping,
    compile_color_value_mapping,
    map_legend_size,
)
from kb_dashboard_core.panels.charts.base.config import (
    ColorRangeMapping,
    ColorThreshold,
    ColorValueAssignment,
    ColorValueMapping,
    LegendWidthEnum,
)
from kb_dashboard_core.panels.charts.base.view import KbnLegendSize


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
                thresholds=[
                    ColorThreshold(up_to=80, color='#00BF6F'),
                    ColorThreshold(up_to=50, color='#FFA500'),
                ],
            )

    def test_rejects_percent_stop_above_100(self) -> None:
        """Test that percent-based stops cannot exceed 100."""
        with pytest.raises(ValidationError, match='between 0 and 100'):
            ColorRangeMapping(
                range_type='percent',
                thresholds=[
                    ColorThreshold(up_to=0, color='#00BF6F'),
                    ColorThreshold(up_to=150, color='#BD271E'),
                ],
            )

    def test_rejects_percent_stop_below_zero(self) -> None:
        """Test that percent-based stops cannot be negative."""
        with pytest.raises(ValidationError, match='between 0 and 100'):
            ColorRangeMapping(
                range_type='percent',
                thresholds=[
                    ColorThreshold(up_to=-10, color='#00BF6F'),
                    ColorThreshold(up_to=50, color='#BD271E'),
                ],
            )

    def test_rejects_empty_stops(self) -> None:
        """Test that at least one stop is required."""
        with pytest.raises(ValidationError):
            ColorRangeMapping(range_type='number', thresholds=[])

    def test_accepts_single_stop(self) -> None:
        """Test that a single threshold is valid."""
        mapping = ColorRangeMapping(
            range_type='percent',
            thresholds=[ColorThreshold(up_to=50, color='#FFA500')],
        )
        assert len(mapping.thresholds) == 1

    def test_accepts_valid_ascending_stops(self) -> None:
        """Test that valid ascending stops are accepted."""
        mapping = ColorRangeMapping(
            range_type='number',
            thresholds=[
                ColorThreshold(up_to=0, color='#00BF6F'),
                ColorThreshold(up_to=50, color='#FFA500'),
                ColorThreshold(up_to=100, color='#BD271E'),
            ],
        )
        assert len(mapping.thresholds) == 3

    def test_accepts_valid_percent_stops_within_bounds(self) -> None:
        """Test that valid percent stops within 0-100 are accepted."""
        mapping = ColorRangeMapping(
            range_type='percent',
            thresholds=[
                ColorThreshold(up_to=0, color='#00BF6F'),
                ColorThreshold(up_to=50, color='#FFA500'),
                ColorThreshold(up_to=100, color='#BD271E'),
            ],
        )
        assert len(mapping.thresholds) == 3

    def test_accepts_legacy_continuity_alias(self) -> None:
        """Legacy continuity input is rejected in 0.4.0."""
        with pytest.raises(ValidationError, match='continuity'):
            ColorRangeMapping.model_validate(
                {
                    'continuity': 'all',
                    'thresholds': [{'up_to': 50, 'color': '#FFA500'}],
                }
            )

    def test_extend_beyond_range_is_accepted_and_ignored(self) -> None:
        """Legacy extend_beyond_range input is rejected in 0.4.0."""
        with pytest.raises(ValidationError, match='extend_beyond_range'):
            ColorRangeMapping.model_validate(
                {
                    'extend_beyond_range': 'none',
                    'thresholds': [{'up_to': 50, 'color': '#FFA500'}],
                }
            )

    def test_number_type_allows_values_outside_percent_bounds(self) -> None:
        """Test that number range type allows values outside 0-100."""
        mapping = ColorRangeMapping(
            range_type='number',
            thresholds=[
                ColorThreshold(up_to=-50, color='#00BF6F'),
                ColorThreshold(up_to=200, color='#BD271E'),
            ],
        )
        assert len(mapping.thresholds) == 2

    def test_rejects_percent_range_max_above_100(self) -> None:
        """Test percent range_max must be between 0 and 100."""
        with pytest.raises(ValidationError, match='range_max must be between 0 and 100'):
            ColorRangeMapping(
                range_type='percent',
                range_max=101,
                thresholds=[ColorThreshold(up_to=90, color='#00BF6F')],
            )

    def test_rejects_range_min_greater_than_or_equal_to_range_max(self) -> None:
        """Test range bounds must be strictly increasing."""
        with pytest.raises(ValidationError, match="'range_min' must be less than 'range_max'"):
            ColorRangeMapping(
                range_type='number',
                range_min=10,
                range_max=10,
                thresholds=[ColorThreshold(up_to=20, color='#00BF6F')],
            )


class TestMapLegendSize:
    """Tests for map_legend_size helper."""

    @pytest.mark.parametrize(
        ('size', 'expected'),
        [
            (None, None),
            ('small', 'small'),
            ('medium', 'medium'),
            ('large', 'large'),
            ('extra_large', 'xlarge'),
        ],
    )
    def test_maps_legend_sizes(self, size: LegendWidthEnum | None, expected: KbnLegendSize | None) -> None:
        """Test YAML legend size mapping to Kibana-compatible values."""
        assert map_legend_size(size) == expected


class TestCompileColorRangeMapping:
    """Tests for compile_color_range_mapping function."""

    def test_returns_none_when_no_range_mapping(self) -> None:
        """Test that no range config compiles to no palette."""
        result = compile_color_range_mapping(None)
        assert result is None

    def test_compiles_number_range_mapping(self) -> None:
        """Test number-based range mapping compilation."""
        color_config = ColorRangeMapping(
            range_type='number',
            thresholds=[
                ColorThreshold(up_to=80, color='#00BF6F'),
                ColorThreshold(up_to=95, color='#FFA500'),
                ColorThreshold(up_to=120, color='#BD271E'),
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
                        {'color': '#BD271E', 'stop': 120.0},
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
        """Test percent ranges use lower bounds in colorStops and 0..100 stops."""
        color_config = ColorRangeMapping(
            range_type='percent',
            thresholds=[
                ColorThreshold(up_to=90, color='#cc5642'),
                ColorThreshold(up_to=95, color='#d6bf57'),
                ColorThreshold(up_to=100, color='#54b399'),
            ],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.rangeType == 'percent'
        assert result.params.rangeMin == 0.0
        assert result.params.rangeMax is None
        assert result.params.stops[0].stop == 90.0
        assert result.params.stops[1].stop == 95.0
        assert result.params.stops[-1].stop == 100.0
        assert result.params.maxSteps == 3
        assert result.params.colorStops[0].stop == 0.0
        assert result.params.colorStops[1].stop == 90.0
        assert result.params.colorStops[2].stop == 95.0

    def test_compiles_single_stop(self) -> None:
        """Test percent compilation preserves the threshold and appends terminal 100."""
        color_config = ColorRangeMapping(
            range_type='percent',
            thresholds=[ColorThreshold(up_to=50, color='#FFA500')],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.steps == 2
        assert result.params.rangeMin == 0.0
        assert result.params.rangeMax is None
        assert len(result.params.stops) == 2
        assert len(result.params.colorStops) == 2
        assert [entry.stop for entry in result.params.stops] == [50.0, 100.0]
        assert [entry.stop for entry in result.params.colorStops] == [0.0, 50.0]

    def test_compiles_percent_range_mapping_with_custom_range_max(self) -> None:
        """Test percent range supports custom max while preserving stop semantics."""
        color_config = ColorRangeMapping(
            range_type='percent',
            range_max=95,
            thresholds=[ColorThreshold(up_to=100, color='#24c292')],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.rangeMin == 0.0
        assert result.params.rangeMax == 95.0
        assert [entry.stop for entry in result.params.colorStops] == [0.0]
        assert [entry.stop for entry in result.params.stops] == [100.0]

    def test_compiles_number_range_mapping_with_custom_bounds(self) -> None:
        """Test number range honors explicit min/max bounds."""
        color_config = ColorRangeMapping(
            range_type='number',
            range_min=-10,
            range_max=100,
            thresholds=[
                ColorThreshold(up_to=4.25, color='#24c292'),
                ColorThreshold(up_to=5, color='#ffc9c2'),
                ColorThreshold(up_to=6, color='#ffc9c2'),
            ],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.rangeMin == -10.0
        assert result.params.rangeMax == 100.0
        assert result.params.continuity == 'above'
        assert [entry.stop for entry in result.params.colorStops] == [-10.0, 4.25, 5.0, 6.0]
        assert [entry.stop for entry in result.params.stops] == [4.25, 5.0, 6.0, 100.0]

    def test_compiles_number_range_mapping_extends_last_stop_to_range_max(self) -> None:
        """Test number range appends a terminal stop when explicit range_max exceeds last threshold."""
        color_config = ColorRangeMapping(
            range_type='number',
            range_min=0,
            range_max=100,
            thresholds=[
                ColorThreshold(up_to=25, color='#00BF6F'),
                ColorThreshold(up_to=50, color='#FFA500'),
                ColorThreshold(up_to=75, color='#BD271E'),
            ],
        )

        result = compile_color_range_mapping(color_config)

        assert result is not None
        assert [entry.stop for entry in result.params.stops] == [25.0, 50.0, 75.0, 100.0]
        assert [entry.stop for entry in result.params.colorStops] == [0.0, 25.0, 50.0, 75.0]
        assert result.params.stops[-1].color == '#BD271E'

    def test_compiles_number_range_mapping_with_open_bounds(self) -> None:
        """Test number range can emit open bounds with null lower start-point."""
        color_config = ColorRangeMapping(
            range_type='number',
            range_min=None,
            range_max=None,
            thresholds=[
                ColorThreshold(up_to=4.25, color='#24c292'),
                ColorThreshold(up_to=5, color='#ffc9c2'),
            ],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert result.params.rangeMin is None
        assert result.params.rangeMax is None
        assert result.params.continuity == 'above'
        assert [entry.stop for entry in result.params.colorStops] == [None, 4.25]
        assert [entry.stop for entry in result.params.stops] == [4.25, 5.0]


class TestBuildCollapseFns:
    """Tests for build_collapse_fns function."""

    def test_returns_none_when_no_collapse_values(self) -> None:
        """None or empty collapse values should produce no mapping."""
        result = build_collapse_fns([('dim-1', None), ('dim-2', None)])
        assert result is None

    def test_builds_mapping_for_non_none_collapse_values(self) -> None:
        """Only dimensions with collapse values should be included."""
        result = build_collapse_fns([('dim-1', 'sum'), ('dim-2', None), ('dim-3', 'avg')])
        assert result == {'dim-1': 'sum', 'dim-3': 'avg'}


class TestColorStopsLowerBounds:
    """Tests verifying that colorStops carries lower bounds."""

    def test_color_stops_use_previous_stop_for_percent_range(self) -> None:
        """ColorStops should start at range_min then use previous stop values."""
        color_config = ColorRangeMapping(
            range_type='percent',
            thresholds=[
                ColorThreshold(up_to=25, color='#00BF6F'),
                ColorThreshold(up_to=100, color='#BD271E'),
            ],
        )
        result = compile_color_range_mapping(color_config)
        assert result is not None
        assert [entry.stop for entry in result.params.colorStops] == [0.0, 25.0]
        assert [entry.stop for entry in result.params.stops] == [25.0, 100.0]


class TestCompilePartitionNumberDisplay:
    """Tests for compile_partition_number_display helper."""

    def test_returns_percent_when_none(self) -> None:
        """Default number display is 'percent' when no format is specified."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_number_display

        assert compile_partition_number_display(None) == 'percent'

    def test_maps_hide_to_hidden(self) -> None:
        """The YAML 'hide' value maps to Kibana 'hidden'."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_number_display

        assert compile_partition_number_display('hide') == 'hidden'

    def test_passes_through_other_formats(self) -> None:
        """Non-hide format strings are passed through unchanged."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_number_display

        assert compile_partition_number_display('percent') == 'percent'
        assert compile_partition_number_display('value') == 'value'


class TestCompilePartitionLegendOptions:
    """Tests for compile_partition_legend_options helper."""

    def test_returns_defaults_when_none(self) -> None:
        """All legend options use Kibana defaults when legend is None."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options

        result = compile_partition_legend_options(None)
        assert result.legend_display == 'default'
        assert result.legend_position == 'right'
        assert result.legend_size is None
        assert result.truncate_legend is None
        assert result.legend_max_lines is None
        assert result.nested_legend is None
        assert result.show_single_series is None

    def test_maps_auto_visible_to_default(self) -> None:
        """Legend visible='auto' maps to legend_display='default'."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.mosaic.config import MosaicLegend

        legend = MosaicLegend(visible='auto')
        result = compile_partition_legend_options(legend)
        assert result.legend_display == 'default'

    def test_maps_show_visible(self) -> None:
        """Legend visible='show' passes through."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.waffle.config import WaffleLegend

        legend = WaffleLegend(visible='show')
        result = compile_partition_legend_options(legend)
        assert result.legend_display == 'show'

    def test_maps_hide_visible(self) -> None:
        """Legend visible='hide' passes through."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.mosaic.config import MosaicLegend

        legend = MosaicLegend(visible='hide')
        result = compile_partition_legend_options(legend)
        assert result.legend_display == 'hide'

    def test_maps_legend_position(self) -> None:
        """Legend position is mapped correctly."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.mosaic.config import MosaicLegend

        legend = MosaicLegend(position='bottom')
        result = compile_partition_legend_options(legend)
        assert result.legend_position == 'bottom'

    def test_maps_legend_width(self) -> None:
        """Legend width enum maps to Kibana legend size."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.waffle.config import WaffleLegend

        legend = WaffleLegend(width='large')
        result = compile_partition_legend_options(legend)
        assert result.legend_size == 'large'

    def test_truncate_labels_zero_disables_truncation(self) -> None:
        """Setting truncate_labels to 0 disables truncation."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.mosaic.config import MosaicLegend

        legend = MosaicLegend(truncate_labels=0)
        result = compile_partition_legend_options(legend)
        assert result.truncate_legend is False
        assert result.legend_max_lines is None

    def test_truncate_labels_nonzero_sets_max_lines(self) -> None:
        """Setting truncate_labels to a positive value sets legend_max_lines."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.mosaic.config import MosaicLegend

        legend = MosaicLegend(truncate_labels=3)
        result = compile_partition_legend_options(legend)
        assert result.truncate_legend is None
        assert result.legend_max_lines == 3

    def test_maps_nested_legend(self) -> None:
        """Nested legend flag is mapped."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.waffle.config import WaffleLegend

        legend = WaffleLegend(nested=True)
        result = compile_partition_legend_options(legend)
        assert result.nested_legend is True

    def test_maps_show_single_series(self) -> None:
        """Show single series flag is mapped."""
        from kb_dashboard_core.panels.charts.base.compile import compile_partition_legend_options
        from kb_dashboard_core.panels.charts.mosaic.config import MosaicLegend

        legend = MosaicLegend(show_single_series=True)
        result = compile_partition_legend_options(legend)
        assert result.show_single_series is True
