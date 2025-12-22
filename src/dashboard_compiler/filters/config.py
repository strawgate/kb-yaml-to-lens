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
        msg = f'Cannot determine filter type from dict with keys: {list(v.keys())}'
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
    """Base class for all filter configurations in the Config schema."""

    alias: str | None = Field(None)
    """An optional alias for the filter, used for display purposes."""

    disabled: bool | None = Field(None)
    """Indicates whether the filter is disabled. If `true`, the filter will not be applied."""


class ExistsFilter(BaseFilter):
    """Represents an 'exists' filter configuration in the Config schema.

    This filter checks for the existence or non-existence of a specific field.
    """

    exists: str = Field(...)
    """The field name to check for existence. If the field exists in a document, it will match that document."""


class CustomFilter(BaseFilter):
    """Represents a custom filter configuration in the Config schema.

    This filter allows for custom query definitions that do not fit into the standard filters.
    """

    dsl: dict[str, Any] = Field(...)
    """The custom query definition. This should be a valid Elasticsearch query object."""


class PhraseFilter(BaseFilter):
    """Represents a 'phrase' filter configuration in the Config schema.

    This filter matches documents where a specific field contains an exact phrase.
    """

    field: str = Field(...)
    """The field name to apply the filter to."""

    equals: str = Field(...)
    """The exact phrase value that the field must match."""


class PhrasesFilter(BaseFilter):
    """Represents a 'phrases' filter configuration in the Config schema.

    This filter matches documents where a specific field contains one or more
    of the specified phrases.
    """

    field: str = Field(...)
    """The field name to apply the filter to."""

    in_list: list[str] = Field(..., alias='in')
    """A list of phrases. Documents must match at least one of these phrases in the specified field."""


class RangeFilter(BaseFilter):
    """Represents a 'range' filter configuration in the Config schema.

    This filter matches documents where a numeric or date field falls within a specified range.
    """

    field: str = Field(...)
    """The field name to apply the filter to."""

    gte: str | None = Field(default=None)
    """Greater than or equal to value for the range filter."""

    lte: str | None = Field(default=None)
    """Less than or equal to value for the range filter."""

    lt: str | None = Field(default=None)
    """Less than value for the range filter."""

    gt: str | None = Field(default=None)
    """Greater than value for the range filter."""

    @model_validator(mode='after')
    def at_least_one_value(self) -> Self:
        """Ensure at least one of gte, lte, gt, or lt is provided."""
        if not any([self.lte, self.gte, self.gt, self.lt]):
            msg = "At least one of 'gte', 'lte', 'gt', or 'lt' must be provided for RangeFilter."
            raise ValueError(msg)
        return self


class NegateFilter(BaseCfgModel):
    """Represents a negated filter configuration in the Config schema.

    This allows for excluding documents that match the nested filter.

    Note: Unlike other filter types, NegateFilter extends BaseCfgModel directly
    rather than BaseFilter, so it does not support 'alias' or 'disabled' fields.
    This is intentional - negation is a logical modifier that wraps another filter,
    and aliasing/disabling should be applied to the wrapped filter itself.
    """

    not_filter: 'FilterTypes' = Field(..., validation_alias='not')
    """The filter to negate. Can be a phrase, phrases, or range filter."""


class AndFilter(BaseFilter):
    """Represents an 'and' filter configuration in the Config schema.

    This filter matches documents that satisfy all of the specified filters.
    """

    and_filters: list['FilterTypes'] = Field(..., alias='and')
    """A list of filters. All filters must match for a document to be included."""


class OrFilter(BaseFilter):
    """Represents an 'or' filter configuration in the Config schema.

    This filter matches documents that satisfy at least one of the specified filters.
    """

    or_filters: list['FilterTypes'] = Field(..., alias='or')
    """A list of filters. At least one filter must match for a document to be included."""
