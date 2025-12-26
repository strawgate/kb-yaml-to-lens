"""Shared configuration model and utility functions for the dashboard compiler."""

import hashlib
import uuid
from collections.abc import Sequence
from typing import Literal

from pydantic import Field

from dashboard_compiler.shared.model import BaseModel

MAX_BYTES_LENGTH = 16  # UUIDs are 128 bits (16 bytes)


class BaseCfgModel(BaseModel):
    """Base configuration model for the dashboard compiler."""


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
    hashed_data = hashlib.sha1(concatenated_values).digest()  # noqa: S324

    # Truncate or pad to 16 bytes (128 bits) if needed
    if len(hashed_data) > MAX_BYTES_LENGTH:
        hashed_data = hashed_data[:MAX_BYTES_LENGTH]
    elif len(hashed_data) < MAX_BYTES_LENGTH:
        hashed_data = hashed_data.ljust(MAX_BYTES_LENGTH, b'\0')

    guid = uuid.UUID(bytes=hashed_data)
    return str(guid)


class Sort(BaseCfgModel):
    """Represents a sort configuration in the Config schema."""

    by: str = Field(...)
    """The field name to sort the data by."""

    direction: Literal['asc', 'desc'] = Field(...)
    """The sort direction. Must be either 'asc' for ascending or 'desc' for descending."""
