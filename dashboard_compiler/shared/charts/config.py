from pydantic import Field

from dashboard_compiler.shared.model import BaseModel


class LensChartMixin:
    """Mixin for defining Lens chart objects."""

    id: str | None = Field(
        default=None,
        description='A unique identifier for the chart. If not provided, one may be generated during compilation.',
    )


class ESQLChartMixin:
    """Mixin for defining ESQL chart objects."""

    id: str | None = Field(
        default=None,
        description='A unique identifier for the chart. If not provided, one may be generated during compilation.',
    )

    esql: str = Field(
        description='The ESQL query string to be executed. This is the core of the chart definition.',
    )
