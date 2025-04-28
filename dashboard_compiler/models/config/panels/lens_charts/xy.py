from typing import Literal

from pydantic import BaseModel, Field, model_validator

from dashboard_compiler.models.config.panels.lens_charts.base import (
    BaseLensAxisFormat,
    BaseLensChart,
    LensAppearanceFormat,
    LensLegendFormat,
)
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric  # Import Metric


class LensBottomAxisFormat(BaseLensAxisFormat):
    """Model for bottom axis formatting options."""

    show_current_time_marker: bool | None = Field(None, description="Show current time marker on the bottom axis.")


class LensLeftAxisFormat(BaseLensAxisFormat):
    """Model for left axis formatting options."""

    pass  # Add left-specific fields if needed


class LensRightAxisFormat(BaseLensAxisFormat):
    """Model for right axis formatting options."""

    metrics: list[Metric] = Field(default_factory=list, description="List of metrics to display on the right axis.")  # Added metrics


class LensAxisFormat(BaseModel):
    """Model for grouping axis formatting options."""

    bottom: LensBottomAxisFormat = Field(default_factory=LensBottomAxisFormat, description="Bottom axis formatting.")
    left: LensLeftAxisFormat = Field(default_factory=LensLeftAxisFormat, description="Left axis formatting.")
    right: LensRightAxisFormat | None = Field(None, description="Right axis formatting (optional).")


class LensXYChart(BaseLensChart):
    """Represents a Bar/Line/Area chart definition within a Lens panel in the YAML schema."""

    type: Literal["bar", "area", "line"] = "bar"
    mode: Literal["stacked", "unstacked", "percentage"] = Field("unstacked", description="Stacking mode for bar and area charts.")
    dimensions: list[Dimension] = Field(
        ..., description="(Required) Defines the axes (usually x-axis or split/breakdown dimensions).", min_length=1
    )
    metrics: list[Metric] = Field(..., description="(Required) Defines the values (usually y-axis).", min_length=1)

    axis: LensAxisFormat = Field(default_factory=LensAxisFormat, description="Axis formatting options.")
    legend: LensLegendFormat = Field(default_factory=LensLegendFormat, description="Legend formatting options.")
    appearance: LensAppearanceFormat = Field(default_factory=LensAppearanceFormat, description="Chart appearance options.")

    @model_validator(mode="after")
    def check_mode_for_chart_type(self) -> "LensXYChart":
        # if self.mode is not None and self.type not in ["bar", "area"]:
        #    raise ValueError("Mode can only be specified for 'bar' or 'area' chart types.")
        return self

    def add_dimension(self, dimension: Dimension) -> None:
        """
        Add a dimension to the chart.

        Args:
            dimension (Dimension): The dimension to add.
        """
        self.dimensions.append(dimension)

    def add_metric(self, metric: Metric) -> None:
        """
        Add a metric to the chart.

        Args:
            metric (Metric): The metric to add.
        """
        self.metrics.append(metric)
