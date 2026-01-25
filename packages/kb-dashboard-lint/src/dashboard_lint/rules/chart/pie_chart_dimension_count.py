"""Rule: Pie charts with multiple dimensions may be hard to read."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPiePanelConfig,
    LensPanel,
    LensPiePanelConfig,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type PieConfig = LensPiePanelConfig | ESQLPiePanelConfig


class PieChartDimensionCountOptions(BaseModel):
    """Options for the pie-chart-dimension-count rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    max_dimensions: int = Field(
        default=1,
        ge=1,
        description='Maximum dimensions before warning',
    )


@chart_rule
@dataclass(frozen=True)
class PieChartDimensionCountRule(ChartRule[PieConfig, PieChartDimensionCountOptions]):
    """Rule: Pie charts with multiple dimensions may be hard to read.

    Multi-level (sunburst) pie charts with multiple dimensions can be
    difficult to interpret. Consider using separate visualizations or
    a different chart type.

    Options:
        max_dimensions (int): Maximum dimensions before warning. Default: 1.
    """

    id: str = 'pie-chart-dimension-count'
    description: str = 'Pie charts with multiple dimensions may be hard to read'
    default_severity: Severity = Severity.INFO
    options_model: type[PieChartDimensionCountOptions] = PieChartDimensionCountOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: PieConfig,
        context: ChartContext,
        options: PieChartDimensionCountOptions,
    ) -> ViolationResult:
        """Check pie chart for excessive dimensions.

        Args:
            panel: The pie chart panel to check.
            config: The panel's pie chart configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if dimension count exceeds max, None otherwise.

        """
        dimension_count = len(config.dimensions)

        if dimension_count > options.max_dimensions:
            return Violation(
                rule_id=self.id,
                message=f'Pie chart has {dimension_count} dimensions; multi-level pies can be hard to read',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
