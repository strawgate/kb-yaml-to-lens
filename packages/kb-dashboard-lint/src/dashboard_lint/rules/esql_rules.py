"""Lint rules for ES|QL queries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard  # noqa: TC001
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation

# Pattern to match WHERE clause (case insensitive, avoiding strings and comments)
# This is a simple heuristic - it looks for WHERE not inside quotes
WHERE_PATTERN = re.compile(r'\bWHERE\b', re.IGNORECASE)


def _get_query_string(query: object) -> str:
    """Extract query string from an ESQLQuery or query-like object.

    Args:
        query: Query object (ESQLQuery with root attr, or str/list directly).

    Returns:
        Single string with the full query.

    """
    # Handle ESQLQuery root model (has 'root' attribute with the actual query)
    if hasattr(query, 'root'):
        return str(query.root)
    if isinstance(query, list):
        return '\n'.join(str(part) for part in query)
    return str(query)


@dataclass(frozen=True)
class ESQLWhereClauseRule:
    """Rule: ES|QL queries should include a WHERE clause.

    Adding a WHERE clause to filter data improves query performance
    and ensures the visualization shows only relevant data.
    This is especially important for large datasets.
    """

    id: str = 'esql-where-clause'
    description: str = 'ES|QL queries should include a WHERE clause'
    default_severity: Severity = Severity.INFO

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:  # noqa: ARG002
        """Check ES|QL panels for missing WHERE clauses.

        Args:
            dashboard: The dashboard to check.
            options: Rule options (currently unused).

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel

        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            if not isinstance(panel, ESQLPanel):
                continue

            # Get the query from the esql config
            config = panel.esql
            if not hasattr(config, 'query'):
                continue

            query = _get_query_string(config.query)

            # Check for WHERE clause
            if WHERE_PATTERN.search(query) is None:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message='ES|QL query should include a WHERE clause to filter data',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].esql.query',
                    )
                )

        return violations


# Register rule with the default registry
register_rule(ESQLWhereClauseRule())
