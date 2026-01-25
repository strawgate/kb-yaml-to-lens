"""Rule: ES|QL uses BY within STATS, not GROUP BY."""

import re
from dataclasses import dataclass

from dashboard_compiler.panels.charts.config import (
    ESQLAreaPanelConfig,
    ESQLBarPanelConfig,
    ESQLDatatablePanelConfig,
    ESQLGaugePanelConfig,
    ESQLHeatmapPanelConfig,
    ESQLLinePanelConfig,
    ESQLMetricPanelConfig,
    ESQLMosaicPanelConfig,
    ESQLPanel,
    ESQLPiePanelConfig,
    ESQLTagcloudPanelConfig,
    LensPanel,
)
from dashboard_lint.esql_helpers import get_query_string
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type ESQLConfig = (
    ESQLMetricPanelConfig
    | ESQLGaugePanelConfig
    | ESQLHeatmapPanelConfig
    | ESQLPiePanelConfig
    | ESQLLinePanelConfig
    | ESQLBarPanelConfig
    | ESQLAreaPanelConfig
    | ESQLTagcloudPanelConfig
    | ESQLDatatablePanelConfig
    | ESQLMosaicPanelConfig
)

# Pattern to detect GROUP BY (SQL syntax)
GROUP_BY_PATTERN = re.compile(r'\bGROUP\s+BY\b', re.IGNORECASE)


@chart_rule
@dataclass(frozen=True)
class ESQLGroupBySyntaxRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: ES|QL uses BY within STATS, not GROUP BY.

    ES|QL is not SQL. In ES|QL, grouping is done with the BY clause
    within STATS, not a separate GROUP BY clause.

    Example fix:
        Before: FROM logs-* | STATS count = COUNT(*) GROUP BY host.name
        After:  FROM logs-* | STATS count = COUNT(*) BY host.name
    """

    id: str = 'esql-group-by-syntax'
    description: str = 'ES|QL uses BY within STATS, not GROUP BY'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check if ES|QL query uses GROUP BY instead of BY.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if GROUP BY is found, None otherwise.

        """
        query_str = get_query_string(config.query)

        if GROUP_BY_PATTERN.search(query_str):
            return Violation(
                rule_id=self.id,
                message='ES|QL uses BY within STATS, not GROUP BY; use STATS ... BY field instead',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
