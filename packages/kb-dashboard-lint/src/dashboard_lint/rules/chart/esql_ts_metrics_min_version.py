"""Rule: TS metrics-* queries require Kibana/Elasticsearch 9.2+."""

import re
from dataclasses import dataclass

from dashboard_lint.esql_helpers import ESQLConfig, get_query_string, split_into_commands
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel

TS_SOURCE_PATTERN = re.compile(r'^\s*TS\s+(?P<source>\S+)', re.IGNORECASE)


@chart_rule
@dataclass(frozen=True)
class ESQLTSMetricsMinVersionRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: TS metrics-* queries require Kibana/Elasticsearch 9.2+.

    TS with metrics-* is only supported in newer stack versions. Warn so
    dashboards intended for older versions can use FROM-based alternatives.
    """

    id: str = 'esql-ts-metrics-min-version'
    description: str = 'TS metrics-* queries require Kibana/Elasticsearch 9.2+'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for TS metrics-* usage that requires 9.2+."""
        query_str = get_query_string(config.query)
        commands = split_into_commands(query_str)
        if len(commands) == 0:
            return None

        match = TS_SOURCE_PATTERN.match(commands[0])
        if match is None:
            return None

        source = match.group('source').strip('`\'"').lower()
        if source.startswith('metrics-'):
            return Violation(
                rule_id=self.id,
                message=('TS queries on metrics-* require Kibana/Elasticsearch 9.2+; use FROM for older stack versions'),
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
