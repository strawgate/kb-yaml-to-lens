"""Shared configuration model and utility functions for the dashboard compiler."""

import hashlib
import uuid
from collections.abc import Sequence
from typing import Any, Literal

from pydantic import Field

from dashboard_compiler.shared.model import BaseModel

MAX_BYTES_LENGTH = 16  # UUIDs are 128 bits (16 bytes)


class BaseCfgModel(BaseModel):
    """Base configuration model for the dashboard compiler."""

    @property
    def minimum_version(self) -> tuple[int, int, int]:
        """Get the minimum Kibana version required for this config and its children.

        This property recursively checks all child models and returns the highest
        version requirement found. Override `_own_minimum_version()` in subclasses
        to declare version requirements for specific features.

        Returns:
            Tuple of (major, minor, patch) representing the minimum Kibana version.

        """
        max_version = self._own_minimum_version()

        # Check all fields for nested BaseCfgModel instances
        field_value: Any
        for field_value in self.__dict__.values():  # pyright: ignore[reportAny]
            if isinstance(field_value, BaseCfgModel):
                child_version = field_value.minimum_version
                max_version = max(max_version, child_version)
            elif isinstance(field_value, list):
                item: Any
                for item in field_value:  # pyright: ignore[reportUnknownVariableType]
                    if isinstance(item, BaseCfgModel):
                        child_version = item.minimum_version
                        max_version = max(max_version, child_version)

        return max_version

    def _own_minimum_version(self) -> tuple[int, int, int]:
        """Return the minimum Kibana version required by this specific config class.

        Override this method in subclasses to declare version requirements.
        The default implementation returns the baseline version (8.8.0).

        Returns:
            Tuple of (major, minor, patch) representing the minimum Kibana version.

        """
        return (8, 8, 0)


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


def get_layer_id(chart_config: object) -> str:
    """Get layer ID from chart config or generate random ID.

    Args:
        chart_config: Chart configuration object with optional 'id' attribute

    Returns:
        Layer ID string (from config.id or randomly generated)

    """
    config_id = getattr(chart_config, 'id', None)
    return config_id if config_id is not None else random_id_generator()


class Sort(BaseCfgModel):
    """Represents a sort configuration in the Config schema."""

    by: str = Field(...)
    """The field name to sort the data by."""

    direction: Literal['asc', 'desc'] = Field(...)
    """The sort direction. Must be either 'asc' for ascending or 'desc' for descending."""
