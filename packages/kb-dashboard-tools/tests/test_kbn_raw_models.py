"""Validation tests for permissive view models against real Kibana dashboard JSON fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest

from kb_dashboard_tools.decompile.kbn_raw_models import KbnDashboard
from kb_dashboard_tools.decompile.kbn_raw_models.panels.charts.view import KbnLensPanel

_FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'elastic-integrations'

_FIXTURE_PATHS = [
    _FIXTURES_DIR / 'nginx-overview.json',
    _FIXTURES_DIR / 'nginx-access-errors.json',
    _FIXTURES_DIR / 'system-overview.json',
]


def _load_fixture(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# KbnDashboard.model_validate parses all fixtures without errors
# ---------------------------------------------------------------------------


@pytest.mark.parametrize('fixture_path', _FIXTURE_PATHS, ids=lambda p: p.stem)
def test_kbn_raw_dashboard_validates_fixture(fixture_path: Path) -> None:
    """KbnDashboard.model_validate must succeed on real Kibana JSON."""
    raw = _load_fixture(fixture_path)
    dashboard = KbnDashboard.model_validate(raw)
    assert dashboard.attributes is not None
    assert dashboard.attributes.title is not None
    assert len(dashboard.attributes.title) > 0


# ---------------------------------------------------------------------------
# Title and panel count assertions
# ---------------------------------------------------------------------------


def test_nginx_overview_title_and_panel_count() -> None:
    """nginx-overview: correct title and 8 panels."""
    raw = _load_fixture(_FIXTURES_DIR / 'nginx-overview.json')
    dashboard = KbnDashboard.model_validate(raw)
    assert dashboard.attributes is not None
    assert dashboard.attributes.title == '[Metrics Nginx] Overview'
    assert dashboard.attributes.panelsJSON is not None
    assert len(dashboard.attributes.panelsJSON) == 8


def test_system_overview_title_and_panel_count() -> None:
    """system-overview: correct title and 10 panels."""
    raw = _load_fixture(_FIXTURES_DIR / 'system-overview.json')
    dashboard = KbnDashboard.model_validate(raw)
    assert dashboard.attributes is not None
    assert dashboard.attributes.title == '[Metrics System] Overview'
    assert dashboard.attributes.panelsJSON is not None
    assert len(dashboard.attributes.panelsJSON) == 10


def test_nginx_access_errors_title_and_panel_count() -> None:
    """nginx-access-errors: correct title and 8 panels."""
    raw = _load_fixture(_FIXTURES_DIR / 'nginx-access-errors.json')
    dashboard = KbnDashboard.model_validate(raw)
    assert dashboard.attributes is not None
    assert dashboard.attributes.title == '[Logs Nginx] Overview'
    assert dashboard.attributes.panelsJSON is not None
    assert len(dashboard.attributes.panelsJSON) == 8


# ---------------------------------------------------------------------------
# Visualization type access via KbnLensPanel
# ---------------------------------------------------------------------------


def _get_viz_types(fixture_path: Path) -> list[str]:
    """Return visualization types from all Lens panels in a fixture."""
    dashboard = KbnDashboard.model_validate(_load_fixture(fixture_path))
    raw_panels = dashboard.attributes.panelsJSON if dashboard.attributes and dashboard.attributes.panelsJSON else []
    viz_types: list[str] = []
    for rp in raw_panels:
        if isinstance(rp, dict) and rp.get('type') == 'lens':
            lp = KbnLensPanel.model_validate(rp)
            ec = lp.embeddableConfig
            if ec is not None and ec.attributes is not None:
                vt = ec.attributes.visualizationType
                if vt is not None:
                    viz_types.append(str(vt))
    return viz_types


def test_nginx_overview_viz_types() -> None:
    """nginx-overview: all panels are lnsXY."""
    viz_types = _get_viz_types(_FIXTURES_DIR / 'nginx-overview.json')
    assert len(viz_types) == 8
    assert all(vt == 'lnsXY' for vt in viz_types)


def test_system_overview_viz_types() -> None:
    """system-overview: mix of metric, datatable, and heatmap panels."""
    viz_types = _get_viz_types(_FIXTURES_DIR / 'system-overview.json')
    assert 'lnsMetric' in viz_types
    assert 'lnsDatatable' in viz_types
    assert 'lnsHeatmap' in viz_types


def test_nginx_access_errors_viz_types() -> None:
    """nginx-access-errors: mix of XY and pie panels."""
    viz_types = _get_viz_types(_FIXTURES_DIR / 'nginx-access-errors.json')
    assert 'lnsXY' in viz_types
    assert 'lnsPie' in viz_types


# ---------------------------------------------------------------------------
# Datasource layer and column access
# ---------------------------------------------------------------------------


def test_lens_panel_datasource_layers_accessible() -> None:
    """KbnLensPanel: datasource layer IDs and column order are accessible."""
    dashboard = KbnDashboard.model_validate(_load_fixture(_FIXTURES_DIR / 'nginx-overview.json'))
    assert dashboard.attributes is not None
    assert dashboard.attributes.panelsJSON is not None
    first_panel = dashboard.attributes.panelsJSON[0]
    assert isinstance(first_panel, dict)
    lp = KbnLensPanel.model_validate(first_panel)

    assert lp.embeddableConfig is not None
    assert lp.embeddableConfig.attributes is not None
    state = lp.embeddableConfig.attributes.state
    assert state is not None
    assert state.datasourceStates is not None
    assert state.datasourceStates.formBased is not None
    assert state.datasourceStates.formBased.layers is not None

    layers = state.datasourceStates.formBased.layers.root
    assert len(layers) > 0

    # Each layer has columnOrder and columns accessible
    for layer in layers.values():
        assert layer.columnOrder is not None
        assert layer.columns is not None
        assert isinstance(layer.columns, dict)


# ---------------------------------------------------------------------------
# Control group parsing
# ---------------------------------------------------------------------------


def test_nginx_overview_control_group_parsed() -> None:
    """nginx-overview: controlGroupInput (with stringified panelsJSON) parses correctly."""
    raw = _load_fixture(_FIXTURES_DIR / 'nginx-overview.json')
    dashboard = KbnDashboard.model_validate(raw)
    assert dashboard.attributes is not None
    ctrl = dashboard.attributes.controlGroupInput
    assert ctrl is not None
    assert ctrl.chainingSystem is not None
    # panelsJSON is parsed from stringified JSON into a dict
    assert ctrl.panelsJSON is not None


# ---------------------------------------------------------------------------
# Options JSON parsing
# ---------------------------------------------------------------------------


def test_options_json_parsed_as_object() -> None:
    """OptionsJSON (may arrive as object or string) is parsed into KbnDashboardOptions."""
    raw = _load_fixture(_FIXTURES_DIR / 'nginx-overview.json')
    dashboard = KbnDashboard.model_validate(raw)
    assert dashboard.attributes is not None
    opts = dashboard.attributes.optionsJSON
    assert opts is not None
    assert opts.useMargins is True
    assert opts.syncColors is True
