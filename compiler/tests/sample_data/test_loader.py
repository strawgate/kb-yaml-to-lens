"""Tests for sample data loader."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

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
    """Test loading sample data successfully."""
    mock_es_client = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        mock_bulk.return_value = (2, 0)

        sample_data = SampleData(
            source='inline',
            index_pattern='logs-*',
            documents=[
                {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test1'},
                {'@timestamp': '2024-01-01T01:00:00Z', 'message': 'test2'},
            ],
        )

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is True
        assert result.success_count == 2
        assert len(result.errors) == 0

        mock_bulk.assert_called_once()
        call_args = mock_bulk.call_args
        assert call_args[0][0] == mock_es_client
        actions = call_args[0][1]
        assert len(actions) == 2
        assert actions[0]['_index'] == 'logs-sample'
        assert actions[0]['pipeline'] == '_none'


@pytest.mark.asyncio
async def test_load_sample_data_with_errors() -> None:
    """Test loading sample data with errors."""
    mock_es_client = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        mock_bulk.return_value = (1, 1)

        sample_data = SampleData(
            source='inline',
            index_pattern='logs-*',
            documents=[
                {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
            ],
        )

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is False
        assert result.success_count == 1
        assert len(result.errors) == 1


@pytest.mark.asyncio
async def test_load_sample_data_with_timestamp_transform() -> None:
    """Test loading sample data with timestamp transformation."""
    mock_es_client = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        mock_bulk.return_value = (1, 0)

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

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is True
        mock_bulk.assert_called_once()


@pytest.mark.asyncio
async def test_load_sample_data_with_index_template() -> None:
    """Test loading sample data with index template creation."""
    mock_es_client = AsyncMock()
    mock_es_client.indices = AsyncMock()
    mock_es_client.indices.put_index_template = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        mock_bulk.return_value = (1, 0)

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

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is True
        mock_es_client.indices.put_index_template.assert_called_once()


@pytest.mark.asyncio
async def test_load_sample_data_file_not_found() -> None:
    """Test loading sample data from non-existent file."""
    mock_es_client = AsyncMock()

    sample_data = SampleData(
        source='file',
        index_pattern='logs-*',
        file_path=Path('/nonexistent/sample.ndjson'),
    )

    result = await load_sample_data(mock_es_client, sample_data)

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
    """Test loading sample data with detailed bulk operation errors."""
    mock_es_client = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        # Return list of failed items with error details
        failed_items = [
            {'index': {'error': {'type': 'mapper_parsing_exception', 'reason': 'failed to parse field [@timestamp]'}}},
            {'index': {'error': {'type': 'version_conflict_engine_exception', 'reason': 'version conflict'}}},
        ]
        mock_bulk.return_value = (1, failed_items)

        sample_data = SampleData(
            source='inline',
            index_pattern='logs-*',
            documents=[
                {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
            ],
        )

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is False
        assert result.success_count == 1
        assert len(result.errors) == 2
        assert any('mapper_parsing_exception' in e for e in result.errors)
        assert any('version_conflict_engine_exception' in e for e in result.errors)


@pytest.mark.asyncio
async def test_load_sample_data_with_bulk_error_count() -> None:
    """Test loading sample data when bulk returns error count instead of list."""
    mock_es_client = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        # Return error count as integer
        mock_bulk.return_value = (5, 3)

        sample_data = SampleData(
            source='inline',
            index_pattern='logs-*',
            documents=[
                {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
            ],
        )

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is False
        assert result.success_count == 5
        assert len(result.errors) == 1
        assert '3 document(s) failed' in result.errors[0]


@pytest.mark.asyncio
async def test_load_sample_data_with_non_dict_error() -> None:
    """Test loading sample data when error item is not a dict."""
    mock_es_client = AsyncMock()

    with patch('dashboard_compiler.sample_data.loader.async_bulk') as mock_bulk:
        # Return list with non-dict items
        failed_items = ['error1', 'error2']
        mock_bulk.return_value = (1, failed_items)

        sample_data = SampleData(
            source='inline',
            index_pattern='logs-*',
            documents=[
                {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
            ],
        )

        result = await load_sample_data(mock_es_client, sample_data)

        assert result.success is False
        assert len(result.errors) == 2


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
