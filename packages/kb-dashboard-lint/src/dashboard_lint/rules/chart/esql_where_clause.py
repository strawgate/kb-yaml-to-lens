"""Rule: ES|QL queries should include a WHERE clause."""

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
from dashboard_compiler.queries.config import ESQLQuery
from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

# Pattern to match WHERE clause (case insensitive)
WHERE_PATTERN = re.compile(r'\bWHERE\b', re.IGNORECASE)

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


def _get_query_string(query: ESQLQuery) -> str:
    """Extract query string from an ESQLQuery, joining list parts with newlines."""
    root = query.root
    if isinstance(root, list):
        return '\n'.join(str(part) for part in root)
    return str(root)


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
        query_str = _get_query_string(config.query)

        # Check for WHERE clause
        if WHERE_PATTERN.search(query_str) is None:
            return Violation(
                rule_id=self.id,
                message='ES|QL query should include a WHERE clause to filter data',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('query'),
            )

        return None
