"""Tests for timestamp transformation utilities."""

from datetime import timedelta

import pytest

from dashboard_compiler.sample_data.config import TimestampTransform
from dashboard_compiler.sample_data.timestamps import (
    parse_relative_time,
    parse_timestamp,
    transform_documents,
    transform_timestamp,
)


def test_parse_relative_time_hours() -> None:
    """Test parsing hour expressions."""
    assert parse_relative_time('24h') == timedelta(hours=24)
    assert parse_relative_time('1h') == timedelta(hours=1)


def test_parse_relative_time_days() -> None:
    """Test parsing day expressions."""
    assert parse_relative_time('7d') == timedelta(days=7)
    assert parse_relative_time('1d') == timedelta(days=1)


def test_parse_relative_time_weeks() -> None:
    """Test parsing week expressions."""
    assert parse_relative_time('2w') == timedelta(weeks=2)
    assert parse_relative_time('1w') == timedelta(weeks=1)


def test_parse_relative_time_minutes() -> None:
    """Test parsing minute expressions."""
    assert parse_relative_time('30m') == timedelta(minutes=30)
    assert parse_relative_time('15m') == timedelta(minutes=15)


def test_parse_relative_time_invalid() -> None:
    """Test parsing invalid expressions."""
    with pytest.raises(ValueError, match='Invalid time expression'):
        parse_relative_time('invalid')

    with pytest.raises(ValueError, match='Invalid time expression'):
        parse_relative_time('24')

    with pytest.raises(ValueError, match='Invalid time expression'):
        parse_relative_time('h')


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


def test_transform_timestamp_shift() -> None:
    """Test timestamp transformation with shift strategy."""
    doc = {'@timestamp': '2024-01-01T12:00:00Z', 'message': 'test'}
    transform = TimestampTransform(strategy='shift', offset='24h')

    result = transform_timestamp(doc, transform)

    assert '@timestamp' in result
    assert result['message'] == 'test'
    assert result['@timestamp'] != '2024-01-01T12:00:00Z'


def test_transform_timestamp_absolute() -> None:
    """Test timestamp transformation with absolute strategy."""
    original_ts = '2024-01-01T12:00:00Z'
    doc = {'@timestamp': original_ts, 'message': 'test'}
    transform = TimestampTransform(strategy='absolute')

    result = transform_timestamp(doc, transform)

    assert result['@timestamp'] == original_ts


def test_transform_timestamp_missing_field() -> None:
    """Test transformation when timestamp field is missing."""
    doc = {'message': 'test'}
    transform = TimestampTransform(strategy='shift', offset='24h')

    result = transform_timestamp(doc, transform)

    assert result == doc


def test_transform_timestamp_custom_field() -> None:
    """Test transformation with custom timestamp field."""
    doc = {'event_time': '2024-01-01T12:00:00Z', 'message': 'test'}
    transform = TimestampTransform(field='event_time', strategy='shift', offset='1h')

    result = transform_timestamp(doc, transform)

    assert 'event_time' in result
    assert result['event_time'] != '2024-01-01T12:00:00Z'


def test_transform_documents() -> None:
    """Test transforming multiple documents."""
    documents = [
        {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'doc1'},
        {'@timestamp': '2024-01-01T01:00:00Z', 'message': 'doc2'},
    ]
    transform = TimestampTransform(strategy='absolute')

    result = transform_documents(documents, transform)

    assert len(result) == 2
    assert result[0]['message'] == 'doc1'
    assert result[1]['message'] == 'doc2'


def test_transform_documents_none() -> None:
    """Test transforming documents with no transformation."""
    documents = [
        {'@timestamp': '2024-01-01T00:00:00Z', 'message': 'doc1'},
    ]

    result = transform_documents(documents, None)

    assert result == documents


def test_transform_timestamp_shift_missing_offset() -> None:
    """Test shift strategy without offset raises error."""
    doc = {'@timestamp': '2024-01-01T12:00:00Z'}
    transform = TimestampTransform(strategy='shift')

    with pytest.raises(ValueError, match='offset is required'):
        transform_timestamp(doc, transform)


def test_transform_timestamp_now_minus_missing_range() -> None:
    """Test now_minus strategy without range raises error."""
    doc = {'@timestamp': '2024-01-01T12:00:00Z'}
    transform = TimestampTransform(strategy='now_minus')

    with pytest.raises(ValueError, match='range_start and range_end are required'):
        transform_timestamp(doc, transform)
