"""Test ESQL query compilation and array format support."""

from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff

from dashboard_compiler.queries.compile import compile_esql_query
from dashboard_compiler.queries.config import ESQLQuery
from tests.conftest import DEEP_DIFF_DEFAULTS

if TYPE_CHECKING:
    from dashboard_compiler.queries.view import KbnESQLQuery

EXCLUDE_REGEX_PATHS = []


@pytest.mark.parametrize(
    ('config', 'expected_esql'),
    [
        # Test case 1: Simple string query (backward compatibility)
        ('FROM logs-* | LIMIT 10', 'FROM logs-* | LIMIT 10'),
        # Test case 2: Simple array with two elements
        (['FROM logs-*', 'LIMIT 10'], 'FROM logs-* | LIMIT 10'),
        # Test case 3: Complex multi-part query
        (
            ['FROM metrics-*', 'WHERE service.name == "api"', 'STATS avg_response = AVG(http.response.time)', 'LIMIT 100'],
            'FROM metrics-* | WHERE service.name == "api" | STATS avg_response = AVG(http.response.time) | LIMIT 100',
        ),
        # Test case 4: Single element array
        (['FROM logs-*'], 'FROM logs-*'),
        # Test case 5: Array with filter and aggregation
        (
            ['FROM logs-*', 'WHERE @timestamp > NOW() - 1h', 'STATS count BY service.name'],
            'FROM logs-* | WHERE @timestamp > NOW() - 1h | STATS count BY service.name',
        ),
    ],
    ids=[
        'String query (backward compatibility)',
        'Array with two elements',
        'Complex multi-part array query',
        'Single element array',
        'Array with filter and aggregation',
    ],
)
async def test_esql_query_formats(config: str | list[str], expected_esql: str) -> None:
    """Test that ESQL queries can be provided as strings or arrays and compile correctly."""
    esql_query = ESQLQuery.model_validate(config)

    # After validation, the root should always be a string (normalized)
    assert isinstance(esql_query.root, str)
    assert esql_query.root == expected_esql

    kbn_query: KbnESQLQuery = compile_esql_query(query=esql_query)
    kbn_query_as_dict = kbn_query.model_dump()

    desired_output = {'esql': expected_esql}
    assert DeepDiff(desired_output, kbn_query_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
