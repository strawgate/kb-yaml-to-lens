"""Lint rules for chart dimensions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard  # noqa: TC001
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation


def _get_dimension_field(dimension: object) -> str | None:
    """Extract the field name from a dimension object.

    Args:
        dimension: A dimension configuration object.

    Returns:
        The field name if available, None otherwise.

    """
    if hasattr(dimension, 'field'):
        return dimension.field  # pyright: ignore[reportAny]
    if hasattr(dimension, 'type'):
        dim_type = dimension.type  # pyright: ignore[reportAny]
        if dim_type == 'filters':
            return '(filters)'
        if dim_type == 'date_histogram':
            return '@timestamp'
    return None


@dataclass(frozen=True)
class DimensionMissingLabelRule:
    """Rule: Dimensions should have explicit labels.

    Setting explicit labels for dimensions improves the readability
    of charts by providing meaningful axis labels and legends instead
    of raw field names.
    """

    id: str = 'dimension-missing-label'
    description: str = 'Dimensions should have explicit labels'
    default_severity: Severity = Severity.INFO

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:  # noqa: ARG002
        """Check Lens panels for dimensions without labels.

        Args:
            dashboard: The dashboard to check.
            options: Rule options (currently unused).

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import LensPanel

        violations: list[Violation] = []

        for panel_idx, panel in enumerate(dashboard.panels):
            if not isinstance(panel, LensPanel):
                continue

            config = panel.lens

            # Check breakdown dimension if present
            if hasattr(config, 'breakdown') and config.breakdown is not None:
                dimension = config.breakdown
                if hasattr(dimension, 'label') and (dimension.label is None or len(dimension.label) == 0):
                    field_name = _get_dimension_field(dimension) or 'unknown'
                    violations.append(
                        Violation(
                            rule_id=self.id,
                            message=f"Dimension '{field_name}' should have an explicit label",
                            severity=self.default_severity,
                            dashboard_name=dashboard.name,
                            panel_title=panel.title if len(panel.title) > 0 else None,
                            location=f'panels[{panel_idx}].lens.breakdown',
                        )
                    )

            # Check horizontal dimension if present (for XY charts)
            if hasattr(config, 'horizontal') and config.horizontal is not None:
                dimension = config.horizontal
                if hasattr(dimension, 'label') and (dimension.label is None or len(dimension.label) == 0):
                    field_name = _get_dimension_field(dimension) or 'unknown'
                    violations.append(
                        Violation(
                            rule_id=self.id,
                            message=f"Dimension '{field_name}' should have an explicit label",
                            severity=self.default_severity,
                            dashboard_name=dashboard.name,
                            panel_title=panel.title if len(panel.title) > 0 else None,
                            location=f'panels[{panel_idx}].lens.horizontal',
                        )
                    )

            # Check vertical dimension if present (for horizontal bar charts)
            if hasattr(config, 'vertical') and config.vertical is not None:
                dimension = config.vertical
                if hasattr(dimension, 'label') and (dimension.label is None or len(dimension.label) == 0):
                    field_name = _get_dimension_field(dimension) or 'unknown'
                    violations.append(
                        Violation(
                            rule_id=self.id,
                            message=f"Dimension '{field_name}' should have an explicit label",
                            severity=self.default_severity,
                            dashboard_name=dashboard.name,
                            panel_title=panel.title if len(panel.title) > 0 else None,
                            location=f'panels[{panel_idx}].lens.vertical',
                        )
                    )

        return violations


# Register rule with the default registry
register_rule(DimensionMissingLabelRule())
