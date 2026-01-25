"""Rule: Gauge charts with goals should define maximum values."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLGaugePanelConfig,
    ESQLPanel,
    ESQLPanelConfig,
    LensGaugePanelConfig,
    LensPanel,
    LensPanelConfig,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation


@chart_rule(config_types=(LensGaugePanelConfig, ESQLGaugePanelConfig))
@dataclass(frozen=True)
class GaugeGoalWithoutMaxRule(ChartRule):
    """Rule: Gauge charts with goals should define maximum values.

    When a gauge has a goal threshold, it should also have a maximum
    value defined for the scale to make the goal position meaningful.
    """

    id: str = 'gauge-goal-without-max'
    description: str = 'Gauge charts with goals should define maximum values'
    default_severity: Severity = Severity.WARNING

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: LensPanelConfig | ESQLPanelConfig,
        context: ChartContext,
        options: dict[str, Any],  # noqa: ARG002
    ) -> ViolationResult:
        """Check gauge panel for goal without max.

        Args:
            panel: The gauge panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Rule options (currently unused).

        Returns:
            Violation if goal present without max, None otherwise.

        """
        # Type is guaranteed by config_types filter
        if not isinstance(config, (LensGaugePanelConfig, ESQLGaugePanelConfig)):
            return None

        has_goal = config.goal is not None
        has_max = config.maximum is not None

        if has_goal and not has_max:
            return Violation(
                rule_id=self.id,
                message='Gauge has goal but no maximum; goal position may be misleading',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
