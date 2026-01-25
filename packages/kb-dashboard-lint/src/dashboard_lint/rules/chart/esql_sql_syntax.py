"""Rule: ES|QL queries should not use SQL syntax."""

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
from dashboard_lint.esql_helpers import (
    find_single_equals,
    find_sql_like_wildcards,
    find_sql_order_by,
    find_sql_select,
    get_query_string,
)
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


@chart_rule
@dataclass(frozen=True)
class ESQLSqlSyntaxRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: ES|QL queries should not use SQL syntax.

    ES|QL is not SQL. Common mistakes include:
    - Using ORDER BY instead of SORT
    - Starting queries with SELECT (ES|QL uses FROM first)
    - Using = for equality instead of ==
    - Using % wildcards in LIKE instead of *
    """

    id: str = 'esql-sql-syntax'
    description: str = 'ES|QL queries should not use SQL syntax'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for SQL syntax usage.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            List of violations for SQL syntax found, empty list if none.

        """
        query_str = get_query_string(config.query)
        violations: list[Violation] = []

        # Check for ORDER BY (should be SORT)
        if len(find_sql_order_by(query_str)) > 0:
            violations.append(
                Violation(
                    rule_id=self.id,
                    message='ES|QL uses SORT, not ORDER BY',
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('query'),
                )
            )

        # Check for SELECT at start (ES|QL uses FROM first)
        if len(find_sql_select(query_str)) > 0:
            violations.append(
                Violation(
                    rule_id=self.id,
                    message='ES|QL queries start with FROM or TS, not SELECT',
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('query'),
                )
            )

        # Check for single = in comparisons (should be ==)
        single_equals = find_single_equals(query_str)
        if len(single_equals) > 0:
            violations.append(
                Violation(
                    rule_id=self.id,
                    message='ES|QL uses == for equality comparison, not =',
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('query'),
                )
            )

        # Check for % wildcards in LIKE (should be *)
        if len(find_sql_like_wildcards(query_str)) > 0:
            violations.append(
                Violation(
                    rule_id=self.id,
                    message='ES|QL LIKE uses * wildcards, not %',
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('query'),
                )
            )

        return violations
