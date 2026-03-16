"""Tests for ESQLMinimumKibanaVersionRule."""

from dashboard_lint.rules.dashboard import ESQLMinimumKibanaVersionRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.charts.config import ESQLMetricPanelConfig, ESQLPanel
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLMetric
from kb_dashboard_core.panels.collapsible import CollapsiblePanel, SectionConfig
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.markdown.config import MarkdownPanelConfig


def _dashboard_with_esql_panel(minimum_kibana_version: str | None) -> Dashboard:
    return Dashboard(
        name='ESQL Dashboard',
        minimum_kibana_version=minimum_kibana_version,
        panels=[
            ESQLPanel(
                title='Requests',
                esql=ESQLMetricPanelConfig(
                    type='metric',
                    query='FROM logs-* | STATS count = COUNT(*)',
                    primary=ESQLMetric(field='count'),
                ),
            )
        ],
    )


def _dashboard_with_esql_in_section(minimum_kibana_version: str | None) -> Dashboard:
    return Dashboard(
        name='Nested ESQL Dashboard',
        minimum_kibana_version=minimum_kibana_version,
        panels=[
            CollapsiblePanel(
                title='Section',
                section=SectionConfig(
                    panels=[
                        ESQLPanel(
                            title='Requests',
                            esql=ESQLMetricPanelConfig(
                                type='metric',
                                query='FROM logs-* | STATS count = COUNT(*)',
                                primary=ESQLMetric(field='count'),
                            ),
                        )
                    ]
                ),
            )
        ],
    )


class TestESQLMinimumKibanaVersionRule:
    """Tests for ESQLMinimumKibanaVersionRule."""

    def test_passes_when_no_esql_panels(self) -> None:
        """Should not flag dashboards that do not use ES|QL panels."""
        dashboard = Dashboard(
            name='No ESQL Dashboard',
            panels=[MarkdownPanel(markdown=MarkdownPanelConfig(content='Hello'))],
        )

        rule = ESQLMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 0

    def test_detects_missing_minimum_version(self) -> None:
        """Should flag ES|QL dashboards missing minimum_kibana_version."""
        dashboard = _dashboard_with_esql_panel(minimum_kibana_version=None)

        rule = ESQLMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-minimum-kibana-version'
        assert 'minimum_kibana_version' in violations[0].message

    def test_detects_invalid_minimum_version(self) -> None:
        """Should flag invalid minimum_kibana_version values."""
        dashboard = _dashboard_with_esql_panel(minimum_kibana_version='latest')

        rule = ESQLMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-minimum-kibana-version'
        assert 'not a valid version' in violations[0].message

    def test_detects_minimum_version_below_required(self) -> None:
        """Should flag ES|QL dashboards targeting unsupported Kibana versions."""
        dashboard = _dashboard_with_esql_panel(minimum_kibana_version='8.13.0')

        rule = ESQLMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-minimum-kibana-version'
        assert 'require Kibana >=' in violations[0].message

    def test_passes_with_supported_minimum_version(self) -> None:
        """Should pass when minimum_kibana_version meets the default requirement."""
        dashboard = _dashboard_with_esql_panel(minimum_kibana_version='8.14.0')

        rule = ESQLMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 0

    def test_detects_esql_in_collapsible_panels(self) -> None:
        """Should inspect ES|QL panels nested in section panels."""
        dashboard = _dashboard_with_esql_in_section(minimum_kibana_version=None)

        rule = ESQLMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'esql-minimum-kibana-version'
