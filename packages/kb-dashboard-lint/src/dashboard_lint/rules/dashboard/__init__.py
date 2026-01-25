"""Dashboard-level lint rules.

These rules check overall dashboard properties like filters,
settings, and cross-panel consistency.
"""

from dashboard_lint.rules.dashboard.dashboard_dataset_filter import DashboardDatasetFilterRule

__all__ = [
    'DashboardDatasetFilterRule',
]
