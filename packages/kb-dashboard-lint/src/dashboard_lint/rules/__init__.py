"""Built-in lint rules for dashboard checking.

All rules are automatically registered when this module is imported.
"""

from dashboard_lint.rules.dashboard_rules import DashboardDatasetFilterRule
from dashboard_lint.rules.dimension_rules import DimensionMissingLabelRule
from dashboard_lint.rules.esql_rules import ESQLWhereClauseRule
from dashboard_lint.rules.markdown_rules import MarkdownHeaderHeightRule
from dashboard_lint.rules.metric_rules import MetricRedundantLabelRule

__all__ = [
    'DashboardDatasetFilterRule',
    'DimensionMissingLabelRule',
    'ESQLWhereClauseRule',
    'MarkdownHeaderHeightRule',
    'MetricRedundantLabelRule',
]
