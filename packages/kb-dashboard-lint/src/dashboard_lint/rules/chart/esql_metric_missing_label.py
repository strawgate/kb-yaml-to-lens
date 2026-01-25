"""Rule: ES|QL datatable metrics should have explicit labels."""

from dataclasses import dataclass

from dashboard_compiler.panels.charts.config import (
    ESQLDatatablePanelConfig,
    ESQLPanel,
    LensPanel,
)
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetric
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation


@chart_rule
@dataclass(frozen=True)
class ESQLMetricMissingLabelRule(ChartRule[ESQLDatatablePanelConfig, EmptyOptions]):
    """Rule: ES|QL datatable metrics should have explicit labels.

    Setting explicit labels for metrics improves the readability
    of datatables by providing meaningful column headers instead of
    raw field names.
    """

    id: str = 'esql-metric-missing-label'
    description: str = 'ES|QL datatable metrics should have explicit labels'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLDatatablePanelConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL datatable for metrics without labels.

        Args:
            panel: The chart panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            List of violations for metrics missing labels, or None if all have labels.

        """
        violations: list[Violation] = []

        for idx, metric in enumerate(config.metrics):
            # Only check ESQLMetric types (not ESQLStaticValue which has different semantics)
            if isinstance(metric, ESQLMetric) and (metric.label is None or len(metric.label) == 0):
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f"ES|QL metric '{metric.field}' should have an explicit label for better readability",
                        severity=self.default_severity,
                        dashboard_name=context.dashboard_name,
                        panel_title=context.panel_title,
                        location=context.location(f'metrics[{idx}]'),
                    )
                )

        return violations if violations else None
