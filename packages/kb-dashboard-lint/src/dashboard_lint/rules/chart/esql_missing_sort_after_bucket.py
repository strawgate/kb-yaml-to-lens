"""Rule: ES|QL time series queries with BUCKET should end with SORT."""

from dataclasses import dataclass

from dashboard_lint.esql_helpers import (
    BUCKET_PATTERN,
    ESQLConfig,
    get_query_string,
    has_command_containing,
    last_command_starts_with,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel


@chart_rule
@dataclass(frozen=True)
class ESQLMissingSortAfterBucketRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: ES|QL time series queries with BUCKET should end with SORT.

    When using BUCKET for time series aggregations, the query should end with
    SORT to ensure chronological ordering. Without explicit sorting, time
    series visualizations may display data in unexpected order.

    Example fix:
        Before: FROM logs-* | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1 hour)
        After:  FROM logs-* | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1 hour) | SORT bucket ASC
    """

    id: str = 'esql-missing-sort-after-bucket'
    description: str = 'ES|QL time series queries with BUCKET should end with SORT for proper ordering'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check if ES|QL query with BUCKET has proper SORT ordering.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if BUCKET is used without SORT, None otherwise.

        """
        query_str = get_query_string(config.query)

        # Only check if query uses BUCKET
        if not has_command_containing(query_str, BUCKET_PATTERN):
            return None

        # Check if the last command is SORT
        if last_command_starts_with(query_str, 'SORT'):
            return None

        return Violation(
            rule_id=self.id,
            message='ES|QL query uses BUCKET but lacks SORT; add SORT <bucket_field> ASC for chronological order',
            severity=self.default_severity,
            dashboard_name=context.dashboard_name,
            panel_title=context.panel_title,
            location=context.location('query'),
        )
