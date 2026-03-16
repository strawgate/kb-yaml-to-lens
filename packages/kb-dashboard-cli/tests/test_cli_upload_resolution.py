"""Tests for upload-time data view ID resolution."""

import json

import pytest

from dashboard_compiler.cli_local import (
    _collect_index_pattern_titles_from_ndjson,
    _resolve_index_pattern_titles_in_ndjson,
)


def test_collect_index_pattern_titles_from_ndjson() -> None:
    """Collect non-UUID index-pattern IDs from references and layer indexPatternId."""
    ndjson = '\n'.join(
        [
            json.dumps(
                {
                    'type': 'lens',
                    'references': [{'type': 'index-pattern', 'id': 'logs-*'}],
                    'attributes': {
                        'state': {
                            'datasourceStates': {
                                'formBased': {
                                    'layers': {
                                        'layer-1': {
                                            'indexPatternId': 'metrics-*',
                                        }
                                    }
                                }
                            }
                        }
                    },
                }
            ),
            json.dumps(
                {
                    'type': 'lens',
                    'references': [{'type': 'index-pattern', 'id': '27a3148b-d1d4-4455-8acf-e63c94071a5b'}],
                }
            ),
            '',
        ]
    )

    assert _collect_index_pattern_titles_from_ndjson(ndjson) == {'logs-*', 'metrics-*'}


def test_resolve_index_pattern_titles_in_ndjson() -> None:
    """Rewrite references and formBased layer indexPatternId using resolved IDs."""
    ndjson = '\n'.join(
        [
            json.dumps(
                {
                    'type': 'lens',
                    'references': [{'type': 'index-pattern', 'id': 'logs-*'}],
                    'attributes': {
                        'state': {
                            'datasourceStates': {
                                'formBased': {
                                    'layers': {
                                        'layer-1': {
                                            'indexPatternId': 'logs-*',
                                        }
                                    }
                                }
                            }
                        }
                    },
                }
            ),
            '',
        ]
    )
    resolved = _resolve_index_pattern_titles_in_ndjson(ndjson, {'logs-*': 'uuid-logs'})
    saved_object = json.loads(resolved.strip())
    assert saved_object['references'][0]['id'] == 'uuid-logs'
    assert saved_object['attributes']['state']['datasourceStates']['formBased']['layers']['layer-1']['indexPatternId'] == 'uuid-logs'


def test_resolve_index_pattern_titles_in_ndjson_raises_for_missing_titles() -> None:
    """Fail fast when an index-pattern title cannot be resolved to a saved object ID."""
    ndjson = json.dumps({'type': 'lens', 'references': [{'type': 'index-pattern', 'id': 'logs-*'}]}) + '\n'
    with pytest.raises(ValueError, match='Could not resolve data view name'):
        _resolve_index_pattern_titles_in_ndjson(ndjson, {})
