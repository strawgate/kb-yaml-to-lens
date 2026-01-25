"""Rule: Gauge charts with goals should define maximum values."""

from dataclasses import dataclass

from dashboard_compiler.panels.charts.config import (
    ESQLGaugePanelConfig,
    ESQLPanel,
    LensGaugePanelConfig,
    LensPanel,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type GaugeConfig = LensGaugePanelConfig | ESQLGaugePanelConfig


@chart_rule
@dataclass(frozen=True)
class GaugeGoalWithoutMaxRule(ChartRule[GaugeConfig, EmptyOptions]):
    """Rule: Gauge charts with goals should define maximum values.

    When a gauge has a goal threshold, it should also have a maximum
    value defined for the scale to make the goal position meaningful.
    """

    id: str = 'gauge-goal-without-max'
    description: str = 'Gauge charts with goals should define maximum values'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: GaugeConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check gauge panel for goal without max.

        Args:
            panel: The gauge panel to check.
            config: The panel's gauge configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if goal present without max, None otherwise.

        """
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
