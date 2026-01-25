"""Chart-level lint rules.

These rules check chart configurations (Lens and ESQL panels) for issues
like missing labels, insufficient dimensions, or configuration problems.
"""

from dashboard_lint.rules.chart.datatable_row_density import DatatableRowDensityRule
from dashboard_lint.rules.chart.dimension_missing_label import DimensionMissingLabelRule
from dashboard_lint.rules.chart.esql_dimension_missing_label import ESQLDimensionMissingLabelRule
from dashboard_lint.rules.chart.esql_dynamic_time_bucket import ESQLDynamicTimeBucketRule
from dashboard_lint.rules.chart.esql_field_escaping import ESQLFieldEscapingRule
from dashboard_lint.rules.chart.esql_metric_missing_label import ESQLMetricMissingLabelRule
from dashboard_lint.rules.chart.esql_sql_syntax import ESQLSqlSyntaxRule
from dashboard_lint.rules.chart.esql_where_clause import ESQLWhereClauseRule
from dashboard_lint.rules.chart.gauge_goal_without_max import GaugeGoalWithoutMaxRule
from dashboard_lint.rules.chart.metric_multiple_metrics_width import MetricMultipleMetricsWidthRule
from dashboard_lint.rules.chart.metric_redundant_label import MetricRedundantLabelRule
from dashboard_lint.rules.chart.panel_height_for_content import PanelHeightForContentRule
from dashboard_lint.rules.chart.pie_chart_dimension_count import PieChartDimensionCountRule

__all__ = [
    'DatatableRowDensityRule',
    'DimensionMissingLabelRule',
    'ESQLDimensionMissingLabelRule',
    'ESQLDynamicTimeBucketRule',
    'ESQLFieldEscapingRule',
    'ESQLMetricMissingLabelRule',
    'ESQLSqlSyntaxRule',
    'ESQLWhereClauseRule',
    'GaugeGoalWithoutMaxRule',
    'MetricMultipleMetricsWidthRule',
    'MetricRedundantLabelRule',
    'PanelHeightForContentRule',
    'PieChartDimensionCountRule',
]
