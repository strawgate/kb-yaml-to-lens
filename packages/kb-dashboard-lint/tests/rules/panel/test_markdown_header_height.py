"""Tests for MarkdownHeaderHeightRule."""

from dashboard_lint.rules.panel import MarkdownHeaderHeightRule
from dashboard_lint.types import Severity
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.config import Size
from kb_dashboard_core.panels.markdown import MarkdownPanel
from kb_dashboard_core.panels.markdown.config import MarkdownPanelConfig


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

    def test_passes_markdown_without_headers(self) -> None:
        """Should not flag markdown panels without headers, even if short."""
        dashboard = Dashboard(
            name='Test Dashboard',
            panels=[
                MarkdownPanel(
                    title='Plain Text',
                    markdown=MarkdownPanelConfig(content='Just plain text without any headers.'),
                    size=Size(w=24, h=1),  # Very short, but no headers
                ),
            ],
        )

        rule = MarkdownHeaderHeightRule()
        violations = rule.check(dashboard, {})

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
