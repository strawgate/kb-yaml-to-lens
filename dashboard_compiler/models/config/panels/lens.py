from pydantic import Field
from typing import List, Literal, Union

from dashboard_compiler.models.config.panels.base import BasePanel
from dashboard_compiler.models.config.panels.lens_charts.xy import LensXYChart
from dashboard_compiler.models.config.panels.lens_charts.components.filter import Filter
from dashboard_compiler.models.config.panels.lens_charts.pie import LensPieChart


class LensPanel(BasePanel):
    """Represents a Lens panel defined in the YAML schema."""

    type: Literal["lens"] = "lens"

    chart: Union[LensXYChart, LensPieChart] = Field(..., description="(Required) Nested chart definition.")
    index_pattern: str = Field(..., description="(Required) Index pattern used by the Lens visualization.")
    query: str = Field("", description="(Optional) Panel-specific KQL query. Defaults to ''.")
    filters: List[Filter] = Field(default_factory=list, description="(Optional) Panel-specific filters. Defaults to empty list.")
