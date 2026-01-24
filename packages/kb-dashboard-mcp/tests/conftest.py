"""Pytest configuration and fixtures."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from elasticsearch import AsyncElasticsearch


@pytest.fixture
def mock_es_client() -> AsyncMock:
    """Create a mock AsyncElasticsearch client."""
    client = AsyncMock(spec=AsyncElasticsearch)

    client.esql = MagicMock()
    client.esql.query = AsyncMock()

    client.indices = MagicMock()
    client.indices.get_data_stream = AsyncMock()

    client.text_structure = MagicMock()
    client.text_structure.test_grok_pattern = AsyncMock()

    client.ingest = MagicMock()
    client.ingest.simulate = AsyncMock()

    client.ping = AsyncMock()
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
