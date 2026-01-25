"""Core components for dashboard lint rules.

This module provides:
- Base classes for creating rules (DashboardRule, PanelRule, ChartRule)
- Context classes for rule checks (PanelContext, ChartContext)
- Options base classes for type-safe rule options (EmptyOptions)
- Decorators for registering rules (@dashboard_rule, @panel_rule, @chart_rule)
- Utility functions for rule result normalization
"""

from dashboard_lint.rules.core.base import (
    ChartContext,
    ChartRule,
    DashboardRule,
    EmptyOptions,
    PanelContext,
    PanelRule,
    ViolationResult,
    normalize_result,
)
from dashboard_lint.rules.core.decorators import chart_rule, dashboard_rule, panel_rule

__all__ = [
    'ChartContext',
    'ChartRule',
    'DashboardRule',
    'EmptyOptions',
    'PanelContext',
    'PanelRule',
    'ViolationResult',
    'chart_rule',
    'dashboard_rule',
    'normalize_result',
    'panel_rule',
]
