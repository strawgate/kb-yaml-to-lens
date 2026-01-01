"""End-to-end tests for ES|QL XY chart compilation from YAML."""

from pathlib import Path

import pytest

from dashboard_compiler.dashboard_compiler import load

esql_xy_dir = Path('tests/scenarios/charts/esql/xy')
esql_xy_files = sorted(esql_xy_dir.rglob('*.yaml'))


@pytest.mark.parametrize('yaml_path', esql_xy_files, ids=lambda p: str(p))
def test_esql_xy_chart_compiles(yaml_path: Path) -> None:
    """Test that ES|QL XY charts compile successfully from YAML.

    This is an end-to-end test that verifies the full compilation pipeline
    from YAML configuration to Kibana dashboard JSON for ES|QL XY charts
    (line, bar, and area).

    Args:
        yaml_path: Path to the YAML file containing the ES|QL XY chart configuration.

    """
    dashboards = load(str(yaml_path))
    assert len(dashboards) > 0, f'Should load at least one dashboard from {yaml_path}'

    # Verify that the dashboard has at least one panel
    dashboard = dashboards[0]
    assert len(dashboard.panels) > 0, f'Dashboard should have at least one panel in {yaml_path}'

    # Verify that the first panel is an ES|QL panel
    from dashboard_compiler.panels.charts.config import ESQLPanel

    panel = dashboard.panels[0]
    assert isinstance(panel, ESQLPanel), f'Panel should be an ESQLPanel in {yaml_path}'
    assert panel.esql is not None, f'Panel should have esql configuration in {yaml_path}'
