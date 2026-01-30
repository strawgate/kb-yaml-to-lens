"""Rule: Metric panels with multiple metrics need adequate width."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import (
    ESQLMetricPanelConfig,
    ESQLPanel,
    LensMetricPanelConfig,
    LensPanel,
)

type MetricConfig = LensMetricPanelConfig | ESQLMetricPanelConfig


class MetricMultipleMetricsWidthOptions(BaseModel):
    """Options for the metric-multiple-metrics-width rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    min_width_multiple: int = Field(
        default=12,
        ge=1,
        description='Minimum width for multi-metric panels',
    )


@chart_rule
@dataclass(frozen=True)
class MetricMultipleMetricsWidthRule(ChartRule[MetricConfig, MetricMultipleMetricsWidthOptions]):
    """Rule: Metric panels with multiple metrics need adequate width.

    When a metric panel displays secondary or maximum values in addition
    to the primary metric, it needs more horizontal space to avoid
    crowding the display.

    Options:
        min_width_multiple (int): Minimum width for multi-metric panels. Default: 12.
    """

    id: str = 'metric-multiple-metrics-width'
    description: str = 'Metric panels with multiple metrics should have adequate width'
    default_severity: Severity = Severity.WARNING
    options_model: type[MetricMultipleMetricsWidthOptions] = MetricMultipleMetricsWidthOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,
        config: MetricConfig,
        context: ChartContext,
        options: MetricMultipleMetricsWidthOptions,
    ) -> ViolationResult:
        """Check metric panel for width vs content complexity.

        Args:
            panel: The metric panel to check.
            config: The panel's metric configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if multi-metric and width too small, None otherwise.

        """
        # Use .width property which resolves semantic widths to integers
        width = panel.size.width

        # Count metrics
        metric_count = 1  # Always have primary
        if config.secondary is not None:
            metric_count += 1
        if config.maximum is not None:
            metric_count += 1

        if metric_count > 1 and width < options.min_width_multiple:
            return Violation(
                rule_id=self.id,
                message=f'Panel has {metric_count} metrics but width {width} is below recommended {options.min_width_multiple}',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
