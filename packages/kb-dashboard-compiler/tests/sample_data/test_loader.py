"""Tests for sample data loader."""

from pathlib import Path
from unittest.mock import AsyncMock, create_autospec

import pytest

from dashboard_compiler.kibana_client import BulkItemError, BulkItemResult, BulkResponse, KibanaClient
from dashboard_compiler.sample_data.config import SampleData, TimestampTransform
from dashboard_compiler.sample_data.loader import (
    SampleDataLoadResult,
    load_sample_data,
    read_documents,
)


def test_read_documents_inline() -> None:
    """Test reading inline documents."""
    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test1'},
            {'@timestamp': '2024-01-01T01:00:00Z', 'message': 'test2'},
        ],
    )

    documents = read_documents(sample_data)

    assert len(documents) == 2
    assert documents[0]['message'] == 'test1'
    assert documents[1]['message'] == 'test2'


def test_read_documents_inline_missing_documents() -> None:
    """Test reading inline documents when documents field is None."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match='documents is required when source is inline'):
        _ = SampleData(
            source='inline',
            index_pattern='logs-*',
        )


def test_read_documents_file_missing_path() -> None:
    """Test reading from file when file_path is None."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match='file_path is required when source is file'):
        _ = SampleData(
            source='file',
            index_pattern='logs-*',
        )


def test_read_documents_ndjson(tmp_path: Path) -> None:
    """Test reading NDJSON file."""
    ndjson_file = tmp_path / 'sample.ndjson'
    _ = ndjson_file.write_text(
        '{"@timestamp": "2024-01-01T00:00:00Z", "message": "line1"}\n{"@timestamp": "2024-01-01T01:00:00Z", "message": "line2"}\n'
    )

    sample_data = SampleData(
        source='file',
        index_pattern='logs-*',
        file_path=ndjson_file,
    )

    documents = read_documents(sample_data)

    assert len(documents) == 2
    assert documents[0]['message'] == 'line1'
    assert documents[1]['message'] == 'line2'


def test_read_documents_file_not_found() -> None:
    """Test reading from non-existent file."""
    sample_data = SampleData(
        source='file',
        index_pattern='logs-*',
        file_path=Path('/nonexistent/sample.ndjson'),
    )

    with pytest.raises(ValueError, match='Sample data file not found'):
        _ = read_documents(sample_data)


def test_read_documents_relative_path(tmp_path: Path) -> None:
    """Test reading file with relative path."""
    ndjson_file = tmp_path / 'sample.ndjson'
    _ = ndjson_file.write_text('{"@timestamp": "2024-01-01T00:00:00Z"}\n')

    sample_data = SampleData(
        source='file',
        index_pattern='logs-*',
        file_path=Path('sample.ndjson'),
    )

    documents = read_documents(sample_data, base_path=tmp_path)

    assert len(documents) == 1


@pytest.mark.asyncio
async def test_load_sample_data_success() -> None:
    """Test loading sample data successfully via Kibana proxy."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)
    mock_bulk_response = BulkResponse(
        took=30,
        errors=False,
        items=[
            {'index': BulkItemResult(index='logs-sample', status=201)},
            {'index': BulkItemResult(index='logs-sample', status=201)},
        ],
    )
    mock_kibana_client.proxy_bulk = AsyncMock(return_value=mock_bulk_response)

    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test1'},
            {'@timestamp': '2024-01-01T01:00:00Z', 'message': 'test2'},
        ],
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is True
    assert result.success_count == 2
    assert len(result.errors) == 0

    mock_kibana_client.proxy_bulk.assert_called_once()
    call_args = mock_kibana_client.proxy_bulk.call_args
    actions = call_args[0][0]
    assert len(actions) == 2
    assert actions[0]['_index'] == 'logs-sample'
    assert actions[0]['pipeline'] == '_none'


@pytest.mark.asyncio
async def test_load_sample_data_with_errors() -> None:
    """Test loading sample data with errors via Kibana proxy."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)
    # Return bulk response with failed items
    mock_bulk_response = BulkResponse(
        took=30,
        errors=True,
        items=[
            {'index': BulkItemResult(index='logs-sample', status=201)},
            {
                'index': BulkItemResult(
                    index='logs-sample',
                    status=400,
                    error=BulkItemError(type='mapper_parsing_exception', reason='failed to parse'),
                )
            },
        ],
    )
    mock_kibana_client.proxy_bulk = AsyncMock(return_value=mock_bulk_response)

    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
        ],
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is False
    assert result.success_count == 1
    assert len(result.errors) == 1
    assert 'mapper_parsing_exception' in result.errors[0]


@pytest.mark.asyncio
async def test_load_sample_data_with_timestamp_transform() -> None:
    """Test loading sample data with timestamp transformation."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)
    mock_bulk_response = BulkResponse(
        took=15,
        errors=False,
        items=[{'index': BulkItemResult(index='logs-sample', status=201)}],
    )
    mock_kibana_client.proxy_bulk = AsyncMock(return_value=mock_bulk_response)

    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
        ],
        timestamp_transform=TimestampTransform(
            enabled=False,
        ),
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is True
    mock_kibana_client.proxy_bulk.assert_called_once()


@pytest.mark.asyncio
async def test_load_sample_data_with_index_template() -> None:
    """Test loading sample data with index template creation via Kibana proxy."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)
    mock_bulk_response = BulkResponse(
        took=15,
        errors=False,
        items=[{'index': BulkItemResult(index='logs-sample', status=201)}],
    )
    mock_kibana_client.proxy_bulk = AsyncMock(return_value=mock_bulk_response)
    mock_kibana_client.proxy_put_index_template = AsyncMock()

    template_config = {
        'mappings': {
            'properties': {
                '@timestamp': {'type': 'date'},
            }
        }
    }

    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[{'@timestamp': '2024-01-01T00:00:00Z'}],
        create_index_template=True,
        index_template=template_config,
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is True
    mock_kibana_client.proxy_put_index_template.assert_called_once_with(
        name='logs-sample-template',
        index_patterns=['logs-sample*'],
        template=template_config,
    )


@pytest.mark.asyncio
async def test_load_sample_data_file_not_found() -> None:
    """Test loading sample data from non-existent file."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)

    sample_data = SampleData(
        source='file',
        index_pattern='logs-*',
        file_path=Path('/nonexistent/sample.ndjson'),
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is False
    assert len(result.errors) == 1
    assert 'Sample data file not found' in result.errors[0]


def test_sample_data_load_result() -> None:
    """Test SampleDataLoadResult properties."""
    result = SampleDataLoadResult(5, [])
    assert result.success is True
    assert result.success_count == 5

    result_with_errors = SampleDataLoadResult(3, ['error1', 'error2'])
    assert result_with_errors.success is False
    assert result_with_errors.success_count == 3
    assert len(result_with_errors.errors) == 2


@pytest.mark.asyncio
async def test_load_sample_data_with_bulk_error_details() -> None:
    """Test loading sample data with detailed bulk operation errors via Kibana proxy."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)
    # Return bulk response with failed items
    mock_bulk_response = BulkResponse(
        took=30,
        errors=True,
        items=[
            {'index': BulkItemResult(index='logs-sample', status=201)},
            {
                'index': BulkItemResult(
                    index='logs-sample',
                    status=400,
                    error=BulkItemError(type='mapper_parsing_exception', reason='failed to parse field [@timestamp]'),
                )
            },
            {
                'index': BulkItemResult(
                    index='logs-sample',
                    status=409,
                    error=BulkItemError(type='version_conflict_engine_exception', reason='version conflict'),
                )
            },
        ],
    )
    mock_kibana_client.proxy_bulk = AsyncMock(return_value=mock_bulk_response)

    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
        ],
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is False
    assert result.success_count == 1
    assert len(result.errors) == 2
    assert any('mapper_parsing_exception' in e for e in result.errors)
    assert any('version_conflict_engine_exception' in e for e in result.errors)


@pytest.mark.asyncio
async def test_load_sample_data_with_error_without_details() -> None:
    """Test loading sample data when error item has no error details."""
    mock_kibana_client = create_autospec(KibanaClient, instance=True)
    # Return bulk response with failed items that have no error details
    mock_bulk_response = BulkResponse(
        took=30,
        errors=True,
        items=[
            {'index': BulkItemResult(index='logs-sample', status=201)},
            {'index': BulkItemResult(index='logs-sample', status=500)},  # No error details
            {'index': BulkItemResult(index='logs-sample', status=503)},  # No error details
        ],
    )
    mock_kibana_client.proxy_bulk = AsyncMock(return_value=mock_bulk_response)

    sample_data = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
        ],
    )

    result = await load_sample_data(mock_kibana_client, sample_data)

    assert result.success is False
    assert len(result.errors) == 2
    assert all('Operation failed with status' in e for e in result.errors)


def test_read_documents_ndjson_with_empty_lines(tmp_path: Path) -> None:
    """Test reading NDJSON file with empty lines."""
    ndjson_file = tmp_path / 'sample.ndjson'
    _ = ndjson_file.write_text(
        '{"@timestamp": "2024-01-01T00:00:00Z", "message": "line1"}\n\n{"@timestamp": "2024-01-01T01:00:00Z", "message": "line2"}\n\n\n'
    )

    sample_data = SampleData(
        source='file',
        index_pattern='logs-*',
        file_path=ndjson_file,
    )

    documents = read_documents(sample_data)

    # Empty lines should be skipped
    assert len(documents) == 2
    assert documents[0]['message'] == 'line1'
    assert documents[1]['message'] == 'line2'
