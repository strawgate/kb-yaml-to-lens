"""Tests for sample data configuration models."""

from pathlib import Path

from inline_snapshot import snapshot

from dashboard_compiler.sample_data.config import SampleData, TimestampTransform


def test_sample_data_inline() -> None:
    """Test SampleData with inline documents."""
    config = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[
            {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'test'},
        ],
    )

    assert config.source == 'inline'
    assert config.index_pattern == 'logs-*'
    assert config.documents is not None
    assert len(config.documents) == 1


def test_sample_data_file() -> None:
    """Test SampleData with file source."""
    config = SampleData(
        source='file',
        index_pattern='metrics-*',
        file_path=Path('sample.ndjson'),
    )

    assert config.source == 'file'
    assert config.index_pattern == 'metrics-*'
    assert config.file_path == Path('sample.ndjson')
    assert config.format == 'ndjson'


def test_sample_data_with_timestamp_transform() -> None:
    """Test SampleData with timestamp transformation."""
    config = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[{'@timestamp': '2024-01-01T00:00:00Z'}],
        timestamp_transform=TimestampTransform(
            strategy='shift',
            offset='24h',
        ),
    )

    assert config.timestamp_transform is not None
    assert config.timestamp_transform.strategy == 'shift'
    assert config.timestamp_transform.offset == '24h'


def test_timestamp_transform_shift() -> None:
    """Test TimestampTransform with shift strategy."""
    transform = TimestampTransform(
        strategy='shift',
        offset='7d',
    )

    assert transform.strategy == 'shift'
    assert transform.offset == '7d'
    assert transform.field == '@timestamp'


def test_timestamp_transform_now_minus() -> None:
    """Test TimestampTransform with now_minus strategy."""
    transform = TimestampTransform(
        strategy='now_minus',
        range_start='now-24h',
        range_end='now',
    )

    assert transform.strategy == 'now_minus'
    assert transform.range_start == 'now-24h'
    assert transform.range_end == 'now'


def test_sample_data_with_pipeline_bypass() -> None:
    """Test SampleData with pipeline bypass enabled."""
    config = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[],
        bypass_pipeline=True,
    )

    assert config.bypass_pipeline is True


def test_sample_data_with_index_template() -> None:
    """Test SampleData with index template creation."""
    template_config = {
        'mappings': {
            'properties': {
                '@timestamp': {'type': 'date'},
                'message': {'type': 'text'},
            }
        }
    }

    config = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[],
        create_index_template=True,
        index_template=template_config,
    )

    assert config.create_index_template is True
    assert config.index_template is not None
    assert config.index_template == snapshot(template_config)


def test_sample_data_model_dump() -> None:
    """Test SampleData model serialization."""
    config = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[{'@timestamp': '2024-01-01T00:00:00Z'}],
    )

    data = config.model_dump()
    assert data == snapshot(
        {
            'source': 'inline',
            'index_pattern': 'logs-*',
            'documents': [{'@timestamp': '2024-01-01T00:00:00Z'}],
            'file_path': None,
            'format': 'ndjson',
            'timestamp_transform': None,
            'bypass_pipeline': True,
            'create_index_template': False,
            'index_template': None,
        }
    )
