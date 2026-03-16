"""Dashboard-level lint rules.

These rules check overall dashboard properties like filters,
settings, and cross-panel consistency.
"""

from dashboard_lint.rules.dashboard.collapsible_minimum_kibana_version import CollapsibleMinimumKibanaVersionRule
from dashboard_lint.rules.dashboard.dashboard_dataset_filter import DashboardDatasetFilterRule
from dashboard_lint.rules.dashboard.dashboard_missing_description import DashboardMissingDescriptionRule
from dashboard_lint.rules.dashboard.datatable_at_bottom import DatatableAtBottomRule
from dashboard_lint.rules.dashboard.esql_minimum_kibana_version import ESQLMinimumKibanaVersionRule
from dashboard_lint.rules.dashboard.markdown_at_top import MarkdownAtTopRule
from dashboard_lint.rules.dashboard.metric_excessive_count import MetricExcessiveCountRule

__all__ = [
    'CollapsibleMinimumKibanaVersionRule',
    'DashboardDatasetFilterRule',
    'DashboardMissingDescriptionRule',
    'DatatableAtBottomRule',
    'ESQLMinimumKibanaVersionRule',
    'MarkdownAtTopRule',
    'MetricExcessiveCountRule',
]
