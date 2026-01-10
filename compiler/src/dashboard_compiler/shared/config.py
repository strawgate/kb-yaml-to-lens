"""Shared configuration model and utility functions for the dashboard compiler."""

import hashlib
import uuid
from collections.abc import Sequence
from typing import Any, ClassVar, Literal, Protocol, runtime_checkable

from pydantic import Field, model_validator

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


class IDMixin(BaseCfgModel):
    """Mixin that provides automatic stable ID generation for config models.

    Subclasses can define how stable IDs are generated in two ways:

    1. **Simple case (ClassVar list)**: For models where ID components are just field values,
       set `_id_components` to a list of field names. The values will be extracted automatically.

    2. **Complex case (method override)**: For models needing custom logic (sorting, transformation),
       override `_compute_id_components()` to return the components directly.

    Example (simple - ClassVar):
        class MyDimension(IDMixin):
            _id_prefix: ClassVar[str] = 'dimension'
            _id_components: ClassVar[list[str]] = ['type_tag', 'field']  # Just list the field names
            field: str = Field(...)
            type_tag: str = 'terms'

    Example (complex - method override):
        class MyFiltersDimension(IDMixin):
            _id_prefix: ClassVar[str] = 'dimension'
            filters: list[Filter] = Field(...)

            @classmethod
            def _compute_id_components(cls, data: dict[str, Any]) -> Sequence[str | int | float | None] | None:
                # Custom logic to extract and sort filter contents
                filters = data.get('filters', [])
                return ['filters', '|'.join(sorted(f['query'] for f in filters))]
    """

    _id_prefix: ClassVar[str] = ''
    """Override in subclasses to provide a prefix for the stable ID (e.g., 'dimension', 'metric')."""

    _id_type_tag: ClassVar[str] = ''
    """Type discriminator tag included in the ID (e.g., 'static', 'formula', 'terms').

    When set, this value is included before the field values in ID generation.
    Useful for distinguishing between different subtypes that share field names.
    """

    _id_components: ClassVar[list[str]] = []
    """List of field names whose values should be used to generate the ID.

    For simple cases, just list the field names and values will be extracted automatically.
    For complex cases (sorting, transformation), override _compute_id_components() instead.
    """

    id: str | None = Field(default=None)
    """A unique identifier. If not provided, one will be generated from id_components."""

    @model_validator(mode='before')
    @classmethod
    def _generate_stable_id(cls, data: Any) -> Any:  # pyright: ignore[reportAny]
        """Generate a stable ID if one is not provided.

        This validator runs before model instantiation, allowing ID generation
        to work with frozen Pydantic models.
        """
        # Only process dict input (not model instances)
        if not isinstance(data, dict):
            return data  # pyright: ignore[reportAny]

        # If ID is already provided, keep it
        if data.get('id') is not None:  # pyright: ignore[reportUnknownMemberType]
            return data  # pyright: ignore[reportUnknownVariableType]

        # Compute ID components from subclass implementation
        components = cls._compute_id_components(data)  # pyright: ignore[reportUnknownArgumentType]
        if components is not None:
            # Prepend the ID prefix if defined
            prefix = cls._id_prefix
            if prefix:
                all_components: list[str | int | float | None] = [prefix, *components]
            else:
                all_components = list(components)
            # Make a copy to avoid mutating input
            data = dict(data)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
            data['id'] = stable_id_generator(all_components)

        return data  # pyright: ignore[reportUnknownVariableType]

    @classmethod
    def _compute_id_components(cls, data: dict[str, Any]) -> Sequence[str | int | float | None] | None:
        """Compute the components used to generate a stable ID.

        Default implementation extracts values from fields listed in `_id_components`,
        prepending `_id_type_tag` if defined.

        Override this method in subclasses for custom logic (sorting, transformation, etc.).

        Args:
            data: The raw input data dictionary before model validation.

        Returns:
            A sequence of values to hash for the stable ID, or None to skip generation.
        """
        # Use ClassVar list if defined
        if cls._id_components:
            values: list[str | int | float | None] = []
            # Add type tag if defined
            if cls._id_type_tag:
                values.append(cls._id_type_tag)
            # Extract field values
            for field_name in cls._id_components:
                value = data.get(field_name)
                # Treat missing required fields as reason to skip ID generation
                if value is None:
                    return None
                values.append(value)  # pyright: ignore[reportAny]
            return values
        return None


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
        # Sort for order-independent deterministic IDs
        return ','.join(sorted(fields))

    # Try 'filters' for filters dimensions
    # Use isinstance(Sequence) instead of hasattr(__len__) for safer type checking, excluding str/bytes
    filters: Any = getattr(dimension, 'filters', None)
    if filters is not None and isinstance(filters, Sequence) and not isinstance(filters, (str, bytes)):
        # Extract filter content for uniqueness - each filter has a query (kql/lucene) and optional label
        filter_contents: list[str] = []
        for f in filters:
            query = getattr(f, 'query', None)
            # Get the query string from either kql or lucene query type - use explicit None checks
            kql = getattr(query, 'kql', None) if query is not None else None  # pyright: ignore[reportAny]
            lucene = getattr(query, 'lucene', None) if query is not None else None  # pyright: ignore[reportAny]
            query_str = kql if kql is not None else (lucene if lucene is not None else '')
            label_val = getattr(f, 'label', None)
            label = label_val if label_val is not None else ''
            filter_contents.append(f'{query_str}:{label}')
        # Sort filter contents to ensure order-independent deterministic IDs
        return f'filters:{"|".join(sorted(filter_contents))}'

    # Fallback to type name
    return type(dimension).__name__


def get_metric_identifier(metric: object) -> str:
    """Get a representative identifier string from a metric object.

    Handles different metric types:
    - Aggregated metrics with 'aggregation' and 'field' attributes (e.g., avg(bytes), sum(bytes))
    - Count metrics with only 'aggregation' attribute (no field)
    - Formula metrics with 'formula' attribute
    - Static values with 'value' attribute

    Args:
        metric: A metric configuration object.

    Returns:
        A representative string identifier for the metric.
    """
    # Get both field and aggregation to properly distinguish metrics
    field: str | None = getattr(metric, 'field', None)
    aggregation: str | None = getattr(metric, 'aggregation', None)

    # If both aggregation and field exist, combine them for uniqueness
    # This prevents collisions like avg(bytes) vs sum(bytes)
    if aggregation is not None and field is not None:
        return f'{aggregation}:{field}'

    # Aggregation-only metrics (e.g., count without field)
    if aggregation is not None:
        return aggregation

    # Field-only metrics (shouldn't happen in practice, but handle gracefully)
    if field is not None:
        return field

    # Try 'formula' for formula metrics
    formula: str | None = getattr(metric, 'formula', None)
    if formula is not None:
        return f'formula:{formula}'

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
