"""End-to-end tests for dashboard compilation to Kibana JSON format.

Fixture Examples:
    https://github.com/strawgate/kb-yaml-to-lens-fixtures
    Contains complete Kibana dashboard JSON structures including panel configurations.
    Useful for understanding expected output format when debugging test failures.
"""

from typing import TYPE_CHECKING, Any

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import render
from tests.conftest import de_json_kbn_dashboard

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.view import KbnDashboard


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


def _replace_nested_ids(result: dict[str, Any]) -> None:
    """Replace nested reference names in panel embeddable config."""
    if 'attributes' in result and 'panelsJSON' in result['attributes']:
        panels = result['attributes']['panelsJSON']
        if isinstance(panels, list):
            for panel in panels:
                if 'embeddableConfig' in panel and 'attributes' in panel['embeddableConfig']:
                    attrs = panel['embeddableConfig']['attributes']
                    _replace_nested_references(attrs)


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


async def test_dashboard_with_one_pie_chart() -> None:
    """Test e2e dashboard compilation with pie chart - verifies reference management from nested panel to top-level."""
    db_input_dict = {
        'dashboards': [
            {
                'name': 'Pie Chart Only on Aerospike Namespace',
                'panels': [
                    {
                        'title': 'Pie Chart of Aerospike Namespace',
                        'id': 'c7a35c4f-e82d-4f16-b1a6-12229363244e',
                        'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                        'lens': {
                            'type': 'pie',
                            'id': '21cb2847-7b10-404e-9672-4ee2f2beca6e',
                            'data_view': 'metrics-*',
                            'color': {'palette': 'default'},
                            'dimensions': [
                                {
                                    'field': 'aerospike.namespace',
                                    'type': 'values',
                                    'size': 5,
                                    'id': '439aa452-8525-4644-8d5b-42d66f8b41fd',
                                }
                            ],
                            'metrics': [
                                {
                                    'aggregation': 'count',
                                    'id': 'fadbe80d-a574-4ab6-80c0-3bfe4c4e6d33',
                                }
                            ],
                        },
                    }
                ],
            }
        ]
    }
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

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
                                                'layerId': IsUUID,
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
    """Test e2e dashboard compilation with dashboard-level query - verifies query ends up in kibanaSavedObjectMeta.searchSourceJSON."""
    db_input_dict = {
        'dashboards': [
            {
                'name': 'One Query Dashboard',
                'description': 'A dashboard with a single query',
                'query': {'kql': 'myquery: myvalue'},
            }
        ]
    }
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

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


async def test_dashboard_with_one_filter() -> None:
    """Test e2e dashboard compilation with dashboard-level filter - verifies filter ends up in kibanaSavedObjectMeta.searchSourceJSON."""
    db_input_dict = {
        'dashboards': [
            {
                'name': 'One Filter Dashboard',
                'description': 'A dashboard with a single filter for namespace',
                'filters': [{'field': 'aerospike.namespace', 'equals': 'test'}],
            }
        ]
    }
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

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


async def test_dashboard_with_custom_options() -> None:
    """Test dashboard with custom options."""
    db_input_dict = {
        'dashboards': [
            {
                'name': 'Dashboard Options Test',
                'description': 'A dashboard to test all dashboard options',
                'settings': {
                    'margins': False,
                    'sync': {
                        'colors': True,
                        'cursor': False,
                        'tooltips': True,
                    },
                    'titles': False,
                },
                'panels': [
                    {
                        'title': 'Test Panel',
                        'grid': {'x': 0, 'y': 0, 'w': 12, 'h': 10},
                        'markdown': {
                            'content': '# Testing dashboard options\n',
                        },
                    }
                ],
            }
        ]
    }
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'Dashboard Options Test',
                'description': 'A dashboard to test all dashboard options',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 12, 'h': 10, 'i': '1edb8caf-94ce-4f06-1c09-a9439973884c'},
                        'type': 'visualization',
                        'embeddableConfig': {
                            'enhancements': {'dynamicActions': {'events': []}},
                            'savedVis': {
                                'type': 'markdown',
                                'id': '',
                                'title': 'Test Panel',
                                'description': '',
                                'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': '# Testing dashboard options\n'},
                                'uiState': {},
                                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
                            },
                        },
                    }
                ],
                'optionsJSON': {
                    'useMargins': False,
                    'syncColors': True,
                    'syncCursor': False,
                    'syncTooltips': True,
                    'hidePanelTitles': True,
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


async def test_dashboard_with_default_options() -> None:
    """Test dashboard with default options."""
    db_input_dict = {
        'dashboards': [
            {
                'name': 'Dashboard Options Defaults Test',
                'description': 'A dashboard to test default dashboard options behavior',
                'panels': [
                    {
                        'title': 'Test Panel',
                        'grid': {'x': 0, 'y': 0, 'w': 12, 'h': 10},
                        'markdown': {
                            'content': '# Testing default dashboard options\n',
                        },
                    }
                ],
            }
        ]
    }
    dashboard_data = db_input_dict['dashboards'][0]
    dashboard = Dashboard(**dashboard_data)

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)
    kbn_dashboard_compiled = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)
    kbn_dashboard_compiled = _replace_dynamic_ids(kbn_dashboard_compiled)

    assert kbn_dashboard_compiled == snapshot(
        {
            'attributes': {
                'title': 'Dashboard Options Defaults Test',
                'description': 'A dashboard to test default dashboard options behavior',
                'panelsJSON': [
                    {
                        'panelIndex': 'panel_0',
                        'gridData': {'x': 0, 'y': 0, 'w': 12, 'h': 10, 'i': '1edb8caf-94ce-4f06-1c09-a9439973884c'},
                        'type': 'visualization',
                        'embeddableConfig': {
                            'enhancements': {'dynamicActions': {'events': []}},
                            'savedVis': {
                                'type': 'markdown',
                                'id': '',
                                'title': 'Test Panel',
                                'description': '',
                                'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': '# Testing default dashboard options\n'},
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
