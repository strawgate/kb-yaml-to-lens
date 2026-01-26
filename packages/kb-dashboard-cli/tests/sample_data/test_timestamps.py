"""Tests for timestamp transformation utilities."""

from datetime import UTC, datetime
from typing import Any

from kb_dashboard_core.sample_data.config import TimestampTransform
from kb_dashboard_core.sample_data.timestamps import (
    find_max_timestamp,
    parse_timestamp,
    transform_documents,
)


def test_parse_timestamp() -> None:
    """Test parsing ISO 8601 timestamps."""
    ts = parse_timestamp('2024-01-01T00:00:00Z')
    assert ts.year == 2024
    assert ts.month == 1
    assert ts.day == 1
    assert ts.hour == 0
    assert ts.minute == 0
    assert ts.second == 0


def test_parse_timestamp_with_offset() -> None:
    """Test parsing timestamps with timezone offsets."""
    ts = parse_timestamp('2024-01-01T00:00:00+00:00')
    assert ts.year == 2024
    assert ts.month == 1
    assert ts.day == 1


def test_find_max_timestamp() -> None:
    """Test finding maximum timestamp in documents."""
    documents = [
        {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'first'},
        {'@timestamp': '2024-01-01T03:00:00Z', 'message': 'third'},
        {'@timestamp': '2024-01-01T01:00:00Z', 'message': 'second'},
    ]

    max_ts = find_max_timestamp(documents, '@timestamp')

    assert max_ts is not None
    assert max_ts == parse_timestamp('2024-01-01T03:00:00Z')


def test_find_max_timestamp_custom_field() -> None:
    """Test finding maximum timestamp with custom field name."""
    documents = [
        {'event_time': '2024-01-01T00:00:00Z'},
        {'event_time': '2024-01-01T02:00:00Z'},
    ]

    max_ts = find_max_timestamp(documents, 'event_time')

    assert max_ts is not None
    assert max_ts == parse_timestamp('2024-01-01T02:00:00Z')


def test_find_max_timestamp_missing_field() -> None:
    """Test finding max timestamp when field is missing from some documents."""
    documents = [
        {'@timestamp': '2024-01-01T01:00:00Z'},
        {'message': 'no timestamp'},
        {'@timestamp': '2024-01-01T03:00:00Z'},
    ]

    max_ts = find_max_timestamp(documents, '@timestamp')

    assert max_ts is not None
    assert max_ts == parse_timestamp('2024-01-01T03:00:00Z')


def test_find_max_timestamp_no_valid_timestamps() -> None:
    """Test finding max timestamp when no valid timestamps exist."""
    documents = [
        {'message': 'no timestamp'},
        {'@timestamp': 12345},
    ]

    max_ts = find_max_timestamp(documents, '@timestamp')

    assert max_ts is None


def test_transform_documents_enabled() -> None:
    """Test timestamp transformation when enabled."""
    documents = [
        {'@timestamp': '2024-01-01T09:01:00Z', 'message': 'first'},
        {'@timestamp': '2024-01-01T09:02:00Z', 'message': 'second'},
        {'@timestamp': '2024-01-01T09:03:00Z', 'message': 'third'},
    ]
    transform = TimestampTransform(enabled=True)

    result = transform_documents(documents, transform)

    assert len(result) == 3

    result_timestamps = [parse_timestamp(doc['@timestamp']) for doc in result]

    time_diffs = [
        (result_timestamps[1] - result_timestamps[0]).total_seconds(),
        (result_timestamps[2] - result_timestamps[1]).total_seconds(),
    ]
    assert time_diffs[0] == 60
    assert time_diffs[1] == 60

    now = datetime.now(UTC)
    max_result_ts = max(result_timestamps)
    time_diff_from_now = abs((max_result_ts - now).total_seconds())
    assert time_diff_from_now < 2


def test_transform_documents_disabled() -> None:
    """Test transformation disabled (no changes)."""
    original_ts = '2024-01-01T12:00:00Z'
    documents = [
        {'@timestamp': original_ts, 'message': 'test'},
    ]
    transform = TimestampTransform(enabled=False)

    result = transform_documents(documents, transform)

    assert result[0]['@timestamp'] == original_ts


def test_transform_documents_none() -> None:
    """Test transforming documents with no transformation."""
    documents = [
        {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'doc1'},
    ]

    result = transform_documents(documents, None)

    assert result == documents


def test_transform_documents_missing_timestamps() -> None:
    """Test transformation when some documents lack timestamps."""
    documents = [
        {'@timestamp': '2024-01-01T01:00:00Z', 'message': 'has_ts'},
        {'message': 'no_ts'},
        {'@timestamp': '2024-01-01T03:00:00Z', 'message': 'has_ts'},
    ]
    transform = TimestampTransform(enabled=True)

    result = transform_documents(documents, transform)

    assert len(result) == 3
    assert '@timestamp' in result[0]
    assert '@timestamp' not in result[1]
    assert '@timestamp' in result[2]


def test_transform_documents_custom_field() -> None:
    """Test transformation with custom timestamp field."""
    documents = [
        {'event_time': '2024-01-01T10:00:00Z', 'message': 'doc1'},
        {'event_time': '2024-01-01T11:00:00Z', 'message': 'doc2'},
    ]
    transform = TimestampTransform(field='event_time', enabled=True)

    result = transform_documents(documents, transform)

    assert len(result) == 2
    assert 'event_time' in result[0]
    assert 'event_time' in result[1]
    assert result[0]['event_time'] != '2024-01-01T10:00:00Z'


def test_transform_documents_preserves_original() -> None:
    """Test that transformation doesn't modify original documents."""
    original_doc = {'@timestamp': '2024-01-01T12:00:00Z', 'message': 'test'}
    documents = [original_doc]
    transform = TimestampTransform(enabled=True)

    _ = transform_documents(documents, transform)

    assert original_doc['@timestamp'] == '2024-01-01T12:00:00Z'


def test_find_max_timestamp_with_invalid_timestamps() -> None:
    """Test finding max timestamp when timestamps fail to parse."""
    documents = [
        {'@timestamp': 'invalid-timestamp', 'message': 'bad'},
        {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'good'},
        {'@timestamp': '2024-01-01T02:00:00Z', 'message': 'good2'},
    ]

    max_ts = find_max_timestamp(documents, '@timestamp')

    assert max_ts is not None
    assert max_ts == parse_timestamp('2024-01-01T02:00:00Z')


def test_find_max_timestamp_empty_list() -> None:
    """Test finding max timestamp in empty document list."""
    documents: list[dict[str, Any]] = []

    max_ts = find_max_timestamp(documents, '@timestamp')

    assert max_ts is None


def test_transform_documents_with_invalid_timestamps() -> None:
    """Test transformation silently skips documents with invalid timestamps."""
    documents = [
        {'@timestamp': 'not-a-timestamp', 'message': 'invalid'},
        {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'valid'},
    ]
    transform = TimestampTransform(enabled=True)

    result = transform_documents(documents, transform)

    assert len(result) == 2
    invalid = next(doc for doc in result if doc.get('message') == 'invalid')
    valid = next(doc for doc in result if doc.get('message') == 'valid')
    assert invalid['@timestamp'] == 'not-a-timestamp'
    assert valid['@timestamp'] != '2024-01-01T00:00:00Z'


def test_transform_documents_all_invalid_timestamps() -> None:
    """Test transformation when all timestamps are invalid (no max found)."""
    documents = [
        {'@timestamp': 'invalid1', 'message': 'bad1'},
        {'@timestamp': 'invalid2', 'message': 'bad2'},
    ]
    transform = TimestampTransform(enabled=True)

    result = transform_documents(documents, transform)

    # Should return documents unchanged since no valid max timestamp
    assert result == documents
