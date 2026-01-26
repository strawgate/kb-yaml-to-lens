"""Rule: Narrow XY charts should not use side legends."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.base.config import LegendVisibleEnum
from kb_dashboard_core.panels.charts.config import (
    ESQLAreaPanelConfig,
    ESQLBarPanelConfig,
    ESQLLinePanelConfig,
    ESQLPanel,
    LensAreaPanelConfig,
    LensBarPanelConfig,
    LensLinePanelConfig,
    LensPanel,
)

type XYPanelConfig = (
    LensLinePanelConfig | LensBarPanelConfig | LensAreaPanelConfig | ESQLLinePanelConfig | ESQLBarPanelConfig | ESQLAreaPanelConfig
)


class NarrowXYChartSideLegendOptions(BaseModel):
    """Options for the narrow-xy-chart-side-legend rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    max_width: int = Field(
        default=16,
        ge=1,
        description='Maximum width for XY charts to use side legends without warning',
    )


@chart_rule
@dataclass(frozen=True)
class NarrowXYChartSideLegendRule(ChartRule[XYPanelConfig, NarrowXYChartSideLegendOptions]):
    """Rule: Narrow XY charts should not use side legends.

    When XY charts (line, bar, area) are narrow (e.g., 3 charts side-by-side),
    side legends consume too much horizontal space, making the chart area
    too small for readability.

    Options:
        max_width (int): Maximum width for XY charts to use side legends. Default: 16.
    """

    id: str = 'narrow-xy-chart-side-legend'
    description: str = 'Narrow XY charts should use bottom legends instead of side legends'
    default_severity: Severity = Severity.WARNING
    options_model: type[NarrowXYChartSideLegendOptions] = NarrowXYChartSideLegendOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,
        config: XYPanelConfig,
        context: ChartContext,
        options: NarrowXYChartSideLegendOptions,
    ) -> ViolationResult:
        """Check XY chart for narrow width with side legend.

        Args:
            panel: The XY panel to check.
            config: The panel's XY chart configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if chart is narrow and has side legend, None otherwise.

        """
        width = panel.size.width

        if width > options.max_width:
            return None

        legend = config.legend
        if legend is None:
            return Violation(
                rule_id=self.id,
                message=(
                    f'Chart has width {width} (≤{options.max_width}) with default side legend. '
                    f'Use `legend: {{ position: bottom }}` for better readability.'
                ),
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('legend'),
            )

        if legend.visible == LegendVisibleEnum.HIDE:
            return None

        position = legend.position
        if position is None or position in ('left', 'right'):
            return Violation(
                rule_id=self.id,
                message=(
                    f'Chart has width {width} (≤{options.max_width}) with side legend (position: {position or "right"!r}). '
                    f'Use `legend: {{ position: bottom }}` for better readability.'
                ),
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('legend.position'),
            )

        return None
