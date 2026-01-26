"""Pydantic models for Kibana API responses."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

__all__ = ['EsqlColumn', 'EsqlResponse']


class EsqlColumn(BaseModel):
    """Column definition in ES|QL query results."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    name: str
    """Column name."""
    type: str
    """Column data type (e.g., keyword, long, date)."""


class EsqlResponse(BaseModel):
    """Response from ES|QL query execution via Kibana.

    This model represents the structured result of an ES|QL query,
    containing column definitions and row values.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow')

    columns: list[EsqlColumn]
    """Column definitions with name and type."""
    values: list[list[Any]]
    """Row values as nested arrays."""
    took: int | None = None
    """Query execution time in milliseconds."""
    is_partial: bool | None = None
    """Whether results are partial."""

    @property
    def row_count(self) -> int:
        """Return the number of rows in the result."""
        return len(self.values)

    @property
    def column_count(self) -> int:
        """Return the number of columns in the result."""
        return len(self.columns)

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert results to a list of dictionaries with column names as keys.

        Returns:
            List of dictionaries, each representing a row with column names as keys.
        """
        # Values are dynamic JSON types from Elasticsearch
        return [{col.name: val for col, val in zip(self.columns, row, strict=False)} for row in self.values]  # pyright: ignore[reportAny]
