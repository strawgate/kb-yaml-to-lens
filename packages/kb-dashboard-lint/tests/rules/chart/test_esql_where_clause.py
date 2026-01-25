"""Tests for ESQLWhereClauseRule."""

from dashboard_lint.rules.chart import ESQLWhereClauseRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard


class TestESQLWhereClauseRule:
    """Tests for ESQLWhereClauseRule."""

    def test_detects_missing_where_clause(self, dashboard_with_esql_no_where: Dashboard) -> None:
        """Should detect ES|QL queries without WHERE clause."""
        rule = ESQLWhereClauseRule()
        violations = rule.check(dashboard_with_esql_no_where, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-where-clause'
        assert violations[0].severity == Severity.INFO

    def test_passes_with_where_clause(self, dashboard_with_esql_where: Dashboard) -> None:
        """Should not flag ES|QL queries with WHERE clause."""
        rule = ESQLWhereClauseRule()
        violations = rule.check(dashboard_with_esql_where, {})

        assert len(violations) == 0
