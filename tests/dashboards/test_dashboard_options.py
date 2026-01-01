"""Unit tests for dashboard options compilation."""

from inline_snapshot import snapshot

from dashboard_compiler.dashboard.compile import compile_dashboard_options
from dashboard_compiler.dashboard.config import DashboardSettings, DashboardSyncSettings


def test_compile_dashboard_options_all_defaults() -> None:
    """Test compile_dashboard_options with all default (None) values."""
    settings = DashboardSettings()
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {
            'useMargins': True,
            'syncColors': False,
            'syncCursor': True,
            'syncTooltips': False,
            'hidePanelTitles': False,
        }
    )


def test_compile_dashboard_options_all_custom_values() -> None:
    """Test compile_dashboard_options with all custom values set."""
    settings = DashboardSettings(
        margins=False,
        sync=DashboardSyncSettings(
            colors=True,
            cursor=False,
            tooltips=True,
        ),
        titles=False,
    )
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': False, 'syncColors': True, 'syncCursor': False, 'syncTooltips': True, 'hidePanelTitles': True}
    )
