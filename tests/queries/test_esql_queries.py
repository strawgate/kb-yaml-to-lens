"""Test ESQL query compilation and array format support."""

from typing import TYPE_CHECKING

from inline_snapshot import snapshot

from dashboard_compiler.queries.compile import compile_esql_query
from dashboard_compiler.queries.config import ESQLQuery

if TYPE_CHECKING:
    from dashboard_compiler.queries.view import KbnESQLQuery


async def test_esql_string_query_backward_compatibility() -> None:
    """Test that ESQL queries can be provided as strings (backward compatibility)."""
    config = 'FROM logs-* | LIMIT 10'
    expected_esql = 'FROM logs-* | LIMIT 10'

    esql_query = ESQLQuery.model_validate(config)

    # After validation, the root should always be a string (normalized)
    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert kbn_query_as_dict == snapshot({'esql': 'FROM logs-* | LIMIT 10'})


async def test_esql_array_with_two_elements() -> None:
    """Test ESQL array with two elements."""
    config = ['FROM logs-*', 'LIMIT 10']
    expected_esql = 'FROM logs-* | LIMIT 10'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert kbn_query_as_dict == snapshot({'esql': 'FROM logs-* | LIMIT 10'})


async def test_esql_complex_multi_part_array_query() -> None:
    """Test ESQL complex multi-part array query."""
    config = ['FROM metrics-*', 'WHERE service.name == "api"', 'STATS avg_response = AVG(http.response.time)', 'LIMIT 100']
    expected_esql = 'FROM metrics-* | WHERE service.name == "api" | STATS avg_response = AVG(http.response.time) | LIMIT 100'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert kbn_query_as_dict == snapshot(
        {'esql': 'FROM metrics-* | WHERE service.name == "api" | STATS avg_response = AVG(http.response.time) | LIMIT 100'}
    )


async def test_esql_single_element_array() -> None:
    """Test ESQL single element array."""
    config = ['FROM logs-*']
    expected_esql = 'FROM logs-*'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert kbn_query_as_dict == snapshot({'esql': 'FROM logs-*'})


async def test_esql_array_with_filter_and_aggregation() -> None:
    """Test ESQL array with filter and aggregation."""
    config = ['FROM logs-*', 'WHERE @timestamp > NOW() - 1h', 'STATS count BY service.name']
    expected_esql = 'FROM logs-* | WHERE @timestamp > NOW() - 1h | STATS count BY service.name'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert kbn_query_as_dict == snapshot({'esql': 'FROM logs-* | WHERE @timestamp > NOW() - 1h | STATS count BY service.name'})


async def test_esql_nested_array_from_yaml_anchor() -> None:
    """Test ESQL nested arrays (simulating YAML anchor expansion).

    When YAML anchors reference arrays and are combined with additional elements,
    they create nested lists. This test verifies the flattening behavior.
    """
    # Simulates what happens when you use:
    # .base: &base
    #   - FROM logs-*
    #   - WHERE status == 200
    # query:
    #   - *base
    #   - STATS count = COUNT()
    config: list[str | list[str]] = [['FROM logs-*', 'WHERE status == 200'], 'STATS count = COUNT()']
    expected_esql = 'FROM logs-* | WHERE status == 200 | STATS count = COUNT()'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert kbn_query_as_dict == snapshot({'esql': 'FROM logs-* | WHERE status == 200 | STATS count = COUNT()'})


async def test_esql_deeply_nested_arrays() -> None:
    """Test ESQL deeply nested arrays are properly flattened."""
    # Simulates multiple levels of anchor composition
    config: list[str | list[str | list[str]]] = [
        [['FROM logs-*'], 'WHERE env == "prod"'],
        'WHERE status >= 400',
        'STATS errors = COUNT()',
    ]
    expected_esql = 'FROM logs-* | WHERE env == "prod" | WHERE status >= 400 | STATS errors = COUNT()'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql


async def test_esql_multiple_anchor_references() -> None:
    """Test ESQL with multiple anchor references in the same query."""
    # Simulates:
    # .source: &source
    #   - FROM metrics-*
    # .filters: &filters
    #   - WHERE host.name IS NOT NULL
    # query:
    #   - *source
    #   - *filters
    #   - STATS avg = AVG(cpu.pct)
    config: list[str | list[str]] = [
        ['FROM metrics-*'],
        ['WHERE host.name IS NOT NULL'],
        'STATS avg = AVG(cpu.pct)',
    ]
    expected_esql = 'FROM metrics-* | WHERE host.name IS NOT NULL | STATS avg = AVG(cpu.pct)'

    esql_query = ESQLQuery.model_validate(config)

    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql
