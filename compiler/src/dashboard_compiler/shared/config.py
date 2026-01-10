"""Shared configuration model and utility functions for the dashboard compiler."""

import hashlib
import uuid
from collections.abc import Sequence
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import Field

from dashboard_compiler.shared.model import BaseModel

MAX_BYTES_LENGTH = 16  # UUIDs are 128 bits (16 bytes)


class BaseCfgModel(BaseModel):
    """Base configuration model for the dashboard compiler."""


@runtime_checkable
class HasId(Protocol):
    """Protocol for objects that have an optional 'id' attribute."""

    id: str | None


def random_id_generator() -> str:
    """Generate a random UUID."""
    return str(uuid.uuid4())


def stable_id_generator(values: Sequence[str | int | float | None]) -> str:
    """Generate a GUID looking string from a hash of values.

    This produces a stable ID as long as the input values are stable.

    Returns:
        str: A stable GUID-like string generated from the input values.

    """
    # The '||' delimiter is used to separate input values before hashing. This ensures
    # different inputs produce different hashes: ['a', 'bc'] ≠ ['ab', 'c']
    # (without delimiter: 'abc' = 'abc', with delimiter: 'a||bc' ≠ 'ab||c')
    concatenated_values = '||'.join([str(value) for value in values]).encode('utf-8')

    # Use SHA-1 for deterministic hashing. While SHA-1 is deprecated for cryptographic
    # use, it's perfect here because we need speed and determinism, not security.
    # Collision risk is acceptable for dashboard IDs.
    # SHA-1 always produces 20 bytes, so we truncate to 16 bytes (128 bits) for UUID
    hashed_data = hashlib.sha1(concatenated_values).digest()[:MAX_BYTES_LENGTH]  # noqa: S324

    guid = uuid.UUID(bytes=hashed_data)
    return str(guid)


def get_dimension_identifier(dimension: object) -> str:
    """Get a representative identifier string from a dimension object.

    Handles different dimension types:
    - LensTermsDimension, LensDateHistogramDimension, etc. with 'field' attribute
    - LensMultiTermsDimension with 'fields' attribute (list)
    - LensFiltersDimension with 'filters' attribute
    - ESQLDimensionTypes with 'field' attribute

    Args:
        dimension: A dimension configuration object.

    Returns:
        A representative string identifier for the dimension.
    """
    # Try 'field' first (most common)
    field: str | None = getattr(dimension, 'field', None)
    if field is not None:
        return field

    # Try 'fields' for multi-terms dimensions
    fields: list[str] | None = getattr(dimension, 'fields', None)
    if fields is not None:
        return ','.join(fields)

    # Try 'filters' for filters dimensions (hasattr check guards against non-list-like attributes)
    filters: list[Any] | None = getattr(dimension, 'filters', None)
    if filters is not None and hasattr(filters, '__len__'):
        return f'filters:{len(filters)}'

    # Fallback to type name
    return type(dimension).__name__


def get_metric_identifier(metric: object) -> str:
    """Get a representative identifier string from a metric object.

    Handles different metric types:
    - Regular metrics with 'field' attribute
    - Count metrics with 'aggregation' attribute
    - Static values with 'value' attribute

    Args:
        metric: A metric configuration object.

    Returns:
        A representative string identifier for the metric.
    """
    # Try 'field' first (most common)
    field: str | None = getattr(metric, 'field', None)
    if field is not None:
        return field

    # Try 'aggregation' for count metrics
    aggregation: str | None = getattr(metric, 'aggregation', None)
    if aggregation is not None:
        return aggregation

    # Try 'value' for static values
    value: float | int | None = getattr(metric, 'value', None)
    if value is not None:
        return f'static:{value}'

    # Fallback to type name
    return type(metric).__name__


def get_layer_id(
    chart_config: object,
    fallback_values: Sequence[str | int | float | None] | None = None,
) -> str:
    """Get layer ID from chart config or generate deterministic/random ID.

    Args:
        chart_config: Chart configuration object with optional 'id' attribute
        fallback_values: Values to use for deterministic ID generation if config.id is None.
                        If None, falls back to random generation (backward compatible).

    Returns:
        Layer ID string (from config.id, deterministic from fallback_values, or random)

    """
    config_id: str | None = getattr(chart_config, 'id', None)
    if config_id is not None:
        return config_id
    if fallback_values is not None:
        return stable_id_generator(fallback_values)
    return random_id_generator()


class Sort(BaseCfgModel):
    """Represents a sort configuration in the Config schema."""

    by: str = Field(...)
    """The field name to sort the data by."""

    direction: Literal['asc', 'desc'] = Field(...)
    """The sort direction. Must be either 'asc' for ascending or 'desc' for descending."""
