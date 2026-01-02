"""Timestamp transformation utilities for sample data."""

import re
from datetime import UTC, datetime, timedelta
from typing import Any

from dashboard_compiler.sample_data.config import TimestampTransform


def parse_relative_time(expr: str) -> timedelta:
    """Parse relative time expressions into timedelta.

    Args:
        expr: Time expression like '24h', '7d', '1w', '30m'

    Returns:
        Corresponding timedelta object

    Raises:
        ValueError: If expression format is invalid

    """
    match = re.match(r'^(\d+)([mhdw])$', expr)
    if match is None:
        msg = f'Invalid time expression: {expr}. Expected format: <number><unit> (e.g., 24h, 7d, 1w, 30m)'
        raise ValueError(msg)

    value = int(match.group(1))
    unit = match.group(2)

    units = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks',
    }

    return timedelta(**{units[unit]: value})


def parse_timestamp(ts_str: str) -> datetime:
    """Parse timestamp string to datetime.

    Args:
        ts_str: Timestamp string in ISO 8601 format

    Returns:
        Parsed datetime object with timezone

    """
    ts_str_normalized = ts_str.replace('Z', '+00:00')
    return datetime.fromisoformat(ts_str_normalized)


def transform_timestamp(doc: dict[str, Any], transform: TimestampTransform) -> dict[str, Any]:
    """Apply timestamp transformation to a document.

    Args:
        doc: Document dictionary containing timestamp field
        transform: Transformation configuration

    Returns:
        Document with transformed timestamp

    Raises:
        ValueError: If timestamp field is missing or transformation fails

    """
    if transform.field not in doc:
        return doc

    ts_value = doc[transform.field]
    if not isinstance(ts_value, str):
        msg = f'Timestamp field {transform.field} must be a string, got {type(ts_value).__name__}'
        raise TypeError(msg)
    original_ts = parse_timestamp(ts_value)

    if transform.strategy == 'shift':
        if transform.offset is None:
            msg = 'offset is required for shift strategy'
            raise ValueError(msg)
        offset = parse_relative_time(transform.offset)
        new_ts = original_ts + offset
    elif transform.strategy == 'now_minus':
        if transform.range_start is None or transform.range_end is None:
            msg = 'range_start and range_end are required for now_minus strategy'
            raise ValueError(msg)

        start_offset = parse_relative_time(transform.range_start.replace('now-', ''))
        end_offset_str = transform.range_end.replace('now-', '').replace('now', '0m')
        end_offset = parse_relative_time(end_offset_str) if end_offset_str != '0m' else timedelta(0)

        range_start = datetime.now(UTC) - start_offset
        range_end = datetime.now(UTC) - end_offset
        range_duration = range_end - range_start

        time_offset = original_ts - original_ts.replace(hour=0, minute=0, second=0, microsecond=0)
        new_ts = range_start + (time_offset % range_duration)
    elif transform.strategy == 'absolute':
        new_ts = original_ts
    else:
        msg = f'Unknown transformation strategy: {transform.strategy}'
        raise ValueError(msg)

    doc[transform.field] = new_ts.isoformat().replace('+00:00', 'Z')
    return doc


def transform_documents(
    documents: list[dict[str, Any]],
    transform: TimestampTransform | None,
) -> list[dict[str, Any]]:
    """Apply timestamp transformation to a list of documents.

    Args:
        documents: List of document dictionaries
        transform: Transformation configuration (None to skip transformation)

    Returns:
        List of documents with transformed timestamps

    """
    if transform is None:
        return documents

    return [transform_timestamp(doc.copy(), transform) for doc in documents]
