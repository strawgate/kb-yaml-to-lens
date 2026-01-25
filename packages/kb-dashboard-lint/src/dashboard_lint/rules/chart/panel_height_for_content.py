"""Rule: Panels should have minimum height for their chart type."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    LensPanel,
    LensPanelConfig,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

# Minimum recommended heights for different chart types
MIN_HEIGHTS: dict[str, int] = {
    'metric': 3,
    'gauge': 3,
    'line': 4,
    'bar': 4,
    'area': 4,
    'pie': 4,
    'tagcloud': 4,
    'datatable': 5,
    'heatmap': 5,
    'mosaic': 5,
}

type AnyChartConfig = LensPanelConfig | ESQLPanelConfig


@chart_rule
@dataclass(frozen=True)
class PanelHeightForContentRule(ChartRule[AnyChartConfig]):
    """Rule: Panels should have minimum height for their chart type.

    Different chart types require different minimum heights to display
    effectively. For example, datatables need more vertical space than
    metric displays.

    Options:
        min_heights (dict): Override default heights per chart type.
    """

    id: str = 'panel-height-for-content'
    description: str = 'Panels should have minimum height for their chart type'
    default_severity: Severity = Severity.WARNING

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,
        config: AnyChartConfig,  # noqa: ARG002
        context: ChartContext,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check panel for insufficient height based on chart type.

        Args:
            panel: The chart panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Rule options with optional 'min_heights' dict.

        Returns:
            Violation if height below minimum for chart type, None otherwise.

        """
        height = panel.size.h
        chart_type = context.chart_type

        # Get custom min heights from options or use defaults
        custom_heights = options.get('min_heights', {})
        min_height = custom_heights.get(chart_type, MIN_HEIGHTS.get(chart_type))

        if min_height is not None and height < min_height:
            return Violation(
                rule_id=self.id,
                message=f'{chart_type} chart has height {height} but should be at least {min_height}',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('size'),
            )

        return None
