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
    with (scenario_basedir / f'{scenario_name}.json').open() as file:
        return json.load(file)


def get_db_yaml(scenario_name: str) -> dict:
    """Load a YAML scenario file from the scenarios directory."""
    with (scenario_basedir / f'{scenario_name}.yaml').open() as file:
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
    db_input_dict = get_db_yaml('case_markdown_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'Case Markdown Dashboard',
                'description': 'A dashboard for viewing case markdown',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 12, 'h': 10, 'i': '5405ecf0-1dbf-8342-b0e4-86b6464e5c0c'},
                        'type': 'visualization',
                        'embeddableConfig': {
                            'enhancements': {'dynamicActions': {'events': []}},
                            'savedVis': {
                                'type': 'markdown',
                                'id': '',
                                'title': 'Markdown Panel',
                                'description': 'Cool description',
                                'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': '# This is a basic markdown test'},
                                'uiState': {},
                                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
                            },
                        },
                    }
                ],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {'searchSourceJSON': {'filter': [], 'query': {'query': '', 'language': 'kuery'}}},
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )


async def test_dashboard_with_one_pie_chart() -> None:
    """Test dashboard with one pie chart."""
    db_input_dict = get_db_yaml('case_pie_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'Pie Chart Only on Aerospike Namespace',
                'description': '',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'c7a35c4f-e82d-4f16-b1a6-12229363244e'},
                        'type': 'lens',
                        'embeddableConfig': {
                            'enhancements': {'dynamicActions': {'events': []}},
                            'attributes': {
                                'title': 'Pie Chart of Aerospike Namespace',
                                'visualizationType': 'lnsPie',
                                'type': 'lens',
                                'references': [{'type': 'index-pattern', 'id': 'metrics-*', 'name': 'nested_ref_0'}],
                                'state': {
                                    'visualization': {
                                        'layers': [
                                            {
                                                'layerId': 'DYNAMIC_LAYER_ID',
                                                'layerType': 'data',
                                                'colorMapping': {
                                                    'assignments': [],
                                                    'specialAssignments': [
                                                        {'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}
                                                    ],
                                                    'paletteId': 'default',
                                                    'colorMode': {'type': 'categorical'},
                                                },
                                                'primaryGroups': ['439aa452-8525-4644-8d5b-42d66f8b41fd'],
                                                'metrics': ['fadbe80d-a574-4ab6-80c0-3bfe4c4e6d33'],
                                                'numberDisplay': 'percent',
                                                'categoryDisplay': 'default',
                                                'legendDisplay': 'default',
                                                'nestedLegend': False,
                                            }
                                        ],
                                        'shape': 'pie',
                                    },
                                    'query': {'query': '', 'language': 'kuery'},
                                    'filters': [],
                                    'datasourceStates': {
                                        'formBased': {
                                            'layers': {
                                                '21cb2847-7b10-404e-9672-4ee2f2beca6e': {
                                                    'columns': {
                                                        '439aa452-8525-4644-8d5b-42d66f8b41fd': {
                                                            'label': 'Top 5 values of aerospike.namespace',
                                                            'dataType': 'string',
                                                            'operationType': 'terms',
                                                            'isBucketed': True,
                                                            'scale': 'ordinal',
                                                            'params': {
                                                                'size': 5,
                                                                'orderBy': {
                                                                    'type': 'column',
                                                                    'columnId': 'fadbe80d-a574-4ab6-80c0-3bfe4c4e6d33',
                                                                },
                                                                'orderDirection': 'desc',
                                                                'otherBucket': True,
                                                                'missingBucket': False,
                                                                'parentFormat': {'id': 'terms'},
                                                                'include': [],
                                                                'exclude': [],
                                                                'includeIsRegex': False,
                                                                'excludeIsRegex': False,
                                                            },
                                                            'sourceField': 'aerospike.namespace',
                                                        },
                                                        'fadbe80d-a574-4ab6-80c0-3bfe4c4e6d33': {
                                                            'label': 'Count of records',
                                                            'dataType': 'number',
                                                            'operationType': 'count',
                                                            'isBucketed': False,
                                                            'scale': 'ratio',
                                                            'sourceField': '___records___',
                                                            'params': {'emptyAsNull': True},
                                                        },
                                                    },
                                                    'columnOrder': [
                                                        '439aa452-8525-4644-8d5b-42d66f8b41fd',
                                                        'fadbe80d-a574-4ab6-80c0-3bfe4c4e6d33',
                                                    ],
                                                    'incompleteColumns': {},
                                                    'sampling': 1,
                                                }
                                            }
                                        },
                                        'indexpattern': {'layers': {}},
                                        'textBased': {'layers': {}},
                                    },
                                    'internalReferences': [],
                                    'adHocDataViews': {},
                                },
                            },
                            'syncTooltips': False,
                            'syncColors': False,
                            'syncCursor': True,
                            'filters': [],
                            'query': {'query': '', 'language': 'kuery'},
                        },
                    }
                ],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {'searchSourceJSON': {'filter': [], 'query': {'query': '', 'language': 'kuery'}}},
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [{'type': 'index-pattern', 'id': 'metrics-*', 'name': 'ref_0'}],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )


async def test_dashboard_with_one_query() -> None:
    """Test dashboard with one query."""
    db_input_dict = get_db_yaml('case_query_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'One Query Dashboard',
                'description': 'A dashboard with a single query',
                'panelsJSON': [],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {'searchSourceJSON': {'filter': [], 'query': {'query': 'myquery: myvalue', 'language': 'kuery'}}},
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )


async def test_dashboard_with_one_link() -> None:
    """Test dashboard with one link."""
    db_input_dict = get_db_yaml('case_link_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'one-link',
                'description': 'A dashboard with a single link to a specific URL',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 48, 'h': 2, 'i': 'e19a731d-0163-490a-a691-0bd1b1264d0b'},
                        'type': 'links',
                        'embeddableConfig': {
                            'enhancements': {},
                            'attributes': {
                                'layout': 'horizontal',
                                'links': [
                                    {
                                        'id': '9f2896f6-9ca0-4f63-9960-631d5af3840c',
                                        'order': 0,
                                        'type': 'dashboardLink',
                                        'destinationRefName': 'link_9f2896f6-9ca0-4f63-9960-631d5af3840c_dashboard',
                                    }
                                ],
                            },
                        },
                    }
                ],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {'searchSourceJSON': {'filter': [], 'query': {'query': '', 'language': 'kuery'}}},
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [{'type': 'dashboard', 'id': 'e52208aa-f836-45a8-b960-8e72a139acf7', 'name': 'ref_0'}],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )


async def test_dashboard_with_one_filter() -> None:
    """Test dashboard with one filter."""
    db_input_dict = get_db_yaml('case_filter_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'One Filter Dashboard',
                'description': 'A dashboard with a single filter for namespace',
                'panelsJSON': [],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': {
                        'filter': [
                            {
                                '$state': {'store': 'appState'},
                                'meta': {
                                    'disabled': False,
                                    'negate': False,
                                    'alias': None,
                                    'type': 'phrase',
                                    'key': 'aerospike.namespace',
                                    'field': 'aerospike.namespace',
                                    'params': {'query': 'test'},
                                },
                                'query': {'match_phrase': {'aerospike.namespace': 'test'}},
                            }
                        ],
                        'query': {'query': '', 'language': 'kuery'},
                    }
                },
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )


async def test_dashboard_with_one_yaml_ref() -> None:
    """Test dashboard with one YAML ref."""
    db_input_dict = get_db_yaml('case_yaml_ref_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'Pie Chart Only on Aerospike Namespace with yaml ref',
                'description': '',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'de393fc9-0eb7-d07e-257b-091e1a19995c'},
                        'type': 'lens',
                        'embeddableConfig': {
                            'enhancements': {'dynamicActions': {'events': []}},
                            'attributes': {
                                'title': 'Pie Chart of Aerospike Namespace',
                                'visualizationType': 'lnsPie',
                                'type': 'lens',
                                'references': [{'type': 'index-pattern', 'id': 'metrics-*', 'name': 'nested_ref_0'}],
                                'state': {
                                    'visualization': {
                                        'layers': [
                                            {
                                                'layerId': 'DYNAMIC_LAYER_ID',
                                                'layerType': 'data',
                                                'colorMapping': {
                                                    'assignments': [],
                                                    'specialAssignments': [
                                                        {'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}
                                                    ],
                                                    'paletteId': 'default',
                                                    'colorMode': {'type': 'categorical'},
                                                },
                                                'primaryGroups': ['5260d8f2-7d7b-67f5-6c8c-e7e126beaba9'],
                                                'metrics': ['832d8d25-9f56-ce76-c599-dcd60beeb50e'],
                                                'numberDisplay': 'percent',
                                                'categoryDisplay': 'default',
                                                'legendDisplay': 'default',
                                                'nestedLegend': False,
                                            }
                                        ],
                                        'shape': 'pie',
                                    },
                                    'query': {'query': '', 'language': 'kuery'},
                                    'filters': [],
                                    'datasourceStates': {
                                        'formBased': {
                                            'layers': {
                                                '00000000-0000-0000-0000-000000000000': {
                                                    'columns': {
                                                        '5260d8f2-7d7b-67f5-6c8c-e7e126beaba9': {
                                                            'label': 'Top 5 values of aerospike.namespace',
                                                            'dataType': 'string',
                                                            'operationType': 'terms',
                                                            'isBucketed': True,
                                                            'scale': 'ordinal',
                                                            'params': {
                                                                'size': 5,
                                                                'orderBy': {
                                                                    'type': 'column',
                                                                    'columnId': '832d8d25-9f56-ce76-c599-dcd60beeb50e',
                                                                },
                                                                'orderDirection': 'desc',
                                                                'otherBucket': True,
                                                                'missingBucket': False,
                                                                'parentFormat': {'id': 'terms'},
                                                                'include': [],
                                                                'exclude': [],
                                                                'includeIsRegex': False,
                                                                'excludeIsRegex': False,
                                                            },
                                                            'sourceField': 'aerospike.namespace',
                                                        },
                                                        '832d8d25-9f56-ce76-c599-dcd60beeb50e': {
                                                            'label': 'Count of ___records___',
                                                            'dataType': 'number',
                                                            'operationType': 'count',
                                                            'isBucketed': False,
                                                            'scale': 'ratio',
                                                            'sourceField': '___records___',
                                                            'params': {'emptyAsNull': True},
                                                        },
                                                    },
                                                    'columnOrder': [
                                                        '5260d8f2-7d7b-67f5-6c8c-e7e126beaba9',
                                                        '832d8d25-9f56-ce76-c599-dcd60beeb50e',
                                                    ],
                                                    'incompleteColumns': {},
                                                    'sampling': 1,
                                                }
                                            }
                                        },
                                        'indexpattern': {'layers': {}},
                                        'textBased': {'layers': {}},
                                    },
                                    'internalReferences': [],
                                    'adHocDataViews': {},
                                },
                            },
                            'syncTooltips': False,
                            'syncColors': False,
                            'syncCursor': True,
                            'filters': [],
                            'query': {'query': '', 'language': 'kuery'},
                        },
                    }
                ],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {'searchSourceJSON': {'filter': [], 'query': {'query': '', 'language': 'kuery'}}},
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [{'type': 'index-pattern', 'id': 'metrics-*', 'name': 'ref_0'}],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )


async def test_dashboard_with_one_xy_line_chart() -> None:
    """Test dashboard with one XY line chart."""
    db_input_dict = get_db_yaml('case_xy_line_dashboard')
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

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'One Line Chart',
                'description': '',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'c7a35c4f-e82d-4f16-b1a6-12229363244e'},
                        'type': 'lens',
                        'embeddableConfig': {
                            'enhancements': {'dynamicActions': {'events': []}},
                            'attributes': {
                                'title': 'Empty XY Chart',
                                'visualizationType': 'lnsXY',
                                'type': 'lens',
                                'references': [{'type': 'index-pattern', 'id': 'metrics-*', 'name': 'nested_ref_0'}],
                                'state': {
                                    'visualization': {
                                        'layers': [
                                            {
                                                'layerId': 'DYNAMIC_LAYER_ID',
                                                'accessors': ['e50ccc00-a3a4-4e56-8246-4e71c1a35203'],
                                                'layerType': 'data',
                                                'seriesType': 'bar_stacked',
                                                'xAccessor': '27ebdeb3-213f-4587-8231-d7fb2a1c5dc3',
                                                'position': 'top',
                                                'showGridlines': False,
                                                'colorMapping': {
                                                    'assignments': [],
                                                    'specialAssignments': [
                                                        {'rule': {'type': 'other'}, 'color': {'type': 'loop'}, 'touched': False}
                                                    ],
                                                    'paletteId': 'eui_amsterdam_color_blind',
                                                    'colorMode': {'type': 'categorical'},
                                                },
                                            }
                                        ],
                                        'preferredSeriesType': 'bar_stacked',
                                        'legend': {'isVisible': True, 'position': 'right'},
                                        'valueLabels': 'hide',
                                    },
                                    'query': {'query': '', 'language': 'kuery'},
                                    'filters': [],
                                    'datasourceStates': {
                                        'formBased': {
                                            'layers': {
                                                '0f3a20be-b703-4935-b518-6baf2006e773': {
                                                    'columns': {
                                                        '27ebdeb3-213f-4587-8231-d7fb2a1c5dc3': {
                                                            'label': '@timestamp',
                                                            'dataType': 'date',
                                                            'operationType': 'date_histogram',
                                                            'isBucketed': True,
                                                            'scale': 'interval',
                                                            'params': {'interval': 'auto', 'includeEmptyRows': True, 'dropPartials': False},
                                                            'sourceField': '@timestamp',
                                                        },
                                                        'e50ccc00-a3a4-4e56-8246-4e71c1a35203': {
                                                            'label': 'Minimum of aerospike.namespace.query.count',
                                                            'dataType': 'number',
                                                            'operationType': 'min',
                                                            'isBucketed': False,
                                                            'scale': 'ratio',
                                                            'sourceField': 'aerospike.namespace.query.count',
                                                            'params': {'emptyAsNull': True},
                                                        },
                                                    },
                                                    'columnOrder': [
                                                        '27ebdeb3-213f-4587-8231-d7fb2a1c5dc3',
                                                        'e50ccc00-a3a4-4e56-8246-4e71c1a35203',
                                                    ],
                                                    'incompleteColumns': {},
                                                    'sampling': 1,
                                                }
                                            }
                                        },
                                        'indexpattern': {'layers': {}},
                                        'textBased': {'layers': {}},
                                    },
                                    'internalReferences': [],
                                    'adHocDataViews': {},
                                },
                            },
                            'syncTooltips': False,
                            'syncColors': False,
                            'syncCursor': True,
                            'filters': [],
                            'query': {'query': '', 'language': 'kuery'},
                        },
                    }
                ],
                'optionsJSON': {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                },
                'kibanaSavedObjectMeta': {'searchSourceJSON': {'filter': [], 'query': {'query': '', 'language': 'kuery'}}},
                'timeRestore': False,
                'version': 1,
                'controlGroupInput': {
                    'chainingSystem': 'HIERARCHICAL',
                    'controlStyle': 'oneLine',
                    'ignoreParentSettingsJSON': {
                        'ignoreFilters': False,
                        'ignoreQuery': False,
                        'ignoreTimerange': False,
                        'ignoreValidations': False,
                    },
                    'panelsJSON': {},
                    'showApplySelections': False,
                },
            },
            'coreMigrationVersion': '8.8.0',
            'created_at': 'DYNAMIC_TIMESTAMP',
            'created_by': 'DYNAMIC_USER',
            'id': 'DYNAMIC_ID',
            'managed': False,
            'references': [{'type': 'index-pattern', 'id': 'metrics-*', 'name': 'ref_0'}],
            'type': 'dashboard',
            'typeMigrationVersion': '10.2.0',
            'updated_at': 'DYNAMIC_TIMESTAMP',
            'updated_by': 'DYNAMIC_USER',
            'version': 'DYNAMIC_VERSION',
        }
    )
