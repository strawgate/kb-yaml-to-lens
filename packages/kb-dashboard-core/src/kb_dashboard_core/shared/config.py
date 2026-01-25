"""Shared configuration model and utility functions for the dashboard compiler."""

import hashlib
import json
import uuid
from typing import Any, Literal, Protocol, override, runtime_checkable

from pydantic import Field

from kb_dashboard_core.shared.model import BaseModel

MAX_BYTES_LENGTH = 16  # UUIDs are 128 bits (16 bytes)


def stable_id_generator(values: list[object]) -> str:
    """Generate a deterministic UUID from a list of values.

    This function is used to generate IDs for objects that don't inherit from BaseIdentifiableModel,
    such as controls, links, panels, and dashboards during compilation.

    Args:
        values: List of values to hash. Values are JSON-serialized for collision safety.

    Returns:
        A deterministic UUID string based on the input values.
    """
    # Use JSON encoding to avoid collision risks from embedded separators
    # e.g., ['a:b', 'c'] vs ['a', 'b:c'] would both be 'a:b:c' with colon joining
    key = json.dumps(values, sort_keys=True, separators=(',', ':'), default=str)
    # SHA-1 hash truncated to UUID size (16 bytes)
    hash_bytes = hashlib.sha1(key.encode()).digest()[:MAX_BYTES_LENGTH]  # noqa: S324
    return str(uuid.UUID(bytes=hash_bytes))


class BaseCfgModel(BaseModel):
    """Base configuration model for the dashboard compiler."""


@runtime_checkable
class HasId(Protocol):
    """Protocol for objects that have an optional 'id' attribute."""

    id: str | None


class BaseIdentifiableModel(BaseCfgModel):
    """Base model that provides automatic stable ID generation for config models.

    IDs are generated deterministically by hashing the model's JSON representation.
    The class name is included as a prefix to ensure different model types with
    identical field values get different IDs.

    The ID generation is simple:
    1. If `id` is explicitly provided, use it
    2. Otherwise, hash the JSON dump of the model (excluding `id` field)

    Example:
        class LensStaticValue(BaseIdentifiableModel):
            value: int | float = Field(...)

        # Both will have the same auto-generated ID:
        a = LensStaticValue(value=42)
        b = LensStaticValue(value=42)
        assert a.id == b.id

        # Explicit ID takes precedence:
        c = LensStaticValue(id='custom', value=42)
        assert c.id == 'custom'
    """

    id: str | None = Field(default=None)
    """A unique identifier. If not provided, one will be generated automatically."""

    @override
    def model_post_init(self, _context: Any) -> None:  # pyright: ignore[reportAny]
        """Generate a stable ID after model construction if not already provided.

        Uses object.__setattr__ to bypass frozen model restrictions.
        """
        if self.id is None:
            # Get JSON-serializable dict of all fields except id
            data = self.model_dump(mode='json', exclude={'id'})
            # Use class name as prefix to differentiate types with same data
            prefix = type(self).__name__
            # JSON with sorted keys ensures deterministic output
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            # SHA-1 hash truncated to UUID size (16 bytes)
            hash_bytes = hashlib.sha1(f'{prefix}:{json_str}'.encode()).digest()[:MAX_BYTES_LENGTH]  # noqa: S324
            object.__setattr__(self, 'id', str(uuid.UUID(bytes=hash_bytes)))

    def get_id(self) -> str:
        """Get the ID, guaranteed to be non-None.

        model_post_init guarantees that id is always set after construction.
        This method provides a type-safe way to access it without None checks.

        Returns:
            The object's id, which is guaranteed to be a string.

        Raises:
            RuntimeError: If id is unexpectedly None (should never happen).
        """
        if self.id is None:
            msg = f'{type(self).__name__}.id is unexpectedly None - BaseIdentifiableModel should have set it'
            raise RuntimeError(msg)
        return self.id


class Sort(BaseCfgModel):
    """Represents a sort configuration in the Config schema."""

    by: str = Field(...)
    """The field name to sort the data by."""

    direction: Literal['asc', 'desc'] = Field(...)
    """The sort direction. Must be either 'asc' for ascending or 'desc' for descending."""
