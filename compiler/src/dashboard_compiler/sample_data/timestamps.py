"""Timestamp transformation utilities for sample data."""

from datetime import UTC, datetime
from typing import Any

from dashboard_compiler.sample_data.config import TimestampTransform


def parse_timestamp(ts_str: str) -> datetime:
    """Parse timestamp string to datetime.

    Args:
        ts_str: Timestamp string in ISO 8601 format

    Returns:
        Parsed datetime object with timezone

    """
    ts_str_normalized = ts_str.replace('Z', '+00:00')
    return datetime.fromisoformat(ts_str_normalized)


def find_max_timestamp(documents: list[dict[str, Any]], field: str) -> datetime | None:
    """Find the maximum timestamp in a list of documents.

    Args:
        documents: List of document dictionaries
        field: Name of the timestamp field

    Returns:
        Maximum timestamp found, or None if no valid timestamps exist

    """
    max_ts: datetime | None = None

    for doc in documents:
        if field not in doc:
            continue

        ts_value = doc[field]  # pyright: ignore[reportAny]
        if not isinstance(ts_value, str):
            continue

        try:
            ts = parse_timestamp(ts_value)
            if max_ts is None or ts > max_ts:
                max_ts = ts
        except (ValueError, TypeError):
            continue

    return max_ts


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
    if transform is None or transform.enabled is False:
        return documents

    max_ts = find_max_timestamp(documents, transform.field)
    if max_ts is None:
        return documents

    now = datetime.now(UTC)
    shift_offset = now - max_ts

    transformed = []
    for doc in documents:
        doc_copy = doc.copy()
        if transform.field in doc_copy:
            ts_value = doc_copy[transform.field]  # pyright: ignore[reportAny]
            if isinstance(ts_value, str):
                try:
                    original_ts = parse_timestamp(ts_value)
                    new_ts = original_ts + shift_offset
                    doc_copy[transform.field] = new_ts.isoformat().replace('+00:00', 'Z')
                except (ValueError, TypeError):
                    pass
        transformed.append(doc_copy)  # pyright: ignore[reportUnknownMemberType]
    return transformed  # pyright: ignore[reportUnknownVariableType]
