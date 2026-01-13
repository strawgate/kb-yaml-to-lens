"""Unit tests for dashboard options compilation and Dashboard config methods."""

from inline_snapshot import snapshot

from dashboard_compiler.controls.config import OptionsListControl
from dashboard_compiler.dashboard.compile import compile_dashboard_options
from dashboard_compiler.dashboard.config import Dashboard, DashboardSettings, DashboardSyncSettings
from dashboard_compiler.filters.config import PhraseFilter
from dashboard_compiler.panels.markdown.config import MarkdownPanel


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


def test_dashboard_add_filter() -> None:
    """Test Dashboard.add_filter adds filters and returns self for chaining."""
    dashboard = Dashboard(name='Test Dashboard')
    filter1 = PhraseFilter(field='status', equals='active')
    filter2 = PhraseFilter(field='type', equals='error')

    result = dashboard.add_filter(filter1).add_filter(filter2)

    assert result is dashboard
    assert len(dashboard.filters) == 2
    assert dashboard.filters[0] == filter1
    assert dashboard.filters[1] == filter2


def test_dashboard_add_control() -> None:
    """Test Dashboard.add_control adds controls and returns self for chaining."""
    dashboard = Dashboard(name='Test Dashboard')
    control1 = OptionsListControl(data_view='test-*', field='status')
    control2 = OptionsListControl(data_view='test-*', field='type')

    result = dashboard.add_control(control1).add_control(control2)

    assert result is dashboard
    assert len(dashboard.controls) == 2
    assert dashboard.controls[0] == control1
    assert dashboard.controls[1] == control2


def test_dashboard_add_panel() -> None:
    """Test Dashboard.add_panel adds panels and returns self for chaining."""
    dashboard = Dashboard(name='Test Dashboard')
    panel1 = MarkdownPanel(size={'w': 12, 'h': 5}, position={'x': 0, 'y': 0}, markdown={'content': 'Panel 1'})
    panel2 = MarkdownPanel(size={'w': 12, 'h': 5}, position={'x': 12, 'y': 0}, markdown={'content': 'Panel 2'})

    result = dashboard.add_panel(panel1).add_panel(panel2)

    assert result is dashboard
    assert len(dashboard.panels) == 2
    assert dashboard.panels[0] == panel1
    assert dashboard.panels[1] == panel2
