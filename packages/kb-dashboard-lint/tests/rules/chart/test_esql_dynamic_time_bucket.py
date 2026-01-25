"""Tests for ESQLDynamicTimeBucketRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.charts.config import ESQLLinePanelConfig, ESQLMetricPanelConfig, ESQLPanel
from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetric
from dashboard_compiler.panels.charts.xy.metrics import XYESQLMetric
from dashboard_lint.rules.chart import ESQLDynamicTimeBucketRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_fixed_bucket() -> Dashboard:
    """Create a dashboard with fixed BUCKET interval."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Requests over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(@timestamp, 1 minute)',
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_fixed_bucket_hours() -> Dashboard:
    """Create a dashboard with fixed hour BUCKET interval."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Requests over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(`@timestamp`, 1 hour)',
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_tbucket_fixed() -> Dashboard:
    """Create a dashboard with fixed TBUCKET interval."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Rate over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='TS metrics-* | STATS rate = SUM(RATE(requests)) BY TBUCKET(5 minutes)',
                    metrics=[XYESQLMetric(field='rate')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_dynamic_bucket() -> Dashboard:
    """Create a dashboard with dynamic bucket sizing."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Requests over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(`@timestamp`, 20, ?_tstart, ?_tend)',
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_without_bucket() -> Dashboard:
    """Create a dashboard without any time bucket."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Total count',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | WHERE status == 200 | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            ),
        ],
    )


class TestESQLDynamicTimeBucketRule:
    """Tests for ESQLDynamicTimeBucketRule."""

    def test_detects_fixed_bucket_minutes(self, dashboard_with_fixed_bucket: Dashboard) -> None:
        """Should detect fixed minute bucket."""
        rule = ESQLDynamicTimeBucketRule()
        violations = rule.check(dashboard_with_fixed_bucket, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-dynamic-time-bucket'
        assert 'dynamic' in violations[0].message.lower()
        assert violations[0].severity == Severity.INFO

    def test_detects_fixed_bucket_hours(self, dashboard_with_fixed_bucket_hours: Dashboard) -> None:
        """Should detect fixed hour bucket."""
        rule = ESQLDynamicTimeBucketRule()
        violations = rule.check(dashboard_with_fixed_bucket_hours, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-dynamic-time-bucket'
        assert violations[0].severity == Severity.INFO

    def test_detects_tbucket_fixed(self, dashboard_with_tbucket_fixed: Dashboard) -> None:
        """Should detect fixed TBUCKET interval."""
        rule = ESQLDynamicTimeBucketRule()
        violations = rule.check(dashboard_with_tbucket_fixed, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-dynamic-time-bucket'
        assert violations[0].severity == Severity.INFO

    def test_passes_dynamic_bucket(self, dashboard_with_dynamic_bucket: Dashboard) -> None:
        """Should not flag dynamic bucket sizing."""
        rule = ESQLDynamicTimeBucketRule()
        violations = rule.check(dashboard_with_dynamic_bucket, {})

        assert len(violations) == 0

    def test_passes_no_bucket(self, dashboard_without_bucket: Dashboard) -> None:
        """Should not flag queries without time buckets."""
        rule = ESQLDynamicTimeBucketRule()
        violations = rule.check(dashboard_without_bucket, {})

        assert len(violations) == 0
