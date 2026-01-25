"""Pytest configuration and fixtures."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from dashboard_compiler.kibana_client import KibanaClient


@pytest.fixture
def mock_kibana_client() -> AsyncMock:
    """Create a mock KibanaClient."""
    client = AsyncMock(spec=KibanaClient)

    client.esql_query_raw = AsyncMock()
    client.get_data_streams = AsyncMock()
    client.test_grok_pattern = AsyncMock()
    client.simulate_ingest = AsyncMock()
    client.close = AsyncMock()

    return client


@pytest.fixture
def sample_esql_response() -> dict[str, Any]:
    """Sample ES|QL query response."""
    return {
        'columns': [
            {'name': '@timestamp', 'type': 'date'},
            {'name': 'message', 'type': 'keyword'},
            {'name': 'level', 'type': 'keyword'},
        ],
        'values': [
            ['2024-01-01T00:00:00Z', 'Test message 1', 'info'],
            ['2024-01-01T00:01:00Z', 'Test message 2', 'error'],
            ['2024-01-01T00:02:00Z', 'Test message 3', 'warn'],
        ],
    }


@pytest.fixture
def sample_data_stream_response() -> dict[str, Any]:
    """Sample data stream listing response."""
    return {
        'data_streams': [
            {
                'name': 'logs-nginx-default',
                'timestamp_field': {'name': '@timestamp'},
                'indices': [
                    {'index_name': '.ds-logs-nginx-default-2024.01.01-000001'},
                ],
            },
            {
                'name': 'metrics-system-default',
                'timestamp_field': {'name': '@timestamp'},
                'indices': [
                    {'index_name': '.ds-metrics-system-default-2024.01.01-000001'},
                ],
            },
        ],
    }


@pytest.fixture
def sample_grok_match_response() -> dict[str, Any]:
    """Sample grok pattern match response."""
    return {
        'matches': [
            {
                'match': {
                    'timestamp': '2024-01-01 00:00:00',
                    'level': 'INFO',
                    'message': 'Test log message',
                }
            }
        ]
    }


@pytest.fixture
def sample_dissect_response() -> dict[str, Any]:
    """Sample dissect simulation response."""
    return {
        'docs': [
            {
                'doc': {
                    '_source': {
                        'message': 'user=john action=login',
                        'user': 'john',
                        'action': 'login',
                    }
                }
            },
            {
                'doc': {
                    '_source': {
                        'message': 'user=jane action=logout',
                        'user': 'jane',
                        'action': 'logout',
                    }
                }
            },
        ]
    }


@pytest.fixture
def sample_dissect_error_response() -> dict[str, Any]:
    """Sample dissect simulation response with error."""
    return {
        'docs': [
            {
                'error': {
                    'reason': 'Unable to find match for dissect pattern',
                }
            }
        ]
    }
