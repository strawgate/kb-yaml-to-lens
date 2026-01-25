"""Lint rules for chart dimensions."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation


def _get_dimension_field(dimension: Any) -> str | None:
    """Extract the field name from a dimension object.

    Args:
        dimension: A dimension configuration object.

    Returns:
        The field name if available, None otherwise.

    """
    from dashboard_compiler.panels.charts.lens.dimensions.config import (
        LensDateHistogramDimension,
        LensFiltersDimension,
        LensIntervalsDimension,
        LensMultiTermsDimension,
        LensTermsDimension,
    )

    if isinstance(dimension, LensTermsDimension):
        return dimension.field
    if isinstance(dimension, LensMultiTermsDimension):
        return ', '.join(dimension.fields)
    if isinstance(dimension, LensDateHistogramDimension):
        return dimension.field
    if isinstance(dimension, LensIntervalsDimension):
        return dimension.field
    if isinstance(dimension, LensFiltersDimension):
        return '(filters)'
    return None


def _dimension_has_empty_label(dimension: Any) -> bool:
    """Check if a dimension has an empty or missing label.

    Args:
        dimension: A dimension configuration object.

    Returns:
        True if the dimension lacks a label, False otherwise.

    """
    from dashboard_compiler.panels.charts.lens.dimensions.config import BaseLensDimension

    if isinstance(dimension, BaseLensDimension):
        return dimension.label is None or len(dimension.label) == 0
    return False


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
        from dashboard_compiler.panels.charts.config import (
            LensAreaPanelConfig,
            LensBarPanelConfig,
            LensLinePanelConfig,
            LensMetricPanelConfig,
            LensMosaicPanelConfig,
            LensPanel,
        )

        # All Lens config types that have a breakdown dimension
        configs_with_breakdown = (
            LensMetricPanelConfig,
            LensLinePanelConfig,
            LensBarPanelConfig,
            LensAreaPanelConfig,
            LensMosaicPanelConfig,
        )

        violations: list[Violation] = []

        for panel_idx, panel in enumerate(dashboard.panels):
            if not isinstance(panel, LensPanel):
                continue

            config = panel.lens

            # Check breakdown dimension on supported chart types
            if (
                isinstance(config, configs_with_breakdown)  # pyright: ignore[reportUnnecessaryIsInstance]
                and config.breakdown is not None
                and _dimension_has_empty_label(config.breakdown)
            ):
                field_name = _get_dimension_field(config.breakdown) or 'unknown'
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

        return violations


# Register rule with the default registry
register_rule(DimensionMissingLabelRule())
