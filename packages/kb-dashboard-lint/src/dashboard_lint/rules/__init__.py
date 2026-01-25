"""Built-in lint rules for dashboard checking.

All rules are automatically registered when this module is imported.

This module provides:
- Base classes for creating rules (DashboardRule, PanelRule, ChartRule)
- Context classes for rule checks (PanelContext, ChartContext)
- Decorators for registering rules (@dashboard_rule, @panel_rule, @chart_rule)
- All built-in lint rules organized by category
"""

from dashboard_lint.rules.chart import (
    DatatableRowDensityRule,
    DimensionMissingLabelRule,
    ESQLWhereClauseRule,
    GaugeGoalWithoutMaxRule,
    MetricMultipleMetricsWidthRule,
    MetricRedundantLabelRule,
    PanelHeightForContentRule,
    PieChartDimensionCountRule,
)
from dashboard_lint.rules.core import (
    ChartContext,
    ChartRule,
    DashboardRule,
    PanelContext,
    PanelRule,
    ViolationResult,
    chart_rule,
    dashboard_rule,
    normalize_result,
    panel_rule,
)
from dashboard_lint.rules.dashboard import DashboardDatasetFilterRule
from dashboard_lint.rules.panel import (
    MarkdownHeaderHeightRule,
    PanelDescriptionRecommendedRule,
    PanelMinWidthRule,
)

__all__ = [
    'ChartContext',
    'ChartRule',
    'DashboardDatasetFilterRule',
    'DashboardRule',
    'DatatableRowDensityRule',
    'DimensionMissingLabelRule',
    'ESQLWhereClauseRule',
    'GaugeGoalWithoutMaxRule',
    'MarkdownHeaderHeightRule',
    'MetricMultipleMetricsWidthRule',
    'MetricRedundantLabelRule',
    'PanelContext',
    'PanelDescriptionRecommendedRule',
    'PanelHeightForContentRule',
    'PanelMinWidthRule',
    'PanelRule',
    'PieChartDimensionCountRule',
    'ViolationResult',
    'chart_rule',
    'dashboard_rule',
    'normalize_result',
    'panel_rule',
]
