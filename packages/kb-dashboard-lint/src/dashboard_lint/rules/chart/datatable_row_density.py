"""Rule: Large datatables should consider compact density."""

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.panels.charts.config import (
    ESQLDatatablePanelConfig,
    ESQLPanel,
    LensDatatablePanelConfig,
    LensPanel,
)
from dashboard_compiler.panels.charts.datatable.config import DatatableDensityEnum
from dashboard_lint.rules.core import ChartContext, ChartRule, ViolationResult, chart_rule
from dashboard_lint.types import Severity, Violation

type DatatableConfig = LensDatatablePanelConfig | ESQLDatatablePanelConfig


@chart_rule
@dataclass(frozen=True)
class DatatableRowDensityRule(ChartRule[DatatableConfig]):
    """Rule: Large datatables should consider compact density.

    Datatables with many columns or rows benefit from compact density
    to show more information without scrolling.

    Options:
        min_columns (int): Minimum columns before suggesting compact. Default: 5.
    """

    id: str = 'datatable-row-density'
    description: str = 'Large datatables should consider compact density'
    default_severity: Severity = Severity.INFO
    config_types: tuple[type, ...] = (LensDatatablePanelConfig, ESQLDatatablePanelConfig)

    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,  # noqa: ARG002
        config: DatatableConfig,
        context: ChartContext,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check datatable for density settings.

        Args:
            panel: The datatable panel to check.
            config: The panel's datatable configuration.
            context: Chart context with location helpers.
            options: Rule options with optional 'min_columns' key.

        Returns:
            Violation if many columns and not compact, None otherwise.

        """
        min_cols = options.get('min_columns', 5)

        column_count = 0
        is_compact = False

        if config.columns is not None:
            column_count = len(config.columns)
        if config.appearance is not None and config.appearance.density == DatatableDensityEnum.COMPACT:
            is_compact = True

        if column_count >= min_cols and not is_compact:
            return Violation(
                rule_id=self.id,
                message=f'Datatable has {column_count} columns; consider using compact row_density',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location(),
            )

        return None
