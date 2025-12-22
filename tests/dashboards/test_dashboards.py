import json
import re
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml
from inline_snapshot import snapshot

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard.view import KbnDashboard
from dashboard_compiler.dashboard_compiler import render
from tests.conftest import de_json_kbn_dashboard

scenario_basedir = Path(__file__).parent / 'scenarios'


def get_kb_json(scenario_name: str) -> dict:
    """Load a JSON scenario file from the scenarios directory."""
    with Path.open(scenario_basedir / f'{scenario_name}.json') as file:
        return json.load(file)


def get_db_yaml(scenario_name: str) -> dict:
    """Load a YAML scenario file from the scenarios directory."""
    with Path.open(scenario_basedir / f'{scenario_name}.yaml') as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


def deterministic_id_generator():
    """Generate deterministic UUIDs for testing."""
    i = 0
    while True:
        yield f'00000000-0000-0000-0000-{i:012d}'
        i += 1


def _replace_panel_indexes(result: dict[str, Any]) -> None:
    """Replace panelIndex values with consistent placeholders."""
    if 'attributes' in result and 'panelsJSON' in result['attributes']:
        panels = result['attributes']['panelsJSON']
        if isinstance(panels, list):
            for i, panel in enumerate(panels):
                panel['panelIndex'] = f'panel_{i}'


def _replace_references(result: dict[str, Any]) -> None:
    """Replace reference names with consistent placeholders."""
    if 'references' in result and isinstance(result['references'], list):
        for i, ref in enumerate(result['references']):
            if 'name' in ref:
                ref['name'] = f'ref_{i}'


def _replace_nested_references(attrs: dict[str, Any]) -> None:
    """Replace nested reference names in attributes."""
    if 'references' in attrs and isinstance(attrs['references'], list):
        for i, ref in enumerate(attrs['references']):
            if 'name' in ref:
                ref['name'] = f'nested_ref_{i}'


def _replace_layer_ids(attrs: dict[str, Any]) -> None:
    """Replace layerIds in visualization layers."""
    if 'state' in attrs and 'visualization' in attrs['state']:
        viz = attrs['state']['visualization']
        if 'layers' in viz:
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            for layer in viz['layers']:
                if 'layerId' in layer and re.match(pattern, layer['layerId']):
                    layer['layerId'] = 'DYNAMIC_LAYER_ID'


def _replace_nested_ids(result: dict[str, Any]) -> None:
    """Replace nested reference names and layerIds in panel embeddable config."""
    if 'attributes' in result and 'panelsJSON' in result['attributes']:
        panels = result['attributes']['panelsJSON']
        if isinstance(panels, list):
            for panel in panels:
                if 'embeddableConfig' in panel and 'attributes' in panel['embeddableConfig']:
                    attrs = panel['embeddableConfig']['attributes']
                    _replace_nested_references(attrs)
                    _replace_layer_ids(attrs)


def _replace_dynamic_ids(result: dict[str, Any]) -> dict[str, Any]:
    """Replace dynamic IDs with placeholders for consistent snapshots."""
    # Replace top-level dynamic fields
    result['id'] = 'DYNAMIC_ID'
    result['created_at'] = 'DYNAMIC_TIMESTAMP'
    result['created_by'] = 'DYNAMIC_USER'
    result['updated_at'] = 'DYNAMIC_TIMESTAMP'
    result['updated_by'] = 'DYNAMIC_USER'
    result['version'] = 'DYNAMIC_VERSION'

    _replace_panel_indexes(result)
    _replace_references(result)
    _replace_nested_ids(result)

    return result


async def test_dashboard_with_one_markdown_panel() -> None:
    """Test dashboard with one markdown panel."""
    db_input_dict = {'dashboards': [get_db_yaml('case_markdown_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()


async def test_dashboard_with_one_pie_chart() -> None:
    """Test dashboard with one pie chart."""
    db_input_dict = {'dashboards': [get_db_yaml('case_pie_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()


async def test_dashboard_with_one_query() -> None:
    """Test dashboard with one query."""
    db_input_dict = {'dashboards': [get_db_yaml('case_query_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()


async def test_dashboard_with_one_link() -> None:
    """Test dashboard with one link."""
    db_input_dict = {'dashboards': [get_db_yaml('case_link_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()


async def test_dashboard_with_one_filter() -> None:
    """Test dashboard with one filter."""
    db_input_dict = {'dashboards': [get_db_yaml('case_filter_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()


async def test_dashboard_with_one_yaml_ref() -> None:
    """Test dashboard with one YAML ref."""
    db_input_dict = {'dashboards': [get_db_yaml('case_yaml_ref_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()


async def test_dashboard_with_one_xy_line_chart() -> None:
    """Test dashboard with one XY line chart."""
    db_input_dict = {'dashboards': [get_db_yaml('case_xy_line_dashboard')]}
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot()
