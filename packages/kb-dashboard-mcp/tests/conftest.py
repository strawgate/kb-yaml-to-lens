"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock

import pytest

from kb_dashboard_tools.kibana_client import KibanaClient
from kb_dashboard_tools.models import (
    DataStreamIndex,
    DataStreamInfo,
    DataStreamsResponse,
    DataStreamTimestampField,
    EsqlColumn,
    EsqlResponse,
    GrokMatch,
    GrokPatternResponse,
    IngestSimulateDoc,
    IngestSimulateDocResult,
    IngestSimulateError,
    IngestSimulateResponse,
)


@pytest.fixture
def mock_kibana_client() -> AsyncMock:
    """Create a mock KibanaClient."""
    client = AsyncMock(spec=KibanaClient)

    client.execute_esql = AsyncMock()
    client.get_data_streams = AsyncMock()
    client.test_grok_pattern = AsyncMock()
    client.simulate_ingest = AsyncMock()
    client.close = AsyncMock()

    return client


@pytest.fixture
def sample_esql_response() -> EsqlResponse:
    """Sample ES|QL query response."""
    return EsqlResponse(
        columns=[
            EsqlColumn(name='@timestamp', type='date'),
            EsqlColumn(name='message', type='keyword'),
            EsqlColumn(name='level', type='keyword'),
        ],
        values=[
            ['2024-01-01T00:00:00Z', 'Test message 1', 'info'],
            ['2024-01-01T00:01:00Z', 'Test message 2', 'error'],
            ['2024-01-01T00:02:00Z', 'Test message 3', 'warn'],
        ],
    )


@pytest.fixture
def sample_data_stream_response() -> DataStreamsResponse:
    """Sample data stream listing response."""
    return DataStreamsResponse(
        data_streams=[
            DataStreamInfo(
                name='logs-nginx-default',
                timestamp_field=DataStreamTimestampField(name='@timestamp'),
                indices=[
                    DataStreamIndex(index_name='.ds-logs-nginx-default-2024.01.01-000001'),
                ],
            ),
            DataStreamInfo(
                name='metrics-system-default',
                timestamp_field=DataStreamTimestampField(name='@timestamp'),
                indices=[
                    DataStreamIndex(index_name='.ds-metrics-system-default-2024.01.01-000001'),
                ],
            ),
        ],
    )


@pytest.fixture
def sample_grok_match_response() -> GrokPatternResponse:
    """Sample grok pattern match response."""
    return GrokPatternResponse(
        matches=[
            GrokMatch(
                matched=True,
                match={
                    'timestamp': '2024-01-01 00:00:00',
                    'level': 'INFO',
                    'message': 'Test log message',
                },
            )
        ]
    )


@pytest.fixture
def sample_dissect_response() -> IngestSimulateResponse:
    """Sample dissect simulation response."""
    return IngestSimulateResponse(
        docs=[
            IngestSimulateDocResult(
                doc=IngestSimulateDoc(
                    source={
                        'message': 'user=john action=login',
                        'user': 'john',
                        'action': 'login',
                    }
                )
            ),
            IngestSimulateDocResult(
                doc=IngestSimulateDoc(
                    source={
                        'message': 'user=jane action=logout',
                        'user': 'jane',
                        'action': 'logout',
                    }
                )
            ),
        ]
    )


@pytest.fixture
def sample_dissect_error_response() -> IngestSimulateResponse:
    """Sample dissect simulation response with error."""
    return IngestSimulateResponse(
        docs=[IngestSimulateDocResult(error=IngestSimulateError(reason='Unable to find match for dissect pattern'))]
    )
