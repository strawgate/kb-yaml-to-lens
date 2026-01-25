"""Rule: Metric primary label should not duplicate panel title."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLMetricPanelConfig,
    ESQLPanel,
    LensMetricPanelConfig,
    LensPanel,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type MetricConfig = LensMetricPanelConfig | ESQLMetricPanelConfig


@chart_rule
@dataclass(frozen=True)
class MetricRedundantLabelRule(ChartRule[MetricConfig]):
    """Rule: Metric primary label should not duplicate panel title.

    When a metric's primary label is the same as the panel title, the title
    is redundant and should be hidden using `hide_title: true`. This avoids
    displaying the same text twice.
    """

    id: str = 'metric-redundant-label'
    description: str = 'Metric primary label matching title should use hide_title: true'
    default_severity: Severity = Severity.WARNING
    config_types: tuple[type, ...] = (LensMetricPanelConfig, ESQLMetricPanelConfig)

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,
        config: MetricConfig,
        context: ChartContext,
        options: dict[str, Any],  # noqa: ARG002
    ) -> ViolationResult:
        """Check metric panel for redundant title/label combinations.

        Args:
            panel: The metric panel to check.
            config: The panel's metric configuration.
            context: Chart context with location helpers.
            options: Rule options (currently unused).

        Returns:
            Violation if label matches title and hide_title not set, None otherwise.

        """
        # Skip panels without titles
        if len(panel.title) == 0:
            return None

        # Skip if hide_title is already set
        if panel.hide_title is True:
            return None

        primary_label = config.primary.label

        # Check if primary label matches title
        if primary_label is not None and primary_label.strip().lower() == panel.title.strip().lower():
            return Violation(
                rule_id=self.id,
                message=f"Primary label '{primary_label}' matches panel title; consider using hide_title: true",
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
