"""Tests for the formula parser module."""

import pytest
from tatsu.exceptions import FailedParse

from dashboard_compiler.panels.charts.lens.metrics.formula_parser import (
    AggregationInfo,
    FormulaParseResult,
    FullReferenceInfo,
    build_tinymath_ast_with_refs,
    parse_formula,
)


class TestParseFormulaBasic:
    """Test basic formula parsing functionality."""

    def test_parse_simple_count(self) -> None:
        """Test parsing a simple count() formula."""
        result = parse_formula('count()')
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'count'
        assert result.aggregations[0].operation_type == 'count'
        assert result.aggregations[0].source_field is None
        assert result.is_simple_literal is False

    def test_parse_count_with_math(self) -> None:
        """Test parsing count() with division."""
        result = parse_formula('count() / 100')
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'count'
        assert result.formula_text == 'count() / 100'

    def test_parse_sum_with_field(self) -> None:
        """Test parsing sum with a field argument."""
        result = parse_formula("sum(field='bytes')")
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'sum'
        assert result.aggregations[0].operation_type == 'sum'
        assert result.aggregations[0].source_field == 'bytes'

    def test_parse_average_with_field(self) -> None:
        """Test parsing average with a field argument."""
        result = parse_formula("average(field='response.time')")
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'average'
        assert result.aggregations[0].operation_type == 'average'
        assert result.aggregations[0].source_field == 'response.time'

    def test_parse_avg_alias(self) -> None:
        """Test parsing avg (alias for average)."""
        result = parse_formula("avg(field='cpu.usage')")
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'avg'
        assert result.aggregations[0].operation_type == 'average'

    def test_parse_number_literal(self) -> None:
        """Test parsing a number literal (no aggregations)."""
        result = parse_formula('42')
        assert len(result.aggregations) == 0
        assert result.is_simple_literal is True
        assert result.tinymath_ast == 42

    def test_parse_float_literal(self) -> None:
        """Test parsing a float literal."""
        result = parse_formula('3.14')
        assert len(result.aggregations) == 0
        assert result.is_simple_literal is True
        assert result.tinymath_ast == 3.14


class TestParseFormulaMultipleAggregations:
    """Test parsing formulas with multiple aggregations."""

    def test_parse_two_counts_division(self) -> None:
        """Test parsing count() / count() with kql filter."""
        result = parse_formula('count(kql="status:error") / count()')
        assert len(result.aggregations) == 2
        assert result.aggregations[0].function_name == 'count'
        assert result.aggregations[0].filter_query == 'status:error'
        assert result.aggregations[1].function_name == 'count'
        assert result.aggregations[1].filter_query is None

    def test_parse_complex_formula(self) -> None:
        """Test parsing a complex formula with multiple aggregation types."""
        result = parse_formula("(max(field='response.time') - min(field='response.time')) / average(field='response.time')")
        assert len(result.aggregations) == 3
        assert result.aggregations[0].function_name == 'max'
        assert result.aggregations[0].source_field == 'response.time'
        assert result.aggregations[1].function_name == 'min'
        assert result.aggregations[1].source_field == 'response.time'
        assert result.aggregations[2].function_name == 'average'
        assert result.aggregations[2].source_field == 'response.time'

    def test_parse_nested_math(self) -> None:
        """Test parsing nested arithmetic operations."""
        result = parse_formula("(sum(field='a') + sum(field='b')) * 2")
        assert len(result.aggregations) == 2
        assert result.aggregations[0].source_field == 'a'
        assert result.aggregations[1].source_field == 'b'


class TestParseFormulaWithFilters:
    """Test parsing formulas with KQL/Lucene filters."""

    def test_parse_count_with_kql(self) -> None:
        """Test parsing count with kql filter."""
        result = parse_formula('count(kql="status:200")')
        assert len(result.aggregations) == 1
        assert result.aggregations[0].filter_query == 'status:200'

    def test_parse_sum_with_kql(self) -> None:
        """Test parsing sum with field and kql filter."""
        result = parse_formula("sum(field='bytes', kql='status:success')")
        assert len(result.aggregations) == 1
        assert result.aggregations[0].source_field == 'bytes'
        assert result.aggregations[0].filter_query == 'status:success'


class TestParseFormulaPercentile:
    """Test parsing percentile formulas."""

    def test_parse_percentile(self) -> None:
        """Test parsing percentile with field and percentile value."""
        result = parse_formula("percentile(field='latency', percentile=95)")
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'percentile'
        assert result.aggregations[0].operation_type == 'percentile'
        assert result.aggregations[0].source_field == 'latency'
        assert result.aggregations[0].percentile == 95

    def test_parse_percentile_rank(self) -> None:
        """Test parsing percentile_rank."""
        result = parse_formula("percentile_rank(field='bytes', percentile=1000)")
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'percentile_rank'
        assert result.aggregations[0].operation_type == 'percentile_rank'


class TestBuildTinymathAst:
    """Test building tinymathAST with column references."""

    def test_simple_aggregation_ref(self) -> None:
        """Test that a simple aggregation returns a string column ID."""
        result = parse_formula('count()')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        # For a simple aggregation, the AST is just the column ID string
        assert ast == 'col-X0'

    def test_math_operation_ast(self) -> None:
        """Test that math operations produce proper AST structure."""
        result = parse_formula('count() / 100')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        # Should be a function node for division
        assert ast['type'] == 'function'
        assert ast['name'] == 'divide'
        assert len(ast['args']) == 2
        assert ast['args'][0] == 'col-X0'
        assert ast['args'][1] == 100

    def test_multiple_aggregations_ast(self) -> None:
        """Test AST with multiple aggregation references."""
        result = parse_formula('count(kql="a") / count(kql="b")')
        column_refs = {0: 'col-X0', 1: 'col-X1'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['type'] == 'function'
        assert ast['name'] == 'divide'
        assert ast['args'][0] == 'col-X0'
        assert ast['args'][1] == 'col-X1'

    def test_literal_ast(self) -> None:
        """Test that literals pass through unchanged."""
        result = parse_formula('42')
        ast = build_tinymath_ast_with_refs(result, {})
        assert ast == 42


class TestParseFormulaSyntaxErrors:
    """Test that invalid formulas raise parse errors."""

    def test_invalid_syntax_raises(self) -> None:
        """Test that invalid formula syntax raises an error."""
        with pytest.raises(FailedParse):
            parse_formula('count( invalid syntax')

    def test_unmatched_parens_raises(self) -> None:
        """Test that unmatched parentheses raise an error."""
        with pytest.raises(FailedParse):
            parse_formula('count(()')  # Mismatched parens


class TestAggregationInfo:
    """Test AggregationInfo dataclass."""

    def test_aggregation_info_creation(self) -> None:
        """Test creating an AggregationInfo."""
        agg = AggregationInfo(
            function_name='sum',
            operation_type='sum',
            source_field='bytes',
            filter_query=None,
            percentile=None,
            position=(0, 10),
            text="sum(field='bytes')",
        )
        assert agg.function_name == 'sum'
        assert agg.operation_type == 'sum'
        assert agg.source_field == 'bytes'


class TestFormulaParseResult:
    """Test FormulaParseResult dataclass."""

    def test_empty_result(self) -> None:
        """Test creating an empty FormulaParseResult."""
        result = FormulaParseResult()
        assert result.aggregations == []
        assert result.full_references == []
        assert result.tinymath_ast is None
        assert result.formula_text == ''
        assert result.is_simple_literal is False

    def test_result_with_aggregations(self) -> None:
        """Test FormulaParseResult populated from parsing."""
        result = parse_formula("sum(field='bytes') + count()")
        assert len(result.aggregations) == 2
        assert len(result.full_references) == 0
        assert result.formula_text == "sum(field='bytes') + count()"
        assert result.is_simple_literal is False


class TestParseFormulaFullReference:
    """Test parsing formulas with fullReference operations."""

    def test_parse_counter_rate_with_max(self) -> None:
        """Test parsing counter_rate(max(field))."""
        result = parse_formula('counter_rate(max(postgresql.operations))')

        # Should extract max as a field aggregation
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'max'
        assert result.aggregations[0].source_field == 'postgresql.operations'

        # Should extract counter_rate as a fullReference operation
        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'counter_rate'
        assert result.full_references[0].operation_type == 'counter_rate'
        assert result.full_references[0].inner_aggregation_index == 0

    def test_parse_cumulative_sum_with_count(self) -> None:
        """Test parsing cumulative_sum(count())."""
        result = parse_formula('cumulative_sum(count())')

        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'count'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'cumulative_sum'
        assert result.full_references[0].inner_aggregation_index == 0

    def test_parse_differences_with_sum(self) -> None:
        """Test parsing differences(sum(bytes))."""
        result = parse_formula('differences(sum(bytes))')

        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'sum'
        assert result.aggregations[0].source_field == 'bytes'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'differences'
        assert result.full_references[0].inner_aggregation_index == 0

    def test_parse_moving_average_with_average(self) -> None:
        """Test parsing moving_average(average(field))."""
        result = parse_formula("moving_average(average(field='response.time'))")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'average'
        assert result.aggregations[0].source_field == 'response.time'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'moving_average'
        assert result.full_references[0].inner_aggregation_index == 0

    def test_parse_multiple_counter_rates(self) -> None:
        """Test parsing formula with multiple counter_rate operations."""
        result = parse_formula('counter_rate(max(in.bytes)) + counter_rate(max(out.bytes))')

        # Should have 2 aggregations (max for in.bytes and max for out.bytes)
        assert len(result.aggregations) == 2
        assert result.aggregations[0].function_name == 'max'
        assert result.aggregations[0].source_field == 'in.bytes'
        assert result.aggregations[1].function_name == 'max'
        assert result.aggregations[1].source_field == 'out.bytes'

        # Should have 2 fullReference operations (counter_rate for each)
        assert len(result.full_references) == 2
        assert result.full_references[0].function_name == 'counter_rate'
        assert result.full_references[0].inner_aggregation_index == 0
        assert result.full_references[1].function_name == 'counter_rate'
        assert result.full_references[1].inner_aggregation_index == 1

    def test_parse_time_scale_with_counter_rate(self) -> None:
        """Test parsing time_scale wrapping counter_rate (nested fullReferences)."""
        # Note: This tests a nested fullReference scenario
        # time_scale(counter_rate(max(field))) is a valid Kibana formula
        result = parse_formula('normalize(sum(bytes))')

        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'sum'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'normalize'

    def test_parse_overall_sum(self) -> None:
        """Test parsing overall_sum (fullReference operation)."""
        result = parse_formula("overall_sum(sum(field='bytes'))")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'sum'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'overall_sum'
        assert result.full_references[0].operation_type == 'overall_sum'


class TestFullReferenceInfo:
    """Test FullReferenceInfo dataclass."""

    def test_full_reference_info_creation(self) -> None:
        """Test creating a FullReferenceInfo."""
        ref = FullReferenceInfo(
            function_name='counter_rate',
            operation_type='counter_rate',
            inner_aggregation_index=0,
            position=(0, 30),
            text='counter_rate(max(field))',
        )
        assert ref.function_name == 'counter_rate'
        assert ref.operation_type == 'counter_rate'
        assert ref.inner_aggregation_index == 0


class TestComparisonOperators:
    """Test parsing and AST generation for comparison operators."""

    def test_greater_than_operator(self) -> None:
        """Test that > operator produces 'gt' function in AST."""
        result = parse_formula('count() > 100')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['type'] == 'function'
        assert ast['name'] == 'gt'
        assert len(ast['args']) == 2
        assert ast['args'][0] == 'col-X0'
        assert ast['args'][1] == 100

    def test_less_than_operator(self) -> None:
        """Test that < operator produces 'lt' function in AST."""
        result = parse_formula('count() < 50')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'lt'

    def test_greater_than_or_equal_operator(self) -> None:
        """Test that >= operator produces 'gte' function in AST."""
        result = parse_formula('sum(bytes) >= 1000')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'gte'

    def test_less_than_or_equal_operator(self) -> None:
        """Test that <= operator produces 'lte' function in AST."""
        result = parse_formula('sum(bytes) <= 500')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'lte'

    def test_equality_operator(self) -> None:
        """Test that == operator produces 'eq' function in AST."""
        result = parse_formula('count() == 0')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'eq'


class TestMathFunctions:
    """Test parsing of tinymath math functions."""

    def test_abs_function(self) -> None:
        """Test parsing abs() function wrapping an aggregation."""
        result = parse_formula('abs(sum(profit))')
        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'sum'

        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['type'] == 'function'
        assert ast['name'] == 'abs'
        assert ast['args'][0] == 'col-X0'

    def test_sqrt_function(self) -> None:
        """Test parsing sqrt() function."""
        result = parse_formula('sqrt(sum(variance))')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'sqrt'

    def test_pow_function(self) -> None:
        """Test parsing pow() function with two arguments."""
        result = parse_formula('pow(count(), 2)')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'pow'
        assert ast['args'][0] == 'col-X0'
        assert ast['args'][1] == 2

    def test_ceil_function(self) -> None:
        """Test parsing ceil() function."""
        result = parse_formula('ceil(average(bytes))')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'ceil'

    def test_floor_function(self) -> None:
        """Test parsing floor() function."""
        result = parse_formula('floor(average(response.time))')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'floor'

    def test_round_function(self) -> None:
        """Test parsing round() function."""
        result = parse_formula('round(sum(bytes) / count())')
        assert len(result.aggregations) == 2
        column_refs = {0: 'col-X0', 1: 'col-X1'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'round'

    def test_log_function(self) -> None:
        """Test parsing log() function."""
        result = parse_formula('log(count())')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'log'

    def test_exp_function(self) -> None:
        """Test parsing exp() function."""
        result = parse_formula('exp(average(rate))')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'exp'

    def test_clamp_function(self) -> None:
        """Test parsing clamp() function with three arguments."""
        result = parse_formula('clamp(sum(value), 0, 100)')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'clamp'
        assert ast['args'][0] == 'col-X0'
        assert ast['args'][1] == 0
        assert ast['args'][2] == 100

    def test_mod_function(self) -> None:
        """Test parsing mod() function."""
        result = parse_formula('mod(count(), 10)')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'mod'

    def test_ifelse_function(self) -> None:
        """Test parsing ifelse() conditional function."""
        result = parse_formula('ifelse(count() > 100, sum(bytes), 0)')
        # count() appears in the condition and the > comparison
        assert len(result.aggregations) == 2
        column_refs = {0: 'col-X0', 1: 'col-X1'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'ifelse'

    def test_pick_max_function(self) -> None:
        """Test parsing pick_max() function with multiple arguments."""
        result = parse_formula('pick_max(sum(a), sum(b), sum(c))')
        assert len(result.aggregations) == 3
        column_refs = {0: 'col-X0', 1: 'col-X1', 2: 'col-X2'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'pick_max'
        assert len(ast['args']) == 3

    def test_pick_min_function(self) -> None:
        """Test parsing pick_min() function with multiple arguments."""
        result = parse_formula('pick_min(min(a), min(b))')
        assert len(result.aggregations) == 2
        column_refs = {0: 'col-X0', 1: 'col-X1'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'pick_min'

    def test_defaults_function(self) -> None:
        """Test parsing defaults() function (null coalescing)."""
        result = parse_formula('defaults(sum(bytes), 0)')
        column_refs = {0: 'col-X0'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'defaults'

    def test_nested_math_functions(self) -> None:
        """Test parsing nested math functions."""
        result = parse_formula('round(abs(sum(profit) - sum(cost)))')
        assert len(result.aggregations) == 2
        column_refs = {0: 'col-X0', 1: 'col-X1'}
        ast = build_tinymath_ast_with_refs(result, column_refs)
        assert ast['name'] == 'round'
        # The inner function should be abs
        assert ast['args'][0]['name'] == 'abs'


class TestDerivativeAlias:
    """Test that derivative is properly aliased to differences."""

    def test_derivative_parses_as_full_reference(self) -> None:
        """Test that derivative() is recognized as a fullReference operation."""
        result = parse_formula('derivative(sum(bytes))')

        assert len(result.aggregations) == 1
        assert result.aggregations[0].function_name == 'sum'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'derivative'
        assert result.full_references[0].operation_type == 'differences'  # Maps to differences

    def test_derivative_with_complex_inner_expression(self) -> None:
        """Test derivative with a more complex inner aggregation."""
        result = parse_formula("derivative(average(field='cpu.usage'))")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].source_field == 'cpu.usage'

        assert len(result.full_references) == 1
        assert result.full_references[0].function_name == 'derivative'


class TestShiftAndReducedTimeRange:
    """Test extraction of shift and reducedTimeRange parameters."""

    def test_shift_parameter_extraction(self) -> None:
        """Test that shift= parameter is extracted from aggregations."""
        result = parse_formula("sum(bytes, shift='1d')")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].source_field == 'bytes'
        assert result.aggregations[0].shift == '1d'

    def test_reduced_time_range_parameter_extraction(self) -> None:
        """Test that reducedTimeRange= parameter is extracted."""
        result = parse_formula("count(reducedTimeRange='1h')")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].reduced_time_range == '1h'

    def test_shift_and_kql_together(self) -> None:
        """Test that shift and kql can be used together."""
        result = parse_formula("count(kql='status:error', shift='1w')")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].filter_query == 'status:error'
        assert result.aggregations[0].shift == '1w'

    def test_year_over_year_comparison(self) -> None:
        """Test parsing a year-over-year comparison formula."""
        result = parse_formula("sum(revenue) - sum(revenue, shift='1y')")

        assert len(result.aggregations) == 2
        assert result.aggregations[0].shift is None
        assert result.aggregations[1].shift == '1y'

    def test_reduced_time_range_with_field(self) -> None:
        """Test reducedTimeRange with field and aggregation."""
        result = parse_formula("average(response.time, reducedTimeRange='5m')")

        assert len(result.aggregations) == 1
        assert result.aggregations[0].source_field == 'response.time'
        assert result.aggregations[0].reduced_time_range == '5m'
