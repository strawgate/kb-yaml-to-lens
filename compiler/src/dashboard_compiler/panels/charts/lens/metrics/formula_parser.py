"""Formula parser for Kibana Lens tinymath expressions.

This module parses Kibana Lens formula strings and generates the helper columns
required for proper rendering, including aggregation columns, math columns with
tinymathAST, and proper reference chains.

Based on Kibana's tinymath grammar:
https://github.com/elastic/kibana/blob/main/src/platform/packages/private/kbn-tinymath/src/grammar.peggy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import tatsu

# TatSu grammar for Kibana Lens tinymath expressions
# Ported from Kibana's Peggy grammar with TatSu-specific syntax
TINYMATH_GRAMMAR = r"""
@@grammar::TinyMath
@@whitespace :: /\s*/
@@left_recursion :: False

start = expression $ ;

expression
    = comparison
    | math_operation
    | expression_group
    ;

comparison
    = left:math_operation op:comp_op right:math_operation
    ;

comp_op
    = ">=" | "<=" | "==" | ">" | "<"
    ;

math_operation
    = add_subtract
    ;

add_subtract
    = left:multiply_divide {op:("+" | "-") ~ right:multiply_divide}*
    ;

multiply_divide
    = left:factor {op:("*" | "/") ~ right:factor}*
    ;

factor
    = group
    | function
    | literal
    ;

group
    = "(" ~ @:math_operation ")"
    ;

expression_group
    = "(" ~ @:expression ")"
    ;

function
    = name:function_name "(" ~ args:[argument_list] ")"
    ;

function_name
    = /[a-zA-Z_][a-zA-Z0-9_]*/
    ;

argument_list
    = args:",".{ argument }+ [","]
    ;

argument
    = named_argument
    | expression
    ;

named_argument
    = name:argument_name "=" ~ value:argument_value
    ;

argument_name
    = /[a-zA-Z_][a-zA-Z0-9_]*/
    ;

argument_value
    = quoted_string
    | number
    ;

literal
    = number
    | variable
    ;

variable
    = quoted_string
    | unquoted_variable
    ;

quoted_string
    = /\'[^\']*\'/
    | /\"[^\"]*\"/
    ;

unquoted_variable
    = /[a-zA-Z0-9._@\[\]\-]+/
    ;

number
    = /-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/
    ;
"""

# Kibana aggregation functions that require helper columns
KIBANA_AGGREGATIONS = frozenset(
    {
        'average',
        'avg',
        'count',
        'counter_rate',
        'cumulative_sum',
        'differences',
        'last_value',
        'max',
        'median',
        'min',
        'moving_average',
        'normalize',
        'overall_average',
        'overall_max',
        'overall_min',
        'overall_sum',
        'percentile',
        'percentile_rank',
        'standard_deviation',
        'sum',
        'time_scale',
        'unique_count',
    }
)

# Mapping from formula function names to Kibana operationType
FORMULA_TO_OPERATION_TYPE = {
    'average': 'average',
    'avg': 'average',
    'count': 'count',
    'counter_rate': 'counter_rate',
    'cumulative_sum': 'cumulative_sum',
    'differences': 'differences',
    'last_value': 'last_value',
    'max': 'max',
    'median': 'median',
    'min': 'min',
    'moving_average': 'moving_average',
    'normalize': 'normalize',
    'overall_average': 'overall_average',
    'overall_max': 'overall_max',
    'overall_min': 'overall_min',
    'overall_sum': 'overall_sum',
    'percentile': 'percentile',
    'percentile_rank': 'percentile_rank',
    'standard_deviation': 'standard_deviation',
    'sum': 'sum',
    'time_scale': 'time_scale',
    'unique_count': 'unique_count',
}

# Binary operator to tinymath function name mapping
OPERATOR_TO_FUNCTION = {
    '+': 'add',
    '-': 'subtract',
    '*': 'multiply',
    '/': 'divide',
    '>': 'gt',
    '<': 'lt',
    '>=': 'gte',
    '<=': 'lte',
    '==': 'eq',
}


@dataclass
class AggregationInfo:
    """Information about an aggregation function extracted from a formula."""

    function_name: str
    """The aggregation function name (e.g., 'average', 'sum', 'count')."""

    operation_type: str
    """The Kibana operationType for this aggregation."""

    source_field: str | None
    """The field being aggregated (None for count without field)."""

    filter_query: str | None
    """Optional KQL filter (from kql= argument)."""

    percentile: int | None
    """Percentile value for percentile aggregation."""

    position: tuple[int, int]
    """(start, end) character positions in the original formula."""

    text: str
    """The original text of this aggregation in the formula."""


@dataclass
class FormulaParseResult:
    """Result of parsing a Lens formula."""

    aggregations: list[AggregationInfo] = field(default_factory=list)
    """List of aggregation functions found in the formula."""

    tinymath_ast: Any = None
    """The tinymathAST structure with column references substituted."""

    formula_text: str = ''
    """The original formula text."""

    is_simple_literal: bool = False
    """True if the formula is just a number literal (no aggregations)."""


def _walk_ast(node: Any, aggregations: list[AggregationInfo], formula_text: str) -> Any:  # noqa: PLR0911, PLR0912
    """Recursively walk the AST and collect aggregations.

    Args:
        node: Current AST node
        aggregations: List to append found aggregations to
        formula_text: Original formula text for position tracking

    Returns:
        Transformed node with aggregation references

    """
    if node is None:
        return None

    if isinstance(node, str):
        # Check if it's a number string
        try:
            if '.' in node or 'e' in node.lower():
                return float(node)
            return int(node)
        except ValueError:
            # It's a variable/field reference
            return node.strip('\'"')

    if isinstance(node, (int, float)):
        return node

    if isinstance(node, list):
        return [_walk_ast(item, aggregations, formula_text) for item in node]

    if not isinstance(node, dict):
        return node

    # Check if this is a function node
    if 'name' in node and 'parseinfo' in node:
        func_name = node['name']

        # Check if it's a Kibana aggregation
        if func_name.lower() in KIBANA_AGGREGATIONS:
            agg_info = _extract_aggregation_info(func_name, node.get('args'), formula_text, node)
            aggregations.append(agg_info)
            return {'type': 'aggregation_ref', 'index': len(aggregations) - 1}

        # For other functions, walk the arguments
        walked_args = _walk_ast(node.get('args'), aggregations, formula_text)
        return {
            'type': 'function',
            'name': func_name,
            'args': walked_args if walked_args else [],
        }

    # Handle binary operations (add_subtract, multiply_divide)
    if 'left' in node:
        left = _walk_ast(node['left'], aggregations, formula_text)
        result = left

        # Check for operators
        if node.get('op'):
            ops = node['op'] if isinstance(node['op'], list) else [node['op']]
            rights = node.get('right', [])
            rights = rights if isinstance(rights, list) else [rights]

            for op, right_node in zip(ops, rights, strict=False):
                right = _walk_ast(right_node, aggregations, formula_text)
                result = {
                    'type': 'function',
                    'name': OPERATOR_TO_FUNCTION.get(op, op),
                    'args': [result, right],
                }
        return result

    # Handle comparison operations
    if 'left' in node and 'right' in node and 'op' in node:
        left = _walk_ast(node['left'], aggregations, formula_text)
        right = _walk_ast(node['right'], aggregations, formula_text)
        op = node['op']
        return {
            'type': 'function',
            'name': OPERATOR_TO_FUNCTION.get(op, op),
            'args': [left, right],
        }

    # For other dict-like nodes, recursively walk
    result = {}
    for key, value in node.items():
        if key != 'parseinfo':
            result[key] = _walk_ast(value, aggregations, formula_text)
    return result


def _extract_field_from_expr(expr: Any) -> str | None:
    """Extract field name from an expression node.

    TatSu wraps simple expressions in nested structures like:
    {'left': {'left': 'field.name', ...}, ...}

    This function unwraps them to get the actual field name.
    """
    if expr is None:
        return None

    if isinstance(expr, str):
        return expr.strip('\'"')

    if isinstance(expr, dict):
        # Check for 'left' key (TatSu binary operation wrapper)
        if 'left' in expr:
            return _extract_field_from_expr(expr['left'])
        # Could be a function call or other structure
        return None

    return None


def _extract_aggregation_info(  # noqa: PLR0912
    name: str,
    args: Any,
    formula_text: str,
    node: dict[str, Any],
) -> AggregationInfo:
    """Extract aggregation information from function arguments."""
    source_field: str | None = None
    filter_query: str | None = None
    percentile: int | None = None

    # Flatten the args structure from TatSu
    flat_args = _flatten_args(args)

    for arg in flat_args:
        if isinstance(arg, dict):
            # Check for named argument (kql=, lucene=, etc.)
            if 'name' in arg and 'value' in arg:
                arg_name = arg['name']
                arg_value = arg['value']
                if isinstance(arg_value, str):
                    arg_value = arg_value.strip('\'"')

                if arg_name == 'field':
                    source_field = arg_value
                elif arg_name in {'kql', 'lucene'}:
                    filter_query = arg_value
                elif arg_name == 'percentile':
                    percentile = int(arg_value) if arg_value else None
            elif source_field is None:
                # Try to extract field from expression wrapper
                extracted = _extract_field_from_expr(arg)
                if extracted and not extracted.isdigit():
                    source_field = extracted
        elif isinstance(arg, str):
            # First non-named string argument is typically the field
            cleaned = arg.strip('\'"')
            if source_field is None and cleaned and not cleaned.isdigit():
                source_field = cleaned
        elif isinstance(arg, (int, float)) and name.lower() in ('percentile', 'percentile_rank') and percentile is None:
            percentile = int(arg)

    # Get position info from parseinfo if available
    start = 0
    end = len(formula_text)
    parseinfo = node.get('parseinfo')
    if parseinfo:
        try:
            start = parseinfo.pos
            end = parseinfo.endpos
        except (AttributeError, TypeError):
            pass

    # Extract the text for this aggregation
    text = formula_text[start:end] if end > start else str(node)

    return AggregationInfo(
        function_name=name.lower(),
        operation_type=FORMULA_TO_OPERATION_TYPE.get(name.lower(), name.lower()),
        source_field=source_field,
        filter_query=filter_query,
        percentile=percentile,
        position=(start, end),
        text=text,
    )


def _flatten_args(args: Any) -> list[Any]:
    """Flatten nested argument structures from TatSu."""
    if args is None:
        return []
    if isinstance(args, dict):
        if 'args' in args:
            return _flatten_args(args['args'])
        return [args]
    if isinstance(args, list):
        result = []
        for item in args:
            if isinstance(item, list):
                result.extend(_flatten_args(item))
            else:
                result.append(item)
        return result
    return [args]


def parse_formula(formula: str) -> FormulaParseResult:
    """Parse a Lens formula and extract aggregation information.

    Args:
        formula: The formula string to parse (e.g., "count() / 100")

    Returns:
        FormulaParseResult containing aggregations and AST structure.

    Raises:
        tatsu.exceptions.FailedParse: If the formula has syntax errors.

    """
    # Compile the grammar
    parser = tatsu.compile(TINYMATH_GRAMMAR)

    # Parse the formula
    ast = parser.parse(formula, parseinfo=True)

    # Walk the AST to collect aggregations
    aggregations: list[AggregationInfo] = []
    tinymath_ast = _walk_ast(ast, aggregations, formula)

    # Check if this is a simple literal (just a number, no aggregations)
    is_simple = len(aggregations) == 0 and isinstance(tinymath_ast, (int, float))

    return FormulaParseResult(
        aggregations=aggregations,
        tinymath_ast=tinymath_ast,
        formula_text=formula,
        is_simple_literal=is_simple,
    )


def build_tinymath_ast_with_refs(
    parse_result: FormulaParseResult,
    column_refs: dict[int, str],
) -> Any:
    """Build the final tinymathAST with column ID references substituted.

    Args:
        parse_result: The parsed formula result
        column_refs: Mapping from aggregation index to column ID

    Returns:
        The tinymathAST structure with column references.

    """
    if parse_result.is_simple_literal:
        return parse_result.tinymath_ast

    def substitute_refs(node: Any) -> Any:
        """Recursively substitute aggregation references with column IDs."""
        if isinstance(node, dict):
            if node.get('type') == 'aggregation_ref':
                idx = node['index']
                return column_refs.get(idx, f'unknown_{idx}')
            return {
                'type': node.get('type', 'function'),
                'name': node.get('name', ''),
                'args': [substitute_refs(arg) for arg in node.get('args', [])],
                'location': {'min': 0, 'max': len(parse_result.formula_text)},
                'text': parse_result.formula_text,
            }
        return node

    return substitute_refs(parse_result.tinymath_ast)
