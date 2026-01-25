"""Rule: ES|QL queries should include a WHERE clause."""

import re
from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    LensPanel,
    LensPanelConfig,
)
from dashboard_compiler.queries.config import ESQLQuery
from dashboard_lint.rules._base import ChartContext, ChartRule, ViolationResult
from dashboard_lint.rules._decorators import chart_rule
from dashboard_lint.types import Severity, Violation

# Pattern to match WHERE clause (case insensitive)
WHERE_PATTERN = re.compile(r'\bWHERE\b', re.IGNORECASE)


def _get_query_string(query: object) -> str:
    """Extract query string from an ESQLQuery or query-like object.

    Args:
        query: Query object (ESQLQuery with root attr, or str/list directly).

    Returns:
        Single string with the full query.

    """
    # Handle ESQLQuery root model (has 'root' attribute with the actual query)
    if isinstance(query, ESQLQuery):
        return str(query.root)
    if isinstance(query, list):
        return '\n'.join(str(part) for part in query)
    return str(query)


@chart_rule(panel_types=('esql',))  # type: ignore[misc]
@dataclass(frozen=True)
class ESQLWhereClauseRule(ChartRule):
    """Rule: ES|QL queries should include a WHERE clause.

    Adding a WHERE clause to filter data improves query performance
    and ensures the visualization shows only relevant data.
    This is especially important for large datasets.
    """

    id: str = 'esql-where-clause'
    description: str = 'ES|QL queries should include a WHERE clause'
    default_severity: Severity = Severity.INFO

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: LensPanelConfig | ESQLPanelConfig,
        context: ChartContext,
        options: dict[str, Any],  # noqa: ARG002
    ) -> ViolationResult:
        """Check ES|QL panel for missing WHERE clause.

        Args:
            panel: The ESQL panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Rule options (currently unused).

        Returns:
            Violation if no WHERE clause found, None otherwise.

        """
        # ESQLPanelConfig has a query field, but the base class doesn't define it
        # All ESQL panel config types inherit from ESQLPanelConfig and have query
        if not hasattr(config, 'query'):
            return None

        query_str = _get_query_string(config.query)  # type: ignore[union-attr]

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
