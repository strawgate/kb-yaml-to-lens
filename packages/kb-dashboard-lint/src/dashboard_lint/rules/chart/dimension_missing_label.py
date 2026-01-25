"""Rule: Dimensions should have explicit labels."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    LensAreaPanelConfig,
    LensBarPanelConfig,
    LensLinePanelConfig,
    LensMetricPanelConfig,
    LensMosaicPanelConfig,
    LensPanel,
    LensPanelConfig,
)
from dashboard_compiler.panels.charts.lens.dimensions.config import (
    BaseLensDimension,
    LensDateHistogramDimension,
    LensFiltersDimension,
    LensIntervalsDimension,
    LensMultiTermsDimension,
    LensTermsDimension,
)
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

# Lens config types that have a breakdown dimension
CONFIGS_WITH_BREAKDOWN = (
    LensMetricPanelConfig,
    LensLinePanelConfig,
    LensBarPanelConfig,
    LensAreaPanelConfig,
    LensMosaicPanelConfig,
)


def _get_dimension_field(dimension: BaseLensDimension) -> str:
    """Extract the field name from a dimension object.

    Args:
        dimension: A dimension configuration object.

    Returns:
        The field name or a descriptive string.

    """
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
    return 'unknown'


def _dimension_has_empty_label(dimension: BaseLensDimension) -> bool:
    """Check if a dimension has an empty or missing label.

    Args:
        dimension: A dimension configuration object.

    Returns:
        True if the dimension lacks a label, False otherwise.

    """
    return dimension.label is None or len(dimension.label) == 0


@chart_rule(config_types=CONFIGS_WITH_BREAKDOWN)
@dataclass(frozen=True)
class DimensionMissingLabelRule(ChartRule):
    """Rule: Dimensions should have explicit labels.

    Setting explicit labels for dimensions improves the readability
    of charts by providing meaningful axis labels and legends instead
    of raw field names.
    """

    id: str = 'dimension-missing-label'
    description: str = 'Dimensions should have explicit labels'
    default_severity: Severity = Severity.INFO

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: LensPanelConfig | ESQLPanelConfig,
        context: ChartContext,
        options: dict[str, Any],  # noqa: ARG002
    ) -> ViolationResult:
        """Check Lens panels for dimensions without labels.

        Args:
            panel: The chart panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Rule options (currently unused).

        Returns:
            Violation if dimension missing label, None otherwise.

        """
        # Type is guaranteed by config_types filter
        if not isinstance(config, CONFIGS_WITH_BREAKDOWN):
            return None

        # Check breakdown dimension
        if config.breakdown is not None and _dimension_has_empty_label(config.breakdown):
            field_name = _get_dimension_field(config.breakdown)
            return Violation(
                rule_id=self.id,
                message=f"Dimension '{field_name}' should have an explicit label",
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('breakdown'),
            )

        return None
