"""Tests for DashboardMissingDescriptionRule."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.rules.dashboard import DashboardMissingDescriptionRule
from dashboard_lint.types import Severity


@pytest.fixture
def dashboard_with_description() -> Dashboard:
    """Create a dashboard with a description."""
    return Dashboard(
        name='Test Dashboard',
        description='This dashboard shows system metrics.',
        panels=[],
    )


@pytest.fixture
def dashboard_without_description() -> Dashboard:
    """Create a dashboard without a description."""
    return Dashboard(
        name='Test Dashboard',
        panels=[],
    )


@pytest.fixture
def dashboard_with_empty_description() -> Dashboard:
    """Create a dashboard with empty description."""
    return Dashboard(
        name='Test Dashboard',
        description='   ',
        panels=[],
    )


class TestDashboardMissingDescriptionRule:
    """Tests for DashboardMissingDescriptionRule."""

    def test_passes_with_description(self, dashboard_with_description: Dashboard) -> None:
        """Should not flag dashboards with descriptions."""
        rule = DashboardMissingDescriptionRule()
        violations = rule.check(dashboard_with_description, {})

        assert len(violations) == 0

    def test_detects_missing_description(self, dashboard_without_description: Dashboard) -> None:
        """Should detect missing dashboard description."""
        rule = DashboardMissingDescriptionRule()
        violations = rule.check(dashboard_without_description, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'dashboard-missing-description'
        assert 'description' in violations[0].message.lower()
        assert violations[0].severity == Severity.INFO

    def test_detects_empty_description(self, dashboard_with_empty_description: Dashboard) -> None:
        """Should detect empty (whitespace-only) descriptions."""
        rule = DashboardMissingDescriptionRule()
        violations = rule.check(dashboard_with_empty_description, {})

        assert len(violations) == 1
        assert violations[0].rule_id == 'dashboard-missing-description'
