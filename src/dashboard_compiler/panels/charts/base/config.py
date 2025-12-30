from pydantic import Field

from dashboard_compiler.shared.config import BaseCfgModel


class BaseChart(BaseCfgModel):
    """Represents a base chart configuration."""

    id: str | None = Field(default=None)

    # data_view: str = Field(default=...)
