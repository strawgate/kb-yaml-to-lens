"""Built-in lint rules for dashboard checking.

All rules are automatically registered when this module is imported.
"""

from dashboard_lint.rules.chart_rules import (
    DatatableRowDensityRule,
    GaugeGoalWithoutMaxRule,
    MetricMultipleMetricsWidthRule,
    PieChartDimensionCountRule,
)
from dashboard_lint.rules.dashboard_rules import DashboardDatasetFilterRule
from dashboard_lint.rules.dimension_rules import DimensionMissingLabelRule
from dashboard_lint.rules.esql_rules import ESQLWhereClauseRule
from dashboard_lint.rules.markdown_rules import MarkdownHeaderHeightRule
from dashboard_lint.rules.metric_rules import MetricRedundantLabelRule
from dashboard_lint.rules.panel_rules import (
    PanelDescriptionRecommendedRule,
    PanelHeightForContentRule,
    PanelMinWidthRule,
)

__all__ = [
    'DashboardDatasetFilterRule',
    'DatatableRowDensityRule',
    'DimensionMissingLabelRule',
    'ESQLWhereClauseRule',
    'GaugeGoalWithoutMaxRule',
    'MarkdownHeaderHeightRule',
    'MetricMultipleMetricsWidthRule',
    'MetricRedundantLabelRule',
    'PanelDescriptionRecommendedRule',
    'PanelHeightForContentRule',
    'PanelMinWidthRule',
    'PieChartDimensionCountRule',
]
