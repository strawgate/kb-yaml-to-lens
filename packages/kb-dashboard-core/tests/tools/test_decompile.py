"""Tests for dashboard decompiler tool."""

import io
import json

from ruamel.yaml import YAML

from kb_dashboard_core.tools.decompile import decompile_dashboard


def _dump_yaml(document: object) -> str:
    """Dump a YAML document to string for comment assertions."""
    yaml = YAML(typ='rt')
    stream = io.StringIO()
    yaml.dump(document, stream)
    return stream.getvalue()


def test_decompile_dashboard_stubs_panels_and_settings() -> None:
    """Decompile keeps panel type/layout/title and simple dashboard settings."""
    dashboard = {
        'id': 'decompile-test',
        'type': 'dashboard',
        'attributes': {
            'title': 'Decompile Demo',
            'description': 'Simple decompile test',
            'timeFrom': 'now-24h',
            'timeTo': 'now',
            'optionsJSON': json.dumps(
                {
                    'useMargins': True,
                    'syncColors': False,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': False,
                }
            ),
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'panel-1',
                        'title': 'Throughput',
                        'type': 'lens',
                        'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                        'embeddableConfig': {
                            'attributes': {'visualizationType': 'lnsMetric'},
                        },
                    },
                    {
                        'panelIndex': 'panel-2',
                        'type': 'markdown',
                        'gridData': {'x': 24, 'y': 0, 'w': 24, 'h': 6},
                        'embeddableConfig': {'markdown': '## Notes'},
                    },
                ]
            ),
        },
    }

    result = decompile_dashboard(dashboard)

    dashboards = result['dashboards']
    assert len(dashboards) == 1
    decompiled = dashboards[0]

    assert decompiled['name'] == 'Decompile Demo'
    assert decompiled['id'] == 'decompile-test'
    assert decompiled['description'] == 'Simple decompile test'
    assert decompiled['time_range']['from'] == 'now-24h'
    assert decompiled['time_range']['to'] == 'now'
    assert decompiled['settings']['margins'] is True
    assert decompiled['settings']['sync']['cursor'] is True
    assert decompiled['settings']['sync']['colors'] is False
    assert decompiled['settings']['titles'] is True

    panels = decompiled['panels']
    assert len(panels) == 2
    assert panels[0]['id'] == 'panel-1'
    assert panels[0]['title'] == 'Throughput'
    assert panels[0]['size']['w'] == 24
    assert panels[0]['position']['x'] == 0
    assert panels[0]['lens']['type'] == 'metric'
    assert panels[1]['id'] == 'panel-2'
    assert panels[1]['markdown']['content'] == '## Notes'


def test_decompile_dashboard_adds_todo_comment_with_original_json() -> None:
    """Decompile emits TODO comments with the original panel JSON."""
    dashboard = {
        'type': 'dashboard',
        'attributes': {
            'title': 'Comment Demo',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'panel-1',
                        'type': 'search',
                        'gridData': {'x': 0, 'y': 0, 'w': 48, 'h': 12},
                        'embeddableConfig': {'enhancements': {'drilldown': {}}},
                    },
                ]
            ),
        },
    }

    result = decompile_dashboard(dashboard)
    yaml_text = _dump_yaml(result)

    assert 'TODO(decompile): complete `search` panel config from original Kibana panel JSON.' in yaml_text
    assert 'Original panel JSON:' in yaml_text
    assert '"panelIndex": "panel-1"' in yaml_text

