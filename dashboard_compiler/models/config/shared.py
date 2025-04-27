from typing import Literal

from pydantic import BaseModel, Field


class Sort(BaseModel):
    """Represents the sort configuration for a control in the YAML schema."""

    by: str = Field(..., description="(Required) Field to sort by.")
    direction: Literal["asc", "desc"] = Field(..., description="(Required) Sort direction ('asc' or 'desc').")


class BaseFilter(BaseModel):
    """Base class for filter configurations in the YAML schema."""

    field: str = Field(..., description="(Required) Field to filter by.")
    # type: Literal["phrase", "phrases"] = Field(..., description="(Required) Filter type.")


class ExistsFilter(BaseFilter):
    """Represents an exists filter configuration for a control in the YAML schema."""

    exists: bool = Field(..., description="(Required) Indicates whether the field must exist or not.")


class PhraseFilter(BaseFilter):
    """Represents a phrase filter configuration for a control in the YAML schema."""

    equals: str = Field(..., description="(Required) Phrase value to filter on.")


class PhrasesFilter(BaseFilter):
    """Represents a phrases filter configuration for a control in the YAML schema."""

    in_list: list[str] = Field(..., alias="in", description="(Required) List of phrases to filter on.")


class RangeFilter(BaseFilter):
    """Represents a range filter configuration for a control in the YAML schema."""

    gte: str | None = Field(None, description="(Optional) Greater than or equal to value for range filters.")
    lte: str | None = Field(None, description="(Optional) Less than or equal to value for range filters.")
    lt: str | None = Field(None, description="(Optional) Less than value for range filters.")
    gt: str | None = Field(None, description="(Optional) Greater than value for range filters.")


class NegationFilter(BaseModel):
    """Represents a negated filter configuration for a control in the YAML schema."""

    not_filter: PhraseFilter | PhrasesFilter | RangeFilter = Field(
        ..., alias="not", description="(Required) Filter to negate. Can be a phrase, phrases, or range filter."
    )


class Filter(BaseModel):
    """Represents a filter configuration for a control in the YAML schema."""

    field: str = Field(..., description="(Required) Field to filter by.")
    type: Literal["phrase", "phrases", "range"]
    value: str = Field(..., description="(Required) Value to filter on.")
    operator: Literal["equals", "contains", "startsWith", "endsWith"] = Field(..., description="(Required) Filter operator.")


class BaseQuery(BaseModel):
    """Represents a query configuration for a control in the YAML schema."""


class KqlQuery(BaseQuery):
    """Represents a KQL query configuration for a control in the YAML schema."""

    kql: str = Field(default="", description="(Required) Query string to filter by.")


class LuceneQuery(BaseQuery):
    """Represents a Lucene query configuration for a control in the YAML schema."""

    lucene: str = Field(default="", description="(Required) Query string to filter by.")
