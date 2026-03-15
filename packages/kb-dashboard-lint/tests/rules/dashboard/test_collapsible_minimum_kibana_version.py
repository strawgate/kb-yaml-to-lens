"""Tests for CollapsibleMinimumKibanaVersionRule."""

from dashboard_lint.rules.dashboard import CollapsibleMinimumKibanaVersionRule
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.collapsible import CollapsiblePanel, SectionConfig
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.markdown.config import MarkdownPanelConfig


def _dashboard_with_section(minimum_kibana_version: str | None) -> Dashboard:
    return Dashboard(
        name='Section Dashboard',
        minimum_kibana_version=minimum_kibana_version,
        panels=[
            CollapsiblePanel(
                title='Section',
                section=SectionConfig(
                    panels=[
                        MarkdownPanel(markdown=MarkdownPanelConfig(content='Inside section')),
                    ]
                ),
            )
        ],
    )


class TestCollapsibleMinimumKibanaVersionRule:
    """Tests for CollapsibleMinimumKibanaVersionRule."""

    def test_passes_when_no_sections(self) -> None:
        """Should not flag dashboards without section panels."""
        dashboard = Dashboard(
            name='No Section Dashboard',
            panels=[MarkdownPanel(markdown=MarkdownPanelConfig(content='Hello'))],
        )

        rule = CollapsibleMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 0

    def test_detects_missing_minimum_version(self) -> None:
        """Should flag section dashboards missing minimum_kibana_version."""
        dashboard = _dashboard_with_section(minimum_kibana_version=None)

        rule = CollapsibleMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'collapsible-minimum-kibana-version'
        assert 'minimum_kibana_version' in violations[0].message

    def test_detects_invalid_minimum_version(self) -> None:
        """Should flag invalid minimum_kibana_version values."""
        dashboard = _dashboard_with_section(minimum_kibana_version='latest')

        rule = CollapsibleMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'collapsible-minimum-kibana-version'
        assert 'not a valid version' in violations[0].message

    def test_detects_minimum_version_below_required(self) -> None:
        """Should flag section dashboards targeting unsupported Kibana versions."""
        dashboard = _dashboard_with_section(minimum_kibana_version='9.0.0')

        rule = CollapsibleMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 1
        assert violations[0].rule_id == 'collapsible-minimum-kibana-version'
        assert 'require Kibana >=' in violations[0].message

    def test_passes_with_supported_minimum_version(self) -> None:
        """Should pass when minimum_kibana_version meets the default requirement."""
        dashboard = _dashboard_with_section(minimum_kibana_version='9.1.0')

        rule = CollapsibleMinimumKibanaVersionRule()
        violations = rule.check(dashboard, {})
        assert len(violations) == 0
