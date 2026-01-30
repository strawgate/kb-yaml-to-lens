"""Test the compilation of filters from config models to view models."""

from typing import TYPE_CHECKING, Any

from inline_snapshot import snapshot
from pydantic import BaseModel

from kb_dashboard_core.queries.compile import compile_nonesql_query
from kb_dashboard_core.queries.types import (
    LegacyQueryTypes,
)

if TYPE_CHECKING:
    from kb_dashboard_core.queries.view import KbnQuery


class QueryHolder(BaseModel):
    """A holder for query configurations to be used in tests."""

    query: LegacyQueryTypes


def compile_query_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile query config and return dict for snapshot testing."""
    query_holder = QueryHolder.model_validate({'query': config})
    kbn_query: KbnQuery = compile_nonesql_query(query=query_holder.query)
    return kbn_query.model_dump()


async def test_kql_query_with_two_components() -> None:
    """Test KQL query with two components."""
    config = {'kql': 'aerospike.namespace.geojson.region_query_cells : * or @timestamp >= 5'}
    result = compile_query_snapshot(config)
    assert result == snapshot({'query': 'aerospike.namespace.geojson.region_query_cells : * or @timestamp >= 5', 'language': 'kuery'})


async def test_lucene_query_with_two_components() -> None:
    """Test Lucene query with two components."""
    config = {'lucene': 'status:[400 TO 499] AND (extension:php OR extension:html)'}
    result = compile_query_snapshot(config)
    assert result == snapshot({'query': 'status:[400 TO 499] AND (extension:php OR extension:html)', 'language': 'lucene'})
