"""Lint rules for panel sizing and layout."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation

# Minimum recommended heights for different chart types
MIN_HEIGHTS: dict[str, int] = {
    'metric': 3,
    'gauge': 3,
    'line': 4,
    'bar': 4,
    'area': 4,
    'pie': 4,
    'tagcloud': 4,
    'datatable': 5,
    'heatmap': 5,
    'mosaic': 5,
}


@dataclass(frozen=True)
class PanelMinWidthRule:
    """Rule: Panels should have minimum width to be readable.

    Very narrow panels (less than 6 grid units) are often too small to
    display content effectively and may indicate a configuration error.
    """

    id: str = 'panel-min-width'
    description: str = 'Panels should have minimum width for readability'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check panels for insufficient width.

        Args:
            dashboard: The dashboard to check.
            options: Rule options. Supports:
                - min_width (int): Minimum width in grid units. Default: 6.

        Returns:
            List of violations found.

        """
        violations: list[Violation] = []
        min_width = options.get('min_width', 6)

        for idx, panel in enumerate(dashboard.panels):
            width = panel.size.w

            if width < min_width:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Panel width {width} is below minimum {min_width}; narrow panels may be hard to read',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].size',
                    )
                )

        return violations


@dataclass(frozen=True)
class PanelHeightForContentRule:
    """Rule: Panels should have minimum height appropriate for their content type.

    Different chart types require different minimum heights to display
    effectively. For example, datatables need more vertical space than
    metric displays.
    """

    id: str = 'panel-height-for-content'
    description: str = 'Panels should have minimum height for their chart type'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check panels for insufficient height based on content type.

        Args:
            dashboard: The dashboard to check.
            options: Rule options (currently unused).

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel

        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            height = panel.size.h
            chart_type: str | None = None

            if isinstance(panel, LensPanel):
                chart_type = panel.lens.type
            elif isinstance(panel, ESQLPanel):
                chart_type = panel.esql.type

            if chart_type is None:
                continue

            # Get custom min heights from options or use defaults
            custom_heights = options.get('min_heights', {})
            min_height = custom_heights.get(chart_type, MIN_HEIGHTS.get(chart_type))

            if min_height is not None and height < min_height:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'{chart_type} chart has height {height} but should be at least {min_height}',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].size',
                    )
                )

        return violations


@dataclass(frozen=True)
class PanelDescriptionRecommendedRule:
    """Rule: Panels should have descriptions for accessibility.

    Panel descriptions provide context for dashboard viewers and improve
    accessibility for screen readers.
    """

    id: str = 'panel-description-recommended'
    description: str = 'Panels should have descriptions for accessibility'
    default_severity: Severity = Severity.INFO

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:  # noqa: ARG002
        """Check panels for missing descriptions.

        Args:
            dashboard: The dashboard to check.
            options: Rule options (currently unused).

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.markdown import MarkdownPanel

        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            # Skip markdown panels (they are self-describing)
            if isinstance(panel, MarkdownPanel):
                continue

            # Skip panels without titles (they likely don't need descriptions)
            if len(panel.title) == 0:
                continue

            if panel.description is None or len(panel.description.strip()) == 0:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message='Consider adding a description to improve accessibility',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title,
                        location=f'panels[{idx}]',
                    )
                )

        return violations


# Register rules with the default registry
register_rule(PanelMinWidthRule())
register_rule(PanelHeightForContentRule())
register_rule(PanelDescriptionRecommendedRule())
