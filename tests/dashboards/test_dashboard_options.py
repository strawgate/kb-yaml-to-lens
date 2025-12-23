"""Unit tests for dashboard options compilation."""

from inline_snapshot import snapshot

from dashboard_compiler.dashboard.compile import compile_dashboard_options
from dashboard_compiler.dashboard.config import DashboardSettings, DashboardSyncSettings


def test_compile_dashboard_options_all_defaults():
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


def test_compile_dashboard_options_margins_true():
    """Test compile_dashboard_options with margins explicitly set to True."""
    settings = DashboardSettings(margins=True)
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_margins_false():
    """Test compile_dashboard_options with margins explicitly set to False."""
    settings = DashboardSettings(margins=False)
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': False, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_sync_colors_true():
    """Test compile_dashboard_options with sync.colors explicitly set to True."""
    settings = DashboardSettings(sync=DashboardSyncSettings(colors=True))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': True, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_sync_colors_false():
    """Test compile_dashboard_options with sync.colors explicitly set to False."""
    settings = DashboardSettings(sync=DashboardSyncSettings(colors=False))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_sync_cursor_true():
    """Test compile_dashboard_options with sync.cursor explicitly set to True."""
    settings = DashboardSettings(sync=DashboardSyncSettings(cursor=True))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_sync_cursor_false():
    """Test compile_dashboard_options with sync.cursor explicitly set to False."""
    settings = DashboardSettings(sync=DashboardSyncSettings(cursor=False))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': False, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_sync_tooltips_true():
    """Test compile_dashboard_options with sync.tooltips explicitly set to True."""
    settings = DashboardSettings(sync=DashboardSyncSettings(tooltips=True))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': True, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_sync_tooltips_false():
    """Test compile_dashboard_options with sync.tooltips explicitly set to False."""
    settings = DashboardSettings(sync=DashboardSyncSettings(tooltips=False))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_titles_true():
    """Test compile_dashboard_options with titles explicitly set to True."""
    settings = DashboardSettings(titles=True)
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )


def test_compile_dashboard_options_titles_false():
    """Test compile_dashboard_options with titles explicitly set to False."""
    settings = DashboardSettings(titles=False)
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': False, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': True}
    )


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

    assert result.model_dump() == snapshot(
        {'useMargins': False, 'syncColors': True, 'syncCursor': False, 'syncTooltips': True, 'hidePanelTitles': True}
    )


def test_compile_dashboard_options_partial_sync_settings():
    """Test compile_dashboard_options with only some sync settings defined."""
    settings = DashboardSettings(sync=DashboardSyncSettings(colors=True))
    result = compile_dashboard_options(settings)

    assert result.model_dump() == snapshot(
        {'useMargins': True, 'syncColors': True, 'syncCursor': True, 'syncTooltips': False, 'hidePanelTitles': False}
    )
