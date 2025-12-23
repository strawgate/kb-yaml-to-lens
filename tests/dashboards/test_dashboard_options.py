"""Unit tests for dashboard options compilation."""

from dashboard_compiler.dashboard.compile import compile_dashboard_options
from dashboard_compiler.dashboard.config import DashboardSettings, DashboardSyncSettings
from dashboard_compiler.dashboard.view import KbnDashboardOptions


def test_compile_dashboard_options_all_defaults():
    """Test compile_dashboard_options with all default (None) values."""
    settings = DashboardSettings()
    result = compile_dashboard_options(settings)

    assert isinstance(result, KbnDashboardOptions)
    # When None, useMargins defaults to True
    assert result.useMargins is True
    # When None, syncColors defaults to False (inverted logic)
    assert result.syncColors is False
    # When None, syncCursor defaults to True
    assert result.syncCursor is True
    # When None, syncTooltips defaults to False (inverted logic)
    assert result.syncTooltips is False
    # When None, hidePanelTitles defaults to True
    assert result.hidePanelTitles is True


def test_compile_dashboard_options_margins_true():
    """Test compile_dashboard_options with margins explicitly set to True."""
    settings = DashboardSettings(margins=True)
    result = compile_dashboard_options(settings)

    assert result.useMargins is True


def test_compile_dashboard_options_margins_false():
    """Test compile_dashboard_options with margins explicitly set to False."""
    settings = DashboardSettings(margins=False)
    result = compile_dashboard_options(settings)

    assert result.useMargins is False


def test_compile_dashboard_options_sync_colors_true():
    """Test compile_dashboard_options with sync.colors explicitly set to True."""
    settings = DashboardSettings(sync=DashboardSyncSettings(colors=True))
    result = compile_dashboard_options(settings)

    assert result.syncColors is True


def test_compile_dashboard_options_sync_colors_false():
    """Test compile_dashboard_options with sync.colors explicitly set to False."""
    settings = DashboardSettings(sync=DashboardSyncSettings(colors=False))
    result = compile_dashboard_options(settings)

    assert result.syncColors is False


def test_compile_dashboard_options_sync_cursor_true():
    """Test compile_dashboard_options with sync.cursor explicitly set to True."""
    settings = DashboardSettings(sync=DashboardSyncSettings(cursor=True))
    result = compile_dashboard_options(settings)

    assert result.syncCursor is True


def test_compile_dashboard_options_sync_cursor_false():
    """Test compile_dashboard_options with sync.cursor explicitly set to False."""
    settings = DashboardSettings(sync=DashboardSyncSettings(cursor=False))
    result = compile_dashboard_options(settings)

    assert result.syncCursor is False


def test_compile_dashboard_options_sync_tooltips_true():
    """Test compile_dashboard_options with sync.tooltips explicitly set to True."""
    settings = DashboardSettings(sync=DashboardSyncSettings(tooltips=True))
    result = compile_dashboard_options(settings)

    assert result.syncTooltips is True


def test_compile_dashboard_options_sync_tooltips_false():
    """Test compile_dashboard_options with sync.tooltips explicitly set to False."""
    settings = DashboardSettings(sync=DashboardSyncSettings(tooltips=False))
    result = compile_dashboard_options(settings)

    assert result.syncTooltips is False


def test_compile_dashboard_options_titles_true():
    """Test compile_dashboard_options with titles explicitly set to True."""
    settings = DashboardSettings(titles=True)
    result = compile_dashboard_options(settings)

    assert result.hidePanelTitles is True


def test_compile_dashboard_options_titles_false():
    """Test compile_dashboard_options with titles explicitly set to False."""
    settings = DashboardSettings(titles=False)
    result = compile_dashboard_options(settings)

    assert result.hidePanelTitles is False


def test_compile_dashboard_options_all_custom_values():
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

    assert result.useMargins is False
    assert result.syncColors is True
    assert result.syncCursor is False
    assert result.syncTooltips is True
    assert result.hidePanelTitles is False


def test_compile_dashboard_options_partial_sync_settings():
    """Test compile_dashboard_options with only some sync settings defined."""
    settings = DashboardSettings(sync=DashboardSyncSettings(colors=True))
    result = compile_dashboard_options(settings)

    # colors is explicitly set to True
    assert result.syncColors is True
    # cursor is None, defaults to True
    assert result.syncCursor is True
    # tooltips is None, defaults to False
    assert result.syncTooltips is False
