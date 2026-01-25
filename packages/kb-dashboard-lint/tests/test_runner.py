"""Tests for the lint runner."""

import dashboard_lint.rules as _rules  # pyright: ignore[reportUnusedImport]
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.config import LintConfig, RuleConfig
from dashboard_lint.registry import default_registry
from dashboard_lint.runner import LintRunner, check_dashboards
from dashboard_lint.types import Severity


class TestLintRunner:
    """Tests for LintRunner."""

    def test_runs_all_rules(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should run all registered rules."""
        runner = LintRunner()
        violations = runner.run([dashboard_with_markdown_header])

        # Should find at least the markdown header violation
        rule_ids = {v.rule_id for v in violations}
        assert 'markdown-header-height' in rule_ids

    def test_respects_disabled_rules(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should skip disabled rules."""
        config = LintConfig(
            rules={
                'markdown-header-height': RuleConfig(enabled=False),
            }
        )
        runner = LintRunner(config=config)
        violations = runner.run([dashboard_with_markdown_header])

        # Should not find markdown header violations
        rule_ids = {v.rule_id for v in violations}
        assert 'markdown-header-height' not in rule_ids

    def test_respects_severity_off(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should skip rules with severity=off."""
        config = LintConfig(
            rules={
                'markdown-header-height': RuleConfig(severity=Severity.OFF),
            }
        )
        runner = LintRunner(config=config)
        violations = runner.run([dashboard_with_markdown_header])

        # Should not find markdown header violations
        rule_ids = {v.rule_id for v in violations}
        assert 'markdown-header-height' not in rule_ids

    def test_overrides_severity(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should apply severity override from config."""
        config = LintConfig(
            rules={
                'markdown-header-height': RuleConfig(severity=Severity.ERROR),
            }
        )
        runner = LintRunner(config=config)
        violations = runner.run([dashboard_with_markdown_header])

        # Should find violation with overridden severity
        markdown_violations = [v for v in violations if v.rule_id == 'markdown-header-height']
        assert len(markdown_violations) == 1
        assert markdown_violations[0].severity == Severity.ERROR

    def test_sorts_violations(
        self,
        dashboard_with_markdown_header: Dashboard,
        dashboard_without_dataset_filter: Dashboard,
    ) -> None:
        """Should sort violations by severity then dashboard name."""
        config = LintConfig(
            rules={
                'markdown-header-height': RuleConfig(severity=Severity.WARNING),
                'dashboard-dataset-filter': RuleConfig(severity=Severity.ERROR),
            }
        )
        runner = LintRunner(config=config)
        violations = runner.run([dashboard_with_markdown_header, dashboard_without_dataset_filter])

        # Ensure we actually have violations to test ordering
        assert len(violations) > 0, 'Expected at least one violation'

        # Errors should come before warnings
        error_indices = [i for i, v in enumerate(violations) if v.severity == Severity.ERROR]
        warning_indices = [i for i, v in enumerate(violations) if v.severity == Severity.WARNING]
        assert len(error_indices) > 0, 'Expected at least one ERROR violation'
        assert len(warning_indices) > 0, 'Expected at least one WARNING violation'
        assert max(error_indices) < min(warning_indices)


class TestCheckDashboards:
    """Tests for check_dashboards convenience function."""

    def test_check_dashboards(self, dashboard_with_markdown_header: Dashboard) -> None:
        """Should work as a convenience function."""
        violations = check_dashboards([dashboard_with_markdown_header])

        # Should find violations
        assert len(violations) > 0


class TestRegistry:
    """Tests for the rule registry."""

    def test_rules_registered(self) -> None:
        """All built-in rules should be registered.

        Note: This test uses exact equality intentionally to ensure tests
        are updated when new rules are added. If adding a new rule, add its
        ID to the expected_rules set below.
        """
        expected_rules = {
            # Dashboard rules
            'dashboard-dataset-filter',
            # Panel rules
            'markdown-header-height',
            'panel-description-recommended',
            'panel-min-width',
            # Chart rules
            'datatable-row-density',
            'dimension-missing-label',
            'esql-dynamic-time-bucket',
            'esql-field-escaping',
            'esql-sql-syntax',
            'esql-where-clause',
            'gauge-goal-without-max',
            'metric-multiple-metrics-width',
            'metric-redundant-label',
            'panel-height-for-content',
            'pie-chart-dimension-count',
        }
        actual_rules = set(default_registry.get_rule_ids())

        assert expected_rules == actual_rules

    def test_get_rule(self) -> None:
        """Should retrieve rules by ID."""
        rule = default_registry.get_rule('markdown-header-height')
        assert rule is not None
        assert rule.id == 'markdown-header-height'

    def test_get_nonexistent_rule(self) -> None:
        """Should return None for nonexistent rules."""
        rule = default_registry.get_rule('nonexistent-rule')
        assert rule is None
