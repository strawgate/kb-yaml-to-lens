"""Test data for query compilation tests."""

CASE_KQL_QUERY = (
    {'kql': 'aerospike.namespace.geojson.region_query_cells : * or @timestamp >= 5'},
    {'query': 'aerospike.namespace.geojson.region_query_cells : * or @timestamp >= 5', 'language': 'kuery'},
)

CASE_LUCENE_QUERY = (
    {'lucene': 'status:[400 TO 499] AND (extension:php OR extension:html)'},
    {'query': 'status:[400 TO 499] AND (extension:php OR extension:html)', 'language': 'lucene'},
)

TEST_CASES = [CASE_KQL_QUERY, CASE_LUCENE_QUERY]

TEST_CASE_IDS = [
    'KQL Query with two components',
    'Lucene Query with two components',
]
