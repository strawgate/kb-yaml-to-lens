"""Tests for ESQLTSMetricsMinVersionRule."""

import pytest

from dashboard_lint.rules.chart import ESQLTSMetricsMinVersionRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLLinePanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.xy.metrics import XYESQLMetric
from kb_dashboard_core.panels.collapsible import CollapsiblePanel, SectionConfig


@pytest.fixture
def dashboard_with_ts_metrics() -> Dashboard:
    """Create a dashboard using TS against metrics-* source."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='CPU over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='TS metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                    metrics=[XYESQLMetric(field='cpu')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_ts_logs() -> Dashboard:
    """Create a dashboard using TS against non-metrics source."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='Logs over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='TS logs-* | STATS count = COUNT(*)',
                    metrics=[XYESQLMetric(field='count')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_from_metrics_no_minimum() -> Dashboard:
    """Create a dashboard using FROM against metrics-* source without minimum version."""
    return Dashboard(
        name='Test Dashboard',
        panels=[
            ESQLPanel(
                title='CPU over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                    metrics=[XYESQLMetric(field='cpu')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_from_metrics_minimum_920() -> Dashboard:
    """Create a dashboard using FROM against metrics-* source with min version 9.2.0."""
    return Dashboard(
        name='Test Dashboard',
        minimum_kibana_version='9.2.0',
        panels=[
            ESQLPanel(
                title='CPU over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                    metrics=[XYESQLMetric(field='cpu')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_from_metrics_minimum_910() -> Dashboard:
    """Create a dashboard using FROM against metrics-* source with min version 9.1.0."""
    return Dashboard(
        name='Test Dashboard',
        minimum_kibana_version='9.1.0',
        panels=[
            ESQLPanel(
                title='CPU over time',
                esql=ESQLLinePanelConfig(
                    type='line',
                    query='FROM metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                    metrics=[XYESQLMetric(field='cpu')],
                ),
            ),
        ],
    )


@pytest.fixture
def dashboard_with_collapsible_from_metrics_minimum_920() -> Dashboard:
    """Create section dashboard with FROM metrics-* source and min version 9.2.0."""
    return Dashboard(
        name='Test Dashboard',
        minimum_kibana_version='9.2.0',
        panels=[
            CollapsiblePanel(
                title='Section',
                section=SectionConfig(
                    panels=[
                        ESQLPanel(
                            title='CPU over time',
                            esql=ESQLLinePanelConfig(
                                type='line',
                                query='FROM metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                                metrics=[XYESQLMetric(field='cpu')],
                            ),
                        )
                    ]
                ),
            )
        ],
    )


@pytest.fixture
def dashboard_with_collapsible_from_metrics_minimum_910() -> Dashboard:
    """Create section dashboard with FROM metrics-* source and min version 9.1.0."""
    return Dashboard(
        name='Test Dashboard',
        minimum_kibana_version='9.1.0',
        panels=[
            CollapsiblePanel(
                title='Section',
                section=SectionConfig(
                    panels=[
                        ESQLPanel(
                            title='CPU over time',
                            esql=ESQLLinePanelConfig(
                                type='line',
                                query='FROM metrics-* | STATS cpu = AVG(system.cpu.total.norm.pct)',
                                metrics=[XYESQLMetric(field='cpu')],
                            ),
                        )
                    ]
                ),
            )
        ],
    )


class TestESQLTSMetricsMinVersionRule:
    """Tests for ESQLTSMetricsMinVersionRule."""

    def test_passes_ts_metrics(self, dashboard_with_ts_metrics: Dashboard) -> None:
        """Should not flag TS metrics-* usage."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_ts_metrics, {})

        assert len(violations) == 0

    def test_passes_ts_non_metrics(self, dashboard_with_ts_logs: Dashboard) -> None:
        """Should not flag TS for non-metrics sources."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_ts_logs, {})

        assert len(violations) == 0

    def test_passes_from_metrics_without_declared_minimum(
        self,
        dashboard_with_from_metrics_no_minimum: Dashboard,
    ) -> None:
        """Should not warn when no minimum_kibana_version is declared."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_from_metrics_no_minimum, {})

        assert len(violations) == 0

    def test_passes_from_metrics_when_minimum_below_920(
        self,
        dashboard_with_from_metrics_minimum_910: Dashboard,
    ) -> None:
        """Should not warn when minimum_kibana_version is below 9.2."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_from_metrics_minimum_910, {})

        assert len(violations) == 0

    def test_detects_from_metrics_when_minimum_is_920_or_higher(
        self,
        dashboard_with_from_metrics_minimum_920: Dashboard,
    ) -> None:
        """Should warn when FROM metrics-* is used on dashboards targeting Kibana 9.2+."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_from_metrics_minimum_920, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-ts-metrics-min-version'
        assert 'TS metrics-*' in violations[0].message
        assert violations[0].severity == Severity.WARNING

    def test_detects_from_metrics_in_collapsible_panels_when_minimum_is_920_or_higher(
        self,
        dashboard_with_collapsible_from_metrics_minimum_920: Dashboard,
    ) -> None:
        """Should warn for FROM metrics-* inside section panels on Kibana 9.2+."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_collapsible_from_metrics_minimum_920, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-ts-metrics-min-version'
        assert violations[0].location == 'panels[0].section.panels[0].esql.query'

    def test_passes_from_metrics_in_collapsible_panels_when_minimum_below_920(
        self,
        dashboard_with_collapsible_from_metrics_minimum_910: Dashboard,
    ) -> None:
        """Should not warn for section panels when minimum_kibana_version is below 9.2."""
        rule = ESQLTSMetricsMinVersionRule()
        violations = rule.check(dashboard_with_collapsible_from_metrics_minimum_910, {})

        assert len(violations) == 0
