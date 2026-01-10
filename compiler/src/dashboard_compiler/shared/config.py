"""Shared configuration model and utility functions for the dashboard compiler."""

import hashlib
import json
import uuid
from collections.abc import Sequence
from typing import Any, ClassVar, Literal, Protocol, override, runtime_checkable

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


def _type_tag_value(value: str | int | float | None) -> str:
    """Add type prefix to a value to prevent collisions between different types.

    This ensures that e.g. int 1 and str '1' produce different hashes.
    """
    if value is None:
        return 'n:'
    if isinstance(value, bool):
        # bool must be checked before int since bool is a subclass of int
        return f'b:{value}'
    if isinstance(value, int):
        return f'i:{value}'
    if isinstance(value, float):
        return f'f:{value}'
    # str or fallback
    return f's:{value}'


def stable_id_generator(values: Sequence[str | int | float | None]) -> str:
    """Generate a GUID looking string from a hash of values.

    This produces a stable ID as long as the input values are stable.
    Type tagging ensures different types with the same string representation
    (e.g., int 1 vs str '1') produce different hashes.

    Returns:
        str: A stable GUID-like string generated from the input values.

    """
    # Type-tag each value to prevent collisions between types
    # e.g., [1, 'x'] becomes 'i:1||s:x' while ['1', 'x'] becomes 's:1||s:x'
    # The '||' delimiter ensures different inputs produce different hashes:
    # ['a', 'bc'] ≠ ['ab', 'c'] (with delimiter: 's:a||s:bc' ≠ 's:ab||s:c')
    concatenated_values = '||'.join([_type_tag_value(value) for value in values]).encode('utf-8')

    # Use SHA-1 for deterministic hashing. While SHA-1 is deprecated for cryptographic
    # use, it's perfect here because we need speed and determinism, not security.
    # Collision risk is acceptable for dashboard IDs.
    # SHA-1 always produces 20 bytes, so we truncate to 16 bytes (128 bits) for UUID
    hashed_data = hashlib.sha1(concatenated_values).digest()[:MAX_BYTES_LENGTH]  # noqa: S324

    guid = uuid.UUID(bytes=hashed_data)
    return str(guid)


def _compute_hash_from_dict(data: dict[str, Any], prefix: str = '') -> str:
    """Compute a deterministic hash from a dictionary.

    Uses JSON serialization for deterministic string representation.
    Sorts keys to ensure order independence.

    Args:
        data: Dictionary to hash (typically from model_dump with mode='json').
        prefix: Optional prefix to include in the hash.

    Returns:
        A stable GUID-like string.
    """
    # JSON with sorted keys and compact separators ensures deterministic output
    # The data should already be JSON-safe (from model_dump with mode='json')
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    hash_input = f'{prefix}:{json_str}' if prefix else json_str
    hash_bytes = hashlib.sha1(hash_input.encode()).digest()[:MAX_BYTES_LENGTH]  # noqa: S324
    return str(uuid.UUID(bytes=hash_bytes))


class IDMixin(BaseCfgModel):
    """Mixin that provides automatic stable ID generation for config models.

    IDs are generated deterministically by hashing the model's data (via model_dump).
    The class name is included as a type discriminator, ensuring different model types
    with identical field values get different IDs.

    Subclasses can customize ID generation by overriding `_get_id_data()` to modify
    the data used for hashing (e.g., to sort arrays for order-independent IDs).

    Example (automatic - no configuration needed):
        class LensStaticValue(IDMixin):
            _id_prefix: ClassVar[str] = 'metric'
            value: int | float = Field(...)

    Example (custom logic for order-independent sorting):
        class LensMultiTermsDimension(IDMixin):
            _id_prefix: ClassVar[str] = 'dimension'
            fields: list[str] = Field(...)

            def _get_id_data(self) -> dict[str, Any]:
                data = super()._get_id_data()
                # Sort fields for order-independent IDs
                data['fields'] = sorted(data['fields'])
                return data
    """

    _id_prefix: ClassVar[str] = ''
    """Override in subclasses to provide a prefix for the stable ID (e.g., 'dimension', 'metric')."""

    id: str | None = Field(default=None)
    """A unique identifier. If not provided, one will be generated automatically."""

    @override
    def model_post_init(self, _context: Any) -> None:  # pyright: ignore[reportAny]
        """Generate a stable ID after model construction if not already provided.

        Uses object.__setattr__ to bypass frozen model restrictions.
        """
        if self.id is None:
            # Get the data to hash (subclasses can override _get_id_data)
            data = self._get_id_data()
            # Build prefix from class name and optional _id_prefix
            prefix = f'{type(self).__name__}:{self._id_prefix}' if self._id_prefix else type(self).__name__
            # Generate deterministic ID
            object.__setattr__(self, 'id', _compute_hash_from_dict(data, prefix))

    def _get_id_data(self) -> dict[str, Any]:
        """Get the data dictionary used for ID generation.

        Override this in subclasses to customize ID generation (e.g., sorting arrays).
        By default, uses model_dump with mode='json' excluding the 'id' field.
        Using mode='json' ensures all values are JSON-serializable primitives,
        preventing non-deterministic string conversions of complex objects.

        Returns:
            Dictionary of field values to hash for ID generation.
        """
        return self.model_dump(mode='json', exclude={'id'})


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
