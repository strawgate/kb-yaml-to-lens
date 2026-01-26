"""Rule: ES|QL queries should use dynamic time bucketing."""

from dataclasses import dataclass

from dashboard_lint.esql_helpers import (
    FIXED_BUCKET_PATTERN,
    TBUCKET_FIXED_PATTERN,
    ESQLConfig,
    get_query_string,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel


@chart_rule
@dataclass(frozen=True)
class ESQLDynamicTimeBucketRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: ES|QL queries should use dynamic time bucketing.

    Fixed time buckets like BUCKET(@timestamp, 1 minute) or TBUCKET(5 minutes)
    create too many data points for long time ranges. Use dynamic bucket sizing:
    BUCKET(`@timestamp`, 20, ?_tstart, ?_tend) for FROM queries so visualizations
    scale with the selected time range.
    """

    id: str = 'esql-dynamic-time-bucket'
    description: str = 'ES|QL queries should use dynamic time bucketing'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for fixed time bucket usage.

        Args:
            panel: The ESQL panel to check.
            config: The panel's ESQL configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if fixed time buckets found, None otherwise.

        """
        query_str = get_query_string(config.query)

        # Check for fixed time bucket patterns
        # Note: BUCKET patterns are function calls with specific syntax, so we check
        # the original query. The patterns already handle quoted field names correctly.
        has_fixed_bucket = FIXED_BUCKET_PATTERN.search(query_str) is not None
        has_fixed_tbucket = TBUCKET_FIXED_PATTERN.search(query_str) is not None

        if has_fixed_bucket or has_fixed_tbucket:
            return Violation(
                rule_id=self.id,
                message=(
                    'Use dynamic bucket sizing: BUCKET(`@timestamp`, 20, ?_tstart, ?_tend) '
                    'instead of fixed intervals for better scaling across time ranges'
                ),
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
