"""Rule: Dimensions should have explicit labels."""

from dataclasses import dataclass

from dashboard_lint.rules.core import ChartContext, ChartRule, EmptyOptions, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import (
    ESQLPanel,
    LensAreaPanelConfig,
    LensBarPanelConfig,
    LensLinePanelConfig,
    LensMetricPanelConfig,
    LensMosaicPanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.lens.dimensions.config import (
    BaseLensDimension,
    LensDateHistogramDimension,
    LensFiltersDimension,
    LensIntervalsDimension,
    LensMultiTermsDimension,
    LensTermsDimension,
)

type BreakdownConfig = LensMetricPanelConfig | LensLinePanelConfig | LensBarPanelConfig | LensAreaPanelConfig | LensMosaicPanelConfig


def _get_dimension_field(dimension: BaseLensDimension) -> str:
    """Extract the field name from a dimension object."""
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
    """Check if a dimension has an empty or missing label."""
    return dimension.label is None or len(dimension.label) == 0


@chart_rule
@dataclass(frozen=True)
class DimensionMissingLabelRule(ChartRule[BreakdownConfig, EmptyOptions]):
    """Rule: Dimensions should have explicit labels.

    Setting explicit labels for dimensions improves the readability
    of charts by providing meaningful axis labels and legends instead
    of raw field names.
    """

    id: str = 'dimension-missing-label'
    description: str = 'Dimensions should have explicit labels'
    default_severity: Severity = Severity.INFO
    options_model: type[EmptyOptions] = EmptyOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: BreakdownConfig,
        context: ChartContext,
        options: EmptyOptions,  # noqa: ARG002
    ) -> ViolationResult:
        """Check Lens panels for dimensions without labels.

        Args:
            panel: The chart panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Validated rule options (empty for this rule).

        Returns:
            Violation if dimension missing label, None otherwise.

        """
        violations: list[Violation] = []

        # Check dimension field (XY charts and Mosaic charts have this)
        if (
            isinstance(config, (LensLinePanelConfig, LensBarPanelConfig, LensAreaPanelConfig, LensMosaicPanelConfig))
            and config.dimension is not None
            and _dimension_has_empty_label(config.dimension)
        ):
            field_name = _get_dimension_field(config.dimension)
            violations.append(
                Violation(
                    rule_id=self.id,
                    message=f"Dimension '{field_name}' should have an explicit label",
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('dimension'),
                )
            )

        # Check breakdown dimension
        if config.breakdown is not None and _dimension_has_empty_label(config.breakdown):
            field_name = _get_dimension_field(config.breakdown)
            violations.append(
                Violation(
                    rule_id=self.id,
                    message=f"Dimension '{field_name}' should have an explicit label",
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('breakdown'),
                )
            )

        return violations if violations else None
