"""Configuration schema for Dashboard filters."""

from typing import Annotated, Any, Self

from pydantic import Discriminator, Field, Tag, model_validator

from dashboard_compiler.shared.config import BaseCfgModel


def get_filter_type(v: dict[str, object] | object) -> str:  # noqa: PLR0911, PLR0912
    """Extract filter type for discriminated union validation.

    Args:
        v: Either a dict (during validation) or a filter instance.

    Returns:
        str: The filter type identifier.

    """
    if isinstance(v, dict):
        if 'exists' in v:
            return 'exists'
        if 'equals' in v:
            return 'phrase'
        if 'in' in v:
            return 'phrases'
        if any(k in v for k in ('gte', 'lte', 'gt', 'lt')):
            return 'range'
        if 'dsl' in v:
            return 'custom'
        if 'and' in v:
            return 'and'
        if 'or' in v:
            return 'or'
        if 'not' in v:
            return 'not'
        msg = f'Cannot determine filter type from dict with keys: {list(v)}'  # pyright: ignore[reportUnknownArgumentType]
        raise ValueError(msg)

    if hasattr(v, 'exists'):
        return 'exists'
    if hasattr(v, 'equals'):
        return 'phrase'
    if hasattr(v, 'in_list'):
        return 'phrases'
    if any(hasattr(v, k) for k in ('gte', 'lte', 'gt', 'lt')):
        return 'range'
    if hasattr(v, 'dsl'):
        return 'custom'
    if hasattr(v, 'and_filters'):
        return 'and'
    if hasattr(v, 'or_filters'):
        return 'or'
    if hasattr(v, 'not_filter'):
        return 'not'
    msg = f'Cannot determine filter type from object: {type(v).__name__}'
    raise ValueError(msg)


type FilterPredicateTypes = Annotated[
    Annotated[ExistsFilter, Tag('exists')]
    | Annotated[PhraseFilter, Tag('phrase')]
    | Annotated[PhrasesFilter, Tag('phrases')]
    | Annotated[RangeFilter, Tag('range')]
    | Annotated[CustomFilter, Tag('custom')],
    Discriminator(get_filter_type),
]

type FilterLogicalTypes = Annotated[
    Annotated[AndFilter, Tag('and')] | Annotated[OrFilter, Tag('or')],
    Discriminator(get_filter_type),
]

type FilterModifierTypes = NegateFilter

type FilterTypes = Annotated[
    Annotated[ExistsFilter, Tag('exists')]
    | Annotated[PhraseFilter, Tag('phrase')]
    | Annotated[PhrasesFilter, Tag('phrases')]
    | Annotated[RangeFilter, Tag('range')]
    | Annotated[CustomFilter, Tag('custom')]
    | Annotated[AndFilter, Tag('and')]
    | Annotated[OrFilter, Tag('or')]
    | Annotated[NegateFilter, Tag('not')],
    Discriminator(get_filter_type),
]


class BaseFilter(BaseCfgModel):
    """Base class for filter configurations."""

    alias: str | None = Field(None)
    """Display alias for the filter."""

    disabled: bool | None = Field(None)
    """If true, the filter will not be applied."""


class ExistsFilter(BaseFilter):
    """Filter that checks if a field exists."""

    exists: str = Field(...)
    """The field name to check for existence."""


class CustomFilter(BaseFilter):
    """Filter using raw Elasticsearch Query DSL."""

    dsl: dict[str, Any] = Field(...)
    """The Elasticsearch query DSL object."""


class PhraseFilter(BaseFilter):
    """Filter matching an exact phrase value."""

    field: str = Field(...)
    """The field to filter on."""

    equals: str = Field(...)
    """The exact value to match."""


class PhrasesFilter(BaseFilter):
    """Filter matching any of multiple phrase values."""

    field: str = Field(...)
    """The field to filter on."""

    in_list: list[str] = Field(..., alias='in')
    """Values to match (documents matching any value are included)."""


class RangeFilter(BaseFilter):
    """Filter matching a numeric or date range."""

    field: str = Field(...)
    """The field to filter on."""

    gte: str | None = Field(default=None)
    """Greater than or equal to."""

    lte: str | None = Field(default=None)
    """Less than or equal to."""

    lt: str | None = Field(default=None)
    """Less than."""

    gt: str | None = Field(default=None)
    """Greater than."""

    @model_validator(mode='after')
    def at_least_one_value(self) -> Self:
        """Ensure at least one of gte, lte, gt, or lt is provided."""
        if not any([self.lte, self.gte, self.gt, self.lt]):
            msg = "At least one of 'gte', 'lte', 'gt', or 'lt' must be provided for RangeFilter."
            raise ValueError(msg)
        return self


class NegateFilter(BaseCfgModel):
    """Negates the wrapped filter (excludes matching documents).

    Note: Does not support 'alias' or 'disabled' - apply those to the wrapped filter.
    """

    not_filter: 'FilterTypes' = Field(..., validation_alias='not')
    """The filter to negate."""


class AndFilter(BaseFilter):
    """Filter requiring all nested filters to match."""

    and_filters: list['FilterTypes'] = Field(..., alias='and')
    """All filters must match."""


class OrFilter(BaseFilter):
    """Filter requiring at least one nested filter to match."""

    or_filters: list['FilterTypes'] = Field(..., alias='or')
    """At least one filter must match."""
