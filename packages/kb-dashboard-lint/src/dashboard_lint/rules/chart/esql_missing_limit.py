"""Rule: ES|QL queries with SORT DESC should have explicit LIMIT."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.esql_helpers import (
    ESQLConfig,
    get_query_string,
    has_command_starting_with,
    has_sort_desc_command,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel


class ESQLMissingLimitOptions(BaseModel):
    """Options for the esql-missing-limit rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    suggested_limit: int = Field(
        default=10,
        ge=1,
        description='Suggested LIMIT value to include in the message',
    )


@chart_rule
@dataclass(frozen=True)
class ESQLMissingLimitRule(ChartRule[ESQLConfig, ESQLMissingLimitOptions]):
    """Rule: ES|QL queries with SORT DESC should have explicit LIMIT.

    Top-N queries (SORT ... DESC) typically want only the top results.
    Without an explicit LIMIT, ES|QL returns up to 1000 rows by default.
    Adding LIMIT makes the intent clear and can improve performance.

    Example fix:
        Before: FROM logs-* | STATS count = COUNT(*) BY host.name | SORT count DESC
        After:  FROM logs-* | STATS count = COUNT(*) BY host.name | SORT count DESC | LIMIT 10

    Options:
        suggested_limit (int): Suggested LIMIT value to include in message. Default: 10.
    """

    id: str = 'esql-missing-limit'
    description: str = 'ES|QL queries with SORT DESC should have explicit LIMIT for top-N results'
    default_severity: Severity = Severity.INFO
    options_model: type[ESQLMissingLimitOptions] = ESQLMissingLimitOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: ESQLMissingLimitOptions,
    ) -> ViolationResult:
        """Check if ES|QL query with SORT DESC has explicit LIMIT.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if SORT DESC without LIMIT is found, None otherwise.

        """
        query_str = get_query_string(config.query)

        # Only check if query has SORT DESC
        if not has_sort_desc_command(query_str):
            return None

        # Check if LIMIT is present
        if has_command_starting_with(query_str, 'LIMIT'):
            return None

        return Violation(
            rule_id=self.id,
            message=f'ES|QL query has SORT DESC but no LIMIT; consider adding LIMIT {options.suggested_limit} for top-N results',
            severity=self.default_severity,
            dashboard_name=context.dashboard_name,
            panel_title=context.panel_title,
            location=context.location('query'),
        )
