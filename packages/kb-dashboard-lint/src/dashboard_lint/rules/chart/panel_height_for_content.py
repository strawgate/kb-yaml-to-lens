"""Rule: Panels should have minimum height for their chart type."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    LensPanel,
    LensPanelConfig,
)

# Minimum recommended heights for different chart types.
# Update this mapping when new chart types are added or height requirements change.
# If a chart type is not in this mapping and no custom override is provided via
# options.min_heights, no height check is performed and the chart is allowed.
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

type AnyChartConfig = LensPanelConfig | ESQLPanelConfig


class PanelHeightForContentOptions(BaseModel):
    """Options for the panel-height-for-content rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    min_heights: dict[str, int] = Field(
        default_factory=dict,
        description='Override default minimum heights per chart type',
    )


@chart_rule
@dataclass(frozen=True)
class PanelHeightForContentRule(ChartRule[AnyChartConfig, PanelHeightForContentOptions]):
    """Rule: Panels should have minimum height for their chart type.

    Different chart types require different minimum heights to display
    effectively. For example, datatables need more vertical space than
    metric displays.

    Options:
        min_heights (dict): Override default heights per chart type.
    """

    id: str = 'panel-height-for-content'
    description: str = 'Panels should have minimum height for their chart type'
    default_severity: Severity = Severity.WARNING
    options_model: type[PanelHeightForContentOptions] = PanelHeightForContentOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,
        config: AnyChartConfig,  # noqa: ARG002
        context: ChartContext,
        options: PanelHeightForContentOptions,
    ) -> ViolationResult:
        """Check panel for insufficient height based on chart type.

        Height resolution:
        1. Check options.min_heights for custom override by chart_type
        2. Fall back to MIN_HEIGHTS defaults
        3. If chart_type not found in either, no check is performed (passes)

        Args:
            panel: The chart panel to check.
            config: The panel's chart configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if height below minimum for chart type, None otherwise.

        """
        height = panel.size.h
        chart_type = context.chart_type

        # Get custom min heights from options or use defaults
        min_height = options.min_heights.get(chart_type, MIN_HEIGHTS.get(chart_type))

        if min_height is not None and height < min_height:
            return Violation(
                rule_id=self.id,
                message=f'{chart_type} chart has height {height} but should be at least {min_height}',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('size'),
            )

        return None
