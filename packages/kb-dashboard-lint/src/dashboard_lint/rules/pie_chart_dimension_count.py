"""Rule: Pie charts with multiple dimensions may be hard to read."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    ESQLPiePanelConfig,
    LensPanel,
    LensPanelConfig,
    LensPiePanelConfig,
)
from dashboard_lint.rules._base import ChartContext, ChartRule, ViolationResult
from dashboard_lint.rules._decorators import chart_rule
from dashboard_lint.types import Severity, Violation


@chart_rule(chart_types=('pie',))  # type: ignore[misc]
@dataclass(frozen=True)
class PieChartDimensionCountRule(ChartRule):
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

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: LensPanelConfig | ESQLPanelConfig,
        context: ChartContext,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check pie chart for excessive dimensions.

        Args:
            panel: The pie chart panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Rule options with optional 'max_dimensions' key.

        Returns:
            Violation if dimension count exceeds max, None otherwise.

        """
        max_dims = options.get('max_dimensions', 1)
        dimension_count = 0

        if isinstance(config, (LensPiePanelConfig, ESQLPiePanelConfig)):
            dimension_count = len(config.dimensions)

        if dimension_count > max_dims:
            return Violation(
                rule_id=self.id,
                message=f'Pie chart has {dimension_count} dimensions; multi-level pies can be hard to read',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
