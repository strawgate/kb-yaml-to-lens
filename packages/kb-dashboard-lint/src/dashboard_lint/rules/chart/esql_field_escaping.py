"""Rule: ES|QL field names with numeric suffixes need backtick escaping."""

from dataclasses import dataclass

from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
from dashboard_lint.esql_helpers import ESQLConfig, UNESCAPED_NUMERIC_FIELD_PATTERN, get_query_string
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation


@chart_rule
@dataclass(frozen=True)
class ESQLFieldEscapingRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: ES|QL field names with numeric suffixes need backtick escaping.

    Field names ending with numbers like apache.load.1 cause parser errors
    and must be escaped with backticks: `apache.load.1`
    """

    id: str = 'esql-field-escaping'
    description: str = 'ES|QL field names with numeric suffixes need backtick escaping'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for unescaped field names with numeric suffixes.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            List of violations for unescaped fields found, empty list if none.

        """
        query_str = get_query_string(config.query)
        violations: list[Violation] = []

        # Find unescaped numeric fields
        for match in UNESCAPED_NUMERIC_FIELD_PATTERN.finditer(query_str):
            field_name = match.group(1)
            violations.append(
                Violation(
                    rule_id=self.id,
                    message=f'Field `{field_name}` has a numeric suffix and must be escaped with backticks',
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('query'),
                )
            )

        return violations
