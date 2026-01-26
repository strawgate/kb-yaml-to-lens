"""Tests for ESQLMissingSortAfterBucketRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import ESQLLinePanelConfig, ESQLMetricPanelConfig, ESQLPanel
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimension, ESQLMetric
from dashboard_compiler.panels.charts.xy.metrics import XYESQLMetric
from dashboard_lint.rules.chart import ESQLMissingSortAfterBucketRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_bucket_no_sort() -> Dashboard:
    """Create a dashboard with BUCKET but no SORT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events Over Time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM logs-* | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1 hour)',
                    dimension=ESQLDimension(field='bucket', data_type='date'),
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_bucket_and_sort() -> Dashboard:
    """Create a dashboard with BUCKET and proper SORT."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Events Over Time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM logs-* | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp, 1 hour) | SORT bucket ASC',
                    dimension=ESQLDimension(field='bucket', data_type='date'),
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_without_bucket() -> Dashboard:
    """Create a dashboard without BUCKET."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Total Count',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


class TestESQLMissingSortAfterBucketRule:
    """Tests for ESQLMissingSortAfterBucketRule."""

    def test_detects_bucket_without_sort(self, dashboard_with_bucket_no_sort: Dashboard) -> None:
        """Should detect BUCKET without SORT."""
        rule = ESQLMissingSortAfterBucketRule()
        violations = rule.check(dashboard_with_bucket_no_sort, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-missing-sort-after-bucket'
        assert 'BUCKET' in violations[0].message
        assert 'SORT' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_passes_bucket_with_sort(self, dashboard_with_bucket_and_sort: Dashboard) -> None:
        """Should not flag BUCKET with proper SORT."""
        rule = ESQLMissingSortAfterBucketRule()
        violations = rule.check(dashboard_with_bucket_and_sort, {})

        assert len(violations) == 0

    def test_passes_without_bucket(self, dashboard_without_bucket: Dashboard) -> None:
        """Should not flag queries without BUCKET."""
        rule = ESQLMissingSortAfterBucketRule()
        violations = rule.check(dashboard_without_bucket, {})

        assert len(violations) == 0
