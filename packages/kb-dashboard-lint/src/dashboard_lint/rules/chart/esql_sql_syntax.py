"""Rule: ES|QL queries should not use SQL syntax."""

from dataclasses import dataclass

from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_lint.esql_helpers import (
    SINGLE_EQUALS_IN_WHERE_PATTERN,
    SQL_LIKE_WILDCARD_PATTERN,
    ESQLConfig,
    first_command_starts_with,
    get_query_string,
    has_order_by,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation


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
        if has_order_by(query_str):
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
        if first_command_starts_with(query_str, 'SELECT'):
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
        if SINGLE_EQUALS_IN_WHERE_PATTERN.search(query_str):
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
        if SQL_LIKE_WILDCARD_PATTERN.search(query_str):
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
