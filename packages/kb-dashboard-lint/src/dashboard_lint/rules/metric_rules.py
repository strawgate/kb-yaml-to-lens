"""Lint rules for Metric panels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard  # noqa: TC001
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation


@dataclass(frozen=True)
class MetricRedundantLabelRule:
    """Rule: Metric primary label should not duplicate panel title.

    When a metric's primary label is the same as the panel title, the title
    is redundant and should be hidden using `hide_title: true`. This avoids
    displaying the same text twice.
    """

    id: str = 'metric-redundant-label'
    description: str = 'Metric primary label matching title should use hide_title: true'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:  # noqa: ARG002
        """Check metric panels for redundant title/label combinations.

        Args:
            dashboard: The dashboard to check.
            options: Rule options (currently unused).

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel

        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            # Skip panels without titles
            if len(panel.title) == 0:
                continue

            # Check if hide_title is already set
            if panel.hide_title is True:
                continue

            primary_label: str | None = None
            chart_type: str | None = None

            if isinstance(panel, LensPanel):
                config = panel.lens
                if hasattr(config, 'type') and config.type == 'metric':
                    chart_type = 'lens.metric'
                    if hasattr(config, 'primary') and hasattr(config.primary, 'label'):
                        primary_label = config.primary.label
            elif isinstance(panel, ESQLPanel):
                config = panel.esql
                if hasattr(config, 'type') and config.type == 'metric':
                    chart_type = 'esql.metric'
                    if hasattr(config, 'primary') and hasattr(config.primary, 'label'):
                        primary_label = config.primary.label

            # Check if primary label matches title
            if chart_type is not None and primary_label is not None and primary_label.strip().lower() == panel.title.strip().lower():
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f"Primary label '{primary_label}' matches panel title; consider using hide_title: true",
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title,
                        location=f'panels[{idx}].{chart_type}',
                    )
                )

        return violations


# Register rule with the default registry
register_rule(MetricRedundantLabelRule())
