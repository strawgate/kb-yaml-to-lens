"""Built-in lint rules for dashboard checking.

All rules are automatically registered when this module is imported.

This module provides:
- Base classes for creating rules (DashboardRule, PanelRule, ChartRule)
- Context classes for rule checks (PanelContext, ChartContext)
- Decorators for registering rules (@dashboard_rule, @panel_rule, @chart_rule)
- All built-in lint rules
"""

# Base classes and utilities (import first)
from dashboard_lint.rules._base import (
    ChartContext,
    ChartRule,
    DashboardRule,
    PanelContext,
    PanelRule,
    ViolationResult,
    normalize_result,
)
from dashboard_lint.rules._decorators import chart_rule, dashboard_rule, panel_rule

# Individual rules (import triggers registration via decorators)
from dashboard_lint.rules.dashboard_dataset_filter import DashboardDatasetFilterRule
from dashboard_lint.rules.datatable_row_density import DatatableRowDensityRule
from dashboard_lint.rules.dimension_missing_label import DimensionMissingLabelRule
from dashboard_lint.rules.esql_where_clause import ESQLWhereClauseRule
from dashboard_lint.rules.gauge_goal_without_max import GaugeGoalWithoutMaxRule
from dashboard_lint.rules.markdown_header_height import MarkdownHeaderHeightRule
from dashboard_lint.rules.metric_multiple_metrics_width import MetricMultipleMetricsWidthRule
from dashboard_lint.rules.metric_redundant_label import MetricRedundantLabelRule
from dashboard_lint.rules.panel_description_recommended import PanelDescriptionRecommendedRule
from dashboard_lint.rules.panel_height_for_content import PanelHeightForContentRule
from dashboard_lint.rules.panel_min_width import PanelMinWidthRule
from dashboard_lint.rules.pie_chart_dimension_count import PieChartDimensionCountRule

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
