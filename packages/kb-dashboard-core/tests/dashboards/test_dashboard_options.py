"""Unit tests for dashboard options compilation and Dashboard config methods."""

from inline_snapshot import snapshot

from kb_dashboard_core.controls.config import OptionsListControl
from kb_dashboard_core.dashboard.compile import compile_dashboard_attributes, compile_dashboard_options
from kb_dashboard_core.dashboard.config import Dashboard, DashboardSettings, DashboardSyncSettings, TimeRange
from kb_dashboard_core.filters.config import PhraseFilter
from kb_dashboard_core.panels.markdown.config import MarkdownPanel


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


def test_dashboard_without_time_range() -> None:
    """Test that dashboard without time_range has timeRestore=False and omits timeFrom/timeTo."""
    dashboard = Dashboard(name='Test Dashboard')
    _, attributes = compile_dashboard_attributes(dashboard)

    assert attributes.timeRestore is False
    assert attributes.timeFrom is None
    assert attributes.timeTo is None


def test_dashboard_with_time_range_from_and_to() -> None:
    """Test that dashboard with time_range sets timeRestore=True and includes timeFrom/timeTo."""
    dashboard = Dashboard(
        name='Test Dashboard',
        time_range=TimeRange(**{'from': 'now-30d/d', 'to': 'now/d'}),
    )
    _, attributes = compile_dashboard_attributes(dashboard)

    assert attributes.timeRestore is True
    assert attributes.timeFrom == 'now-30d/d'
    assert attributes.timeTo == 'now/d'


def test_dashboard_with_time_range_from_only() -> None:
    """Test that dashboard with time_range.from defaults to_time to 'now'."""
    dashboard = Dashboard(
        name='Test Dashboard',
        time_range=TimeRange(**{'from': 'now-1h'}),
    )
    _, attributes = compile_dashboard_attributes(dashboard)

    assert attributes.timeRestore is True
    assert attributes.timeFrom == 'now-1h'
    assert attributes.timeTo == 'now'


def test_time_range_serialization_omits_none_values() -> None:
    """Test that timeFrom and timeTo are omitted from serialization when None."""
    dashboard = Dashboard(name='Test Dashboard')
    _, attributes = compile_dashboard_attributes(dashboard)

    # Serialize to dict - timeFrom and timeTo should be omitted
    serialized = attributes.model_dump()
    assert 'timeFrom' not in serialized
    assert 'timeTo' not in serialized
    assert serialized['timeRestore'] is False


def test_time_range_serialization_includes_values() -> None:
    """Test that timeFrom and timeTo are included in serialization when set."""
    dashboard = Dashboard(
        name='Test Dashboard',
        time_range=TimeRange(**{'from': 'now-7d', 'to': 'now'}),
    )
    _, attributes = compile_dashboard_attributes(dashboard)

    # Serialize to dict - timeFrom and timeTo should be included
    serialized = attributes.model_dump()
    assert serialized['timeFrom'] == 'now-7d'
    assert serialized['timeTo'] == 'now'
    assert serialized['timeRestore'] is True
