"""Tests validating formula parser output against Kibana 8.19 fixtures.

These tests load real Kibana fixtures generated using the LensConfigBuilder API
and verify that our formula parser produces matching column structures.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensFormulaMetric

# Path to the fixture generator output directory
FIXTURE_DIR = Path(__file__).parents[5] / 'fixture-generator' / 'output' / 'v8.19.9'


def load_fixture(name: str) -> dict[str, Any]:
    """Load a Kibana fixture JSON file."""
    fixture_path = FIXTURE_DIR / name
    if not fixture_path.exists():
        pytest.skip(f'Fixture not found: {fixture_path}')
    with fixture_path.open() as f:
        return json.load(f)


def get_columns_from_fixture(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract columns from a Kibana fixture."""
    return fixture['state']['datasourceStates']['formBased']['layers']['layer_0']['columns']


def get_column_order_from_fixture(fixture: dict[str, Any]) -> list[str]:
    """Extract column order from a Kibana fixture."""
    return fixture['state']['datasourceStates']['formBased']['layers']['layer_0']['columnOrder']


def normalize_column_id(column_id: str, fixture_base_id: str, our_base_id: str) -> str:
    """Normalize column IDs between fixture and our output.

    Kibana fixtures use 'metric_formula_accessor' as base, while we use stable IDs.
    This normalizes for comparison.
    """
    return column_id.replace(fixture_base_id, our_base_id)


class TestFormulaFixtureValidation:
    """Test that our formula parser produces output matching Kibana fixtures."""

    def test_simple_aggregation_structure(self) -> None:
        """Test simple formula like average(bytes) matches Kibana structure."""
        fixture = load_fixture('formula-simple-average.json')
        fixture_columns = get_columns_from_fixture(fixture)

        # Our compiler produces the same structure
        metric = LensFormulaMetric(formula='average(bytes)')
        result = compile_lens_metric(metric)

        # Verify we have the same column types in the same pattern
        assert result.primary_column is not None
        assert result.primary_column.operationType == 'formula'

        # Should have 1 helper column (the aggregation)
        assert len(result.helper_columns) == 1

        # The helper column should be an aggregation
        helper_col = next(iter(result.helper_columns.values()))
        assert helper_col.operationType == 'average'

        # Verify fixture structure has same pattern
        formula_col = fixture_columns['metric_formula_accessor']
        assert formula_col['operationType'] == 'formula'
        assert 'metric_formula_accessorX0' in formula_col['references']

        agg_col = fixture_columns['metric_formula_accessorX0']
        assert agg_col['operationType'] == 'average'
        assert agg_col['sourceField'] == 'bytes'

    def test_counter_rate_structure(self) -> None:
        """Test counter_rate(max(field)) produces correct fullReference structure."""
        fixture = load_fixture('formula-counter-rate-max.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='counter_rate(max(postgresql.operations))')
        result = compile_lens_metric(metric)

        # Should have 2 helper columns: aggregation (max) + fullReference (counter_rate)
        assert len(result.helper_columns) == 2

        # Find the aggregation and fullReference columns
        agg_col = None
        full_ref_col = None
        for col in result.helper_columns.values():
            if col.operationType == 'max':
                agg_col = col
            elif col.operationType == 'counter_rate':
                full_ref_col = col

        assert agg_col is not None, 'Should have max aggregation column'
        assert full_ref_col is not None, 'Should have counter_rate fullReference column'

        # Verify timeScale is set for counter_rate
        assert full_ref_col.timeScale == 's', 'counter_rate should have timeScale=s'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

        # Verify fixture has same structure
        fixture_agg = fixture_columns['metric_formula_accessorX0']
        assert fixture_agg['operationType'] == 'max'
        assert fixture_agg['sourceField'] == 'postgresql.operations'

        fixture_fullref = fixture_columns['metric_formula_accessorX1']
        assert fixture_fullref['operationType'] == 'counter_rate'
        assert fixture_fullref['timeScale'] == 's'
        assert fixture_fullref['references'] == ['metric_formula_accessorX0']

    def test_cumulative_sum_structure(self) -> None:
        """Test cumulative_sum(count()) produces correct structure."""
        fixture = load_fixture('formula-cumulative-sum-count.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='cumulative_sum(count())')
        result = compile_lens_metric(metric)

        # Should have 2 helper columns: aggregation (count) + fullReference (cumulative_sum)
        assert len(result.helper_columns) == 2

        # Verify fixture structure matches pattern
        fixture_agg = fixture_columns['metric_formula_accessorX0']
        assert fixture_agg['operationType'] == 'count'
        assert fixture_agg['sourceField'] == '___records___'

        fixture_fullref = fixture_columns['metric_formula_accessorX1']
        assert fixture_fullref['operationType'] == 'cumulative_sum'
        assert fixture_fullref['references'] == ['metric_formula_accessorX0']

    def test_differences_structure(self) -> None:
        """Test differences(sum(bytes)) produces correct structure."""
        fixture = load_fixture('formula-differences-sum.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='differences(sum(bytes))')
        result = compile_lens_metric(metric)

        # Should have 2 helper columns
        assert len(result.helper_columns) == 2

        # Verify fixture structure
        fixture_agg = fixture_columns['metric_formula_accessorX0']
        assert fixture_agg['operationType'] == 'sum'
        assert fixture_agg['sourceField'] == 'bytes'

        fixture_fullref = fixture_columns['metric_formula_accessorX1']
        assert fixture_fullref['operationType'] == 'differences'

    def test_moving_average_with_window(self) -> None:
        """Test moving_average(average(bytes), window=5) has window parameter."""
        fixture = load_fixture('formula-moving-average.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='moving_average(average(bytes), window=5)')
        result = compile_lens_metric(metric)

        # Should have 2 helper columns
        assert len(result.helper_columns) == 2

        # Find the moving_average column
        moving_avg_col = None
        for col in result.helper_columns.values():
            if col.operationType == 'moving_average':
                moving_avg_col = col
                break

        assert moving_avg_col is not None
        # Verify window parameter is set
        assert moving_avg_col.params.window == 5  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

        # Verify fixture has window param
        fixture_fullref = fixture_columns['metric_formula_accessorX1']
        assert fixture_fullref['operationType'] == 'moving_average'
        assert fixture_fullref['params']['window'] == 5

    def test_math_division_structure(self) -> None:
        """Test sum(bytes) / count() produces math column with tinymathAst."""
        fixture = load_fixture('formula-math-division.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='sum(bytes) / count()')
        result = compile_lens_metric(metric)

        # Should have 3 helper columns: 2 aggregations + 1 math column
        assert len(result.helper_columns) == 3

        # Find the math column
        math_col = None
        for col in result.helper_columns.values():
            if col.operationType == 'math':
                math_col = col
                break

        assert math_col is not None
        # Verify tinymathAst structure
        ast = math_col.params.tinymathAst  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert ast['name'] == 'divide'
        assert ast['type'] == 'function'
        assert len(ast['args']) == 2

        # Verify fixture has same structure
        fixture_math = fixture_columns['metric_formula_accessorX2']
        assert fixture_math['operationType'] == 'math'
        assert fixture_math['params']['tinymathAst']['name'] == 'divide'

    def test_kql_filter_structure(self) -> None:
        """Test formula with kql filter has filter on aggregation column."""
        fixture = load_fixture('formula-with-kql-filter.json')
        fixture_columns = get_columns_from_fixture(fixture)

        # The fixture uses sum(bytes, kql='status: success')
        metric = LensFormulaMetric(formula="count(kql='log.level: error')")
        result = compile_lens_metric(metric)

        # Find the aggregation column with filter
        agg_col = None
        for col in result.helper_columns.values():
            if col.operationType == 'count':
                agg_col = col
                break

        assert agg_col is not None
        # Verify filter is set
        assert agg_col.filter is not None
        assert agg_col.filter.query == 'log.level: error'
        assert agg_col.filter.language == 'kuery'

        # Verify fixture structure (different formula but same pattern)
        fixture_agg = fixture_columns['metric_formula_accessorX0']
        assert 'filter' in fixture_agg
        assert fixture_agg['filter']['language'] == 'kuery'

    def test_complex_counter_rates_structure(self) -> None:
        """Test complex formula with multiple counter_rates produces correct structure."""
        fixture = load_fixture('formula-complex-counter-rates.json')
        fixture_columns = get_columns_from_fixture(fixture)

        formula = '(counter_rate(max(postgresql.rows_fetched)) + counter_rate(max(postgresql.rows_returned))) / 2'
        metric = LensFormulaMetric(formula=formula)
        result = compile_lens_metric(metric)

        # Should have 5 helper columns:
        # - 2 aggregations (max for each field)
        # - 2 fullReferences (counter_rate for each)
        # - 1 math column for the division
        assert len(result.helper_columns) == 5

        # Count column types
        agg_count = 0
        fullref_count = 0
        math_count = 0
        for col in result.helper_columns.values():
            if col.operationType == 'max':
                agg_count += 1
            elif col.operationType == 'counter_rate':
                fullref_count += 1
            elif col.operationType == 'math':
                math_count += 1

        assert agg_count == 2, 'Should have 2 max aggregations'
        assert fullref_count == 2, 'Should have 2 counter_rate operations'
        assert math_count == 1, 'Should have 1 math column'

        # Verify fixture has same structure
        assert len(fixture_columns) == 6  # 5 helpers + 1 formula


class TestColumnOrderMatchesKibana:
    """Test that column order follows Kibana's pattern."""

    def test_simple_aggregation_order(self) -> None:
        """Aggregation columns come before formula column."""
        fixture = load_fixture('formula-simple-average.json')
        order = get_column_order_from_fixture(fixture)

        # Pattern: X0 (agg) -> formula
        assert order == ['metric_formula_accessorX0', 'metric_formula_accessor']

    def test_fullreference_order(self) -> None:
        """Aggregation, fullReference, then formula column."""
        fixture = load_fixture('formula-counter-rate-max.json')
        order = get_column_order_from_fixture(fixture)

        # Pattern: X0 (agg) -> X1 (fullRef) -> formula
        assert order == [
            'metric_formula_accessorX0',
            'metric_formula_accessorX1',
            'metric_formula_accessor',
        ]

    def test_math_column_order(self) -> None:
        """Aggregations, then math column, then formula column."""
        fixture = load_fixture('formula-math-division.json')
        order = get_column_order_from_fixture(fixture)

        # Pattern: X0 (agg) -> X1 (agg) -> X2 (math) -> formula
        assert order == [
            'metric_formula_accessorX0',
            'metric_formula_accessorX1',
            'metric_formula_accessorX2',
            'metric_formula_accessor',
        ]


class TestFormulaParserMatchesKibana:
    """Test that our parser extracts the same information Kibana does."""

    def test_source_field_extraction(self) -> None:
        """Verify source field is correctly extracted."""
        fixture = load_fixture('formula-counter-rate-max.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='counter_rate(max(postgresql.operations))')
        result = compile_lens_metric(metric)

        # Find max column
        max_col = None
        for col in result.helper_columns.values():
            if col.operationType == 'max':
                max_col = col
                break

        assert max_col is not None
        assert max_col.sourceField == 'postgresql.operations'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

        # Matches fixture
        assert fixture_columns['metric_formula_accessorX0']['sourceField'] == 'postgresql.operations'

    def test_count_uses_records_field(self) -> None:
        """Verify count() uses ___records___ as source field."""
        fixture = load_fixture('formula-cumulative-sum-count.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='cumulative_sum(count())')
        result = compile_lens_metric(metric)

        # Find count column
        count_col = None
        for col in result.helper_columns.values():
            if col.operationType == 'count':
                count_col = col
                break

        assert count_col is not None
        assert count_col.sourceField == '___records___'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

        # Matches fixture
        assert fixture_columns['metric_formula_accessorX0']['sourceField'] == '___records___'

    def test_labels_match_kibana_pattern(self) -> None:
        """Verify labels follow Kibana's 'Part of {formula}' pattern."""
        fixture = load_fixture('formula-counter-rate-max.json')
        fixture_columns = get_columns_from_fixture(fixture)

        metric = LensFormulaMetric(formula='counter_rate(max(postgresql.operations))')
        result = compile_lens_metric(metric)

        # All helper columns should have 'Part of {formula}' label
        for col in result.helper_columns.values():
            assert col.label.startswith('Part of ')
            assert 'counter_rate(max(postgresql.operations))' in col.label

        # Verify fixture has same pattern
        assert fixture_columns['metric_formula_accessorX0']['label'].startswith('Part of ')
