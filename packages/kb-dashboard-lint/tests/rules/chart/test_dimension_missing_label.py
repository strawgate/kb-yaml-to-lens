"""Tests for DimensionMissingLabelRule."""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.rules.chart import DimensionMissingLabelRule


class TestDimensionMissingLabelRule:
    """Tests for DimensionMissingLabelRule."""

    def test_detects_missing_dimension_label(self, dashboard_with_dimension_no_label: Dashboard) -> None:
        """Should detect dimensions without labels."""
        rule = DimensionMissingLabelRule()
        violations = rule.check(dashboard_with_dimension_no_label, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'dimension-missing-label'
        assert 'host.name' in violations[0].message

    def test_passes_with_dimension_label(self, dashboard_with_dimension_label: Dashboard) -> None:
        """Should not flag dimensions with labels."""
        rule = DimensionMissingLabelRule()
        violations = rule.check(dashboard_with_dimension_label, {})

        assert len(violations) == 0
