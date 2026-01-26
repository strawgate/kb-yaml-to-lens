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
    ESQLGroupBySyntaxRule,
    ESQLMissingLimitRule,
    ESQLMissingSortAfterBucketRule,
    ESQLWhereClauseRule,
    GaugeGoalWithoutMaxRule,
    MetricMultipleMetricsWidthRule,
    MetricRedundantLabelRule,
    PanelHeightForContentRule,
    PieChartDimensionCountRule,
    PieMissingLimitRule,
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
from dashboard_lint.rules.dashboard import (
    DashboardDatasetFilterRule,
    DashboardMissingDescriptionRule,
    DatatableAtBottomRule,
    MarkdownAtTopRule,
    MetricExcessiveCountRule,
)
from dashboard_lint.rules.panel import (
    MarkdownHeaderHeightRule,
    PanelDescriptionRecommendedRule,
    PanelMinWidthRule,
    PanelTitleRedundantPrefixRule,
)

__all__ = [
    'ChartContext',
    'ChartRule',
    'DashboardDatasetFilterRule',
    'DashboardMissingDescriptionRule',
    'DashboardRule',
    'DatatableAtBottomRule',
    'DatatableRowDensityRule',
    'DimensionMissingLabelRule',
    'ESQLGroupBySyntaxRule',
    'ESQLMissingLimitRule',
    'ESQLMissingSortAfterBucketRule',
    'ESQLWhereClauseRule',
    'GaugeGoalWithoutMaxRule',
    'MarkdownAtTopRule',
    'MarkdownHeaderHeightRule',
    'MetricExcessiveCountRule',
    'MetricMultipleMetricsWidthRule',
    'MetricRedundantLabelRule',
    'PanelContext',
    'PanelDescriptionRecommendedRule',
    'PanelHeightForContentRule',
    'PanelMinWidthRule',
    'PanelRule',
    'PanelTitleRedundantPrefixRule',
    'PieChartDimensionCountRule',
    'PieMissingLimitRule',
    'ViolationResult',
    'chart_rule',
    'dashboard_rule',
    'normalize_result',
    'panel_rule',
]
