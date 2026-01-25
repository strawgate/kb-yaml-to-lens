"""Rule: Large datatables should consider compact density."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.panels.charts.config import (
    ESQLDatatablePanelConfig,
    ESQLPanel,
    LensDatatablePanelConfig,
    LensPanel,
)
from kb_dashboard_core.panels.charts.datatable.config import DatatableDensityEnum

type DatatableConfig = LensDatatablePanelConfig | ESQLDatatablePanelConfig


class DatatableRowDensityOptions(BaseModel):
    """Options for the datatable-row-density rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    min_columns: int = Field(
        default=5,
        ge=1,
        description='Minimum columns before suggesting compact density',
    )


@chart_rule
@dataclass(frozen=True)
class DatatableRowDensityRule(ChartRule[DatatableConfig, DatatableRowDensityOptions]):
    """Rule: Large datatables should consider compact density.

    Datatables with many columns benefit from compact density
    to show more information without scrolling.

    Options:
        min_columns (int): Minimum columns before suggesting compact. Default: 5.
    """

    id: str = 'datatable-row-density'
    description: str = 'Large datatables should consider compact density'
    default_severity: Severity = Severity.INFO
    options_model: type[DatatableRowDensityOptions] = DatatableRowDensityOptions

    def check_chart(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: DatatableConfig,
        context: ChartContext,
        options: DatatableRowDensityOptions,
    ) -> ViolationResult:
        """Check datatable for density settings.

        Args:
            panel: The datatable panel to check.
            config: The panel's datatable configuration.
            context: Chart context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if many columns and not compact, None otherwise.

        """
        column_count = 0
        is_compact = False

        if config.columns is not None:
            column_count = len(config.columns)
        if config.appearance is not None and config.appearance.density == DatatableDensityEnum.COMPACT:
            is_compact = True

        if column_count >= options.min_columns and not is_compact:
            return Violation(
                rule_id=self.id,
                message=f'Datatable has {column_count} columns; consider using compact row_density',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
