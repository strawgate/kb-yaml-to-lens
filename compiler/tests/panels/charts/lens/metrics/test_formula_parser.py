"""Tests for the formula parser module."""

import pytest
from tatsu.exceptions import FailedParse

from dashboard_compiler.panels.charts.lens.metrics.formula_parser import (
    AggregationInfo,
    FormulaParseResult,
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
        assert result.tinymath_ast is None
        assert result.formula_text == ''
        assert result.is_simple_literal is False

    def test_result_with_aggregations(self) -> None:
        """Test FormulaParseResult populated from parsing."""
        result = parse_formula("sum(field='bytes') + count()")
        assert len(result.aggregations) == 2
        assert result.formula_text == "sum(field='bytes') + count()"
        assert result.is_simple_literal is False
