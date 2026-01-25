"""Tests for lint rules."""

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.rules.dashboard_dataset_filter import DashboardDatasetFilterRule
from dashboard_lint.rules.dimension_missing_label import DimensionMissingLabelRule
from dashboard_lint.rules.esql_where_clause import ESQLWhereClauseRule
from dashboard_lint.rules.markdown_header_height import MarkdownHeaderHeightRule
from dashboard_lint.rules.metric_redundant_label import MetricRedundantLabelRule
from dashboard_lint.types import Severity


class TestMarkdownHeaderHeightRule:
    """Tests for MarkdownHeaderHeightRule."""

    def test_detects_small_markdown_with_header(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should detect markdown panels with headers and insufficient height."""
        rule = MarkdownHeaderHeightRule()
        violations = rule.check(dashboard_with_markdown_header, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'markdown-header-height'
        assert violations[0].severity == Severity.WARNING
        assert 'height >= 3' in violations[0].message

    def test_passes_good_markdown(self, dashboard_with_good_markdown: Dashboard) -> None:
        """Should not flag properly sized markdown panels."""
        rule = MarkdownHeaderHeightRule()
        violations = rule.check(dashboard_with_good_markdown, {})

        assert len(violations) == 0

    def test_custom_min_height_option(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should respect custom min_height option."""
        rule = MarkdownHeaderHeightRule()

        # With min_height=1, should pass (current height is 2)
        violations = rule.check(dashboard_with_markdown_header, {'min_height': 1})
        assert len(violations) == 0

        # With min_height=5, should fail
        violations = rule.check(dashboard_with_markdown_header, {'min_height': 5})
        assert len(violations) == 1


class TestDashboardDatasetFilterRule:
    """Tests for DashboardDatasetFilterRule."""

    def test_detects_missing_dataset_filter(self, dashboard_without_dataset_filter: Dashboard) -> None:
        """Should detect dashboards without dataset filter."""
        rule = DashboardDatasetFilterRule()
        violations = rule.check(dashboard_without_dataset_filter, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'dashboard-dataset-filter'
        assert 'data_stream.dataset' in violations[0].message

    def test_passes_with_dataset_filter(self, dashboard_with_dataset_filter: Dashboard) -> None:
        """Should not flag dashboards with dataset filter."""
        rule = DashboardDatasetFilterRule()
        violations = rule.check(dashboard_with_dataset_filter, {})

        assert len(violations) == 0


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


class TestMetricRedundantLabelRule:
    """Tests for MetricRedundantLabelRule."""

    def test_detects_redundant_label(self, dashboard_with_redundant_label: Dashboard) -> None:
        """Should detect metric panels with redundant labels."""
        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard_with_redundant_label, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'metric-redundant-label'
        assert 'hide_title' in violations[0].message

    def test_passes_with_hidden_title(self, dashboard_with_hidden_title: Dashboard) -> None:
        """Should not flag panels with hide_title=True."""
        rule = MetricRedundantLabelRule()
        violations = rule.check(dashboard_with_hidden_title, {})

        assert len(violations) == 0


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
