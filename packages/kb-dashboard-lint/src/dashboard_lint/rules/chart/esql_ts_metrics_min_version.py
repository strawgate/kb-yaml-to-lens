"""Rule: FROM metrics-* should use TS metrics-* on Kibana/Elasticsearch 9.2+."""

import re
from dataclasses import dataclass

from dashboard_lint.esql_helpers import ESQLConfig, get_query_string, split_into_commands
from dashboard_lint.kibana_version import version_lt
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import ESQLPanel, LensPanel

SOURCE_PATTERN = re.compile(r'^\s*FROM\s+(?P<source>\S+)', re.IGNORECASE)
TS_METRICS_MINIMUM_VERSION = '9.2.0'


@chart_rule
@dataclass(frozen=True)
class ESQLTSMetricsMinVersionRule(ChartRule[ESQLConfig, EmptyOptions]):
    """Rule: FROM metrics-* should use TS metrics-* on Kibana/Elasticsearch 9.2+."""

    id: str = 'esql-ts-metrics-min-version'
    description: str = 'FROM metrics-* should use TS metrics-* on Kibana/Elasticsearch 9.2+'
    default_severity: Severity = Severity.WARNING
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: ESQLConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for FROM metrics-* usage that should migrate to TS."""
        query_str = get_query_string(config.query)
        commands = split_into_commands(query_str)
        if len(commands) == 0:
            return None

        match = SOURCE_PATTERN.match(commands[0])
        if match is None:
            return None

        source = match.group('source').strip('`\'"').lower()
        if source.startswith('metrics-'):
            minimum_kibana_version = context.dashboard_minimum_kibana_version
            if minimum_kibana_version is None:
                return None

            is_below_minimum = version_lt(minimum_kibana_version, TS_METRICS_MINIMUM_VERSION)
            if is_below_minimum is None or is_below_minimum:
                return None

            return Violation(
                rule_id=self.id,
                message=(
                    'FROM metrics-* should use TS metrics-* on Kibana/Elasticsearch 9.2+. '
                    f"Dashboard declares minimum_kibana_version='{minimum_kibana_version}'. "
                    'Keep FROM only when the stream is not TSDB.'
                ),
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
