"""Lint rules for chart-specific configurations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard  # noqa: TC001
from dashboard_lint.registry import register_rule
from dashboard_lint.types import Severity, Violation


@dataclass(frozen=True)
class MetricMultipleMetricsWidthRule:
    """Rule: Metric panels with multiple metrics need adequate width.

    When a metric panel displays secondary or maximum values in addition
    to the primary metric, it needs more horizontal space to avoid
    crowding the display.
    """

    id: str = 'metric-multiple-metrics-width'
    description: str = 'Metric panels with multiple metrics should have adequate width'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check metric panels for width vs content complexity.

        Args:
            dashboard: The dashboard to check.
            options: Rule options. Supports:
                - min_width_multiple (int): Minimum width for multi-metric panels. Default: 12.

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel

        violations: list[Violation] = []
        min_width = options.get('min_width_multiple', 12)

        for idx, panel in enumerate(dashboard.panels):
            width = panel.size.w
            metric_count = 0
            chart_type: str | None = None

            if isinstance(panel, LensPanel):
                config = panel.lens
                if config.type == 'metric':
                    chart_type = 'lens.metric'
                    metric_count = 1  # primary
                    if hasattr(config, 'secondary') and config.secondary is not None:
                        metric_count += 1
                    if hasattr(config, 'maximum') and config.maximum is not None:
                        metric_count += 1
            elif isinstance(panel, ESQLPanel):
                config = panel.esql
                if config.type == 'metric':
                    chart_type = 'esql.metric'
                    metric_count = 1
                    if hasattr(config, 'secondary') and config.secondary is not None:
                        metric_count += 1
                    if hasattr(config, 'maximum') and config.maximum is not None:
                        metric_count += 1

            if chart_type is not None and metric_count > 1 and width < min_width:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Panel has {metric_count} metrics but width {width} is below recommended {min_width}',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].{chart_type}',
                    )
                )

        return violations


@dataclass(frozen=True)
class GaugeGoalWithoutMaxRule:
    """Rule: Gauge charts with goals should have maximum values.

    When a gauge has a goal threshold, it should also have a maximum
    value defined for the scale to make the goal position meaningful.
    """

    id: str = 'gauge-goal-without-max'
    description: str = 'Gauge charts with goals should define maximum values'
    default_severity: Severity = Severity.WARNING

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:  # noqa: ARG002
        """Check gauge panels for goal without max.

        Args:
            dashboard: The dashboard to check.
            options: Rule options (currently unused).

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel

        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            chart_type: str | None = None
            has_goal = False
            has_max = False

            if isinstance(panel, LensPanel):
                config = panel.lens
                if config.type == 'gauge':
                    chart_type = 'lens.gauge'
                    has_goal = hasattr(config, 'goal') and config.goal is not None
                    has_max = hasattr(config, 'maximum') and config.maximum is not None
            elif isinstance(panel, ESQLPanel):
                config = panel.esql
                if config.type == 'gauge':
                    chart_type = 'esql.gauge'
                    has_goal = hasattr(config, 'goal') and config.goal is not None
                    has_max = hasattr(config, 'maximum') and config.maximum is not None

            if chart_type is not None and has_goal and not has_max:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message='Gauge has goal but no maximum; goal position may be misleading',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].{chart_type}',
                    )
                )

        return violations


@dataclass(frozen=True)
class PieChartDimensionCountRule:
    """Rule: Pie charts with multiple dimensions may be hard to read.

    Multi-level (sunburst) pie charts with multiple dimensions can be
    difficult to interpret. Consider using separate visualizations or
    a different chart type.
    """

    id: str = 'pie-chart-dimension-count'
    description: str = 'Pie charts with multiple dimensions may be hard to read'
    default_severity: Severity = Severity.INFO

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check pie charts for excessive dimensions.

        Args:
            dashboard: The dashboard to check.
            options: Rule options. Supports:
                - max_dimensions (int): Maximum dimensions before warning. Default: 1.

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel

        violations: list[Violation] = []
        max_dims = options.get('max_dimensions', 1)

        for idx, panel in enumerate(dashboard.panels):
            chart_type: str | None = None
            dimension_count = 0

            if isinstance(panel, LensPanel):
                config = panel.lens
                if config.type == 'pie':
                    chart_type = 'lens.pie'
                    if hasattr(config, 'dimensions'):
                        dimension_count = len(config.dimensions)
            elif isinstance(panel, ESQLPanel):
                config = panel.esql
                if config.type == 'pie':
                    chart_type = 'esql.pie'
                    if hasattr(config, 'dimensions'):
                        dimension_count = len(config.dimensions)

            if chart_type is not None and dimension_count > max_dims:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Pie chart has {dimension_count} dimensions; multi-level pies can be hard to read',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].{chart_type}',
                    )
                )

        return violations


@dataclass(frozen=True)
class DatatableRowDensityRule:
    """Rule: Large datatables should consider compact density.

    Datatables with many columns or rows benefit from compact density
    to show more information without scrolling.
    """

    id: str = 'datatable-row-density'
    description: str = 'Large datatables should consider compact density'
    default_severity: Severity = Severity.INFO

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check datatables for density settings.

        Args:
            dashboard: The dashboard to check.
            options: Rule options. Supports:
                - min_columns (int): Minimum columns before suggesting compact. Default: 5.

        Returns:
            List of violations found.

        """
        from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel

        violations: list[Violation] = []
        min_cols = options.get('min_columns', 5)

        for idx, panel in enumerate(dashboard.panels):
            chart_type: str | None = None
            column_count = 0
            is_compact = False

            if isinstance(panel, LensPanel):
                config = panel.lens
                if config.type == 'datatable':
                    chart_type = 'lens.datatable'
                    if hasattr(config, 'columns') and config.columns is not None:
                        column_count = len(config.columns)
                    if hasattr(config, 'row_density') and config.row_density == 'compact':
                        is_compact = True
            elif isinstance(panel, ESQLPanel):
                config = panel.esql
                if config.type == 'datatable':
                    chart_type = 'esql.datatable'
                    if hasattr(config, 'columns') and config.columns is not None:
                        column_count = len(config.columns)
                    if hasattr(config, 'row_density') and config.row_density == 'compact':
                        is_compact = True

            if chart_type is not None and column_count >= min_cols and not is_compact:
                violations.append(
                    Violation(
                        rule_id=self.id,
                        message=f'Datatable has {column_count} columns; consider using compact row_density',
                        severity=self.default_severity,
                        dashboard_name=dashboard.name,
                        panel_title=panel.title if len(panel.title) > 0 else None,
                        location=f'panels[{idx}].{chart_type}',
                    )
                )

        return violations


# Register rules with the default registry
register_rule(MetricMultipleMetricsWidthRule())
register_rule(GaugeGoalWithoutMaxRule())
register_rule(PieChartDimensionCountRule())
register_rule(DatatableRowDensityRule())
