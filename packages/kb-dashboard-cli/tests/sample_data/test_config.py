"""Tests for sample data configuration models."""

from pathlib import Path

from inline_snapshot import snapshot
from kb_dashboard_core.sample_data.config import SampleData, TimestampTransform


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
    # timestamp_transform is enabled by default
    assert config.timestamp_transform is not None
    assert config.timestamp_transform.enabled is True


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


def test_sample_data_with_timestamp_transform() -> None:
    """Test SampleData with timestamp transformation."""
    config = SampleData(
        source='inline',
        index_pattern='logs-*',
        documents=[{'@timestamp': '2024-01-01T00:00:00Z'}],
        timestamp_transform=TimestampTransform(
            enabled=True,
        ),
    )

    assert config.timestamp_transform is not None
    assert config.timestamp_transform.enabled is True


def test_timestamp_transform_enabled() -> None:
    """Test TimestampTransform with transformation enabled."""
    transform = TimestampTransform(
        enabled=True,
    )

    assert transform.enabled is True
    assert transform.field == '@timestamp'


def test_timestamp_transform_disabled() -> None:
    """Test TimestampTransform with transformation disabled."""
    transform = TimestampTransform(
        enabled=False,
    )

    assert transform.enabled is False
    assert transform.field == '@timestamp'


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
            'timestamp_transform': {'field': '@timestamp', 'enabled': True},
            'create_index_template': False,
            'index_template': None,
        }
    )
