"""Rule: ES|QL queries should include a WHERE clause."""

from dataclasses import dataclass

from dashboard_lint.esql_helpers import ESQLConfig, get_query_string, has_command_starting_with
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel


@chart_rule
@dataclass(frozen=True)
class ESQLWhereClauseRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: ES|QL queries should include a WHERE clause.

    Adding a WHERE clause to filter data improves query performance
    and ensures the visualization shows only relevant data.
    This is especially important for large datasets.
    """

    id: str = 'esql-where-clause'
    description: str = 'ES|QL queries should include a WHERE clause'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for missing WHERE clause.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if no WHERE clause found, None otherwise.

        """
        query_str = get_query_string(config.query)

        # Check for WHERE clause
        if not has_command_starting_with(query_str, 'WHERE'):
            return Violation(
                rule_id=self.id,
                message='ES|QL query should include a WHERE clause to filter data',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
