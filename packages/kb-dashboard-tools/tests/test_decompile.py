"""Tests for dashboard decompiler tool."""

import io
import json
from pathlib import Path
from typing import Any, cast

import pytest
from kb_dashboard_core.dashboard_compiler import load, render
from kb_dashboard_core.loader import DashboardConfig
from ruamel.yaml import YAML

from kb_dashboard_tools.decompile import decompile_dashboard
from kb_dashboard_tools.decompile.parse import get_int, parse_dashboard, parse_json_field


def _dump_yaml(document: object) -> str:
    """Dump a YAML document to string for comment assertions."""
    yaml = YAML(typ='rt')
    stream = io.StringIO()
    yaml.dump(document, stream)
    return stream.getvalue()


_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES_DIR = _PROJECT_ROOT / 'packages' / 'kb-dashboard-docs' / 'content' / 'examples'


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


def test_decompile_dashboard_extracts_additional_easy_panel_fields() -> None:
    """Decompile extracts additional trivially reversible panel fields."""
    dashboard = {
        'type': 'dashboard',
        'references': [
            {'name': 'search_0', 'type': 'search', 'id': 'saved-search-123'},
            {'name': 'link_0_dashboard', 'type': 'dashboard', 'id': 'destination-dashboard-456'},
        ],
        'attributes': {
            'title': 'Additional fields',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'search-panel',
                        'type': 'search',
                        'embeddableConfig': {'savedSearchRefName': 'search_0'},
                    },
                    {
                        'panelIndex': 'markdown-panel',
                        'type': 'markdown',
                        'embeddableConfig': {
                            'savedVis': {
                                'params': {
                                    'markdown': '# Hello',
                                    'fontSize': 16,
                                    'openLinksInNewTab': True,
                                }
                            }
                        },
                    },
                    {
                        'panelIndex': 'image-panel',
                        'type': 'image',
                        'embeddableConfig': {
                            'imageConfig': {
                                'src': {'type': 'url', 'url': 'https://example.com/image.png'},
                                'sizing': {'objectFit': 'cover'},
                                'altText': 'Diagram',
                                'backgroundColor': '#ffffff',
                            }
                        },
                    },
                    {
                        'panelIndex': 'links-panel',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'layout': 'vertical',
                                'links': [
                                    {
                                        'type': 'externalLink',
                                        'id': 'external-1',
                                        'label': 'Docs',
                                        'destination': 'https://example.com/docs',
                                        'options': {'openInNewTab': True, 'encodeUrl': False},
                                    },
                                    {
                                        'type': 'dashboardLink',
                                        'id': 'dashboard-1',
                                        'label': 'Operations',
                                        'destinationRefName': 'link_0_dashboard',
                                        'options': {
                                            'openInNewTab': False,
                                            'useCurrentDateRange': True,
                                            'useCurrentFilters': False,
                                        },
                                    },
                                ],
                            }
                        },
                    },
                ]
            ),
        },
    }

    result = decompile_dashboard(dashboard)
    panels = result['dashboards'][0]['panels']

    assert panels[0]['search']['saved_search_id'] == 'saved-search-123'
    assert panels[1]['markdown']['content'] == '# Hello'
    assert panels[1]['markdown']['font_size'] == 16
    assert panels[1]['markdown']['links_in_new_tab'] is True

    assert panels[2]['image']['from_url'] == 'https://example.com/image.png'
    assert panels[2]['image']['fit'] == 'cover'
    assert panels[2]['image']['description'] == 'Diagram'
    assert panels[2]['image']['background_color'] == '#ffffff'

    assert panels[3]['links']['layout'] == 'vertical'
    assert panels[3]['links']['items'][0]['url'] == 'https://example.com/docs'
    assert panels[3]['links']['items'][0]['new_tab'] is True
    assert panels[3]['links']['items'][0]['encode'] is False
    assert panels[3]['links']['items'][1]['dashboard'] == 'destination-dashboard-456'
    assert panels[3]['links']['items'][1]['with_time'] is True
    assert panels[3]['links']['items'][1]['with_filters'] is False


def test_decompile_dashboard_missing_attributes() -> None:
    """Decompile handles missing or non-dict attributes gracefully."""
    result = decompile_dashboard({'type': 'dashboard'})
    decompiled = result['dashboards'][0]
    assert decompiled['name'] == 'Untitled Dashboard'
    assert 'id' not in decompiled
    assert 'description' not in decompiled
    assert 'settings' not in decompiled
    assert 'time_range' not in decompiled
    assert len(decompiled['panels']) == 0


def test_decompile_dashboard_no_title_uses_default() -> None:
    """Decompile uses 'Untitled Dashboard' when title is missing."""
    result = decompile_dashboard({'attributes': {'description': 'no title'}})
    decompiled = result['dashboards'][0]
    assert decompiled['name'] == 'Untitled Dashboard'
    assert decompiled['description'] == 'no title'


def test_decompile_vega_panel() -> None:
    """Decompile creates a vega panel stub with empty spec."""
    dashboard = {
        'attributes': {
            'title': 'Vega test',
            'panelsJSON': json.dumps([{'panelIndex': 'v1', 'type': 'vega'}]),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'vega' in panel
    assert 'spec' in panel['vega']


def test_decompile_unsupported_panel_type() -> None:
    """Decompile wraps unsupported types in a TODO markdown panel."""
    dashboard = {
        'attributes': {
            'title': 'Unknown type',
            'panelsJSON': json.dumps([{'panelIndex': 'u1', 'type': 'custom_viz'}]),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'markdown' in panel
    assert 'unsupported panel type `custom_viz`' in panel['markdown']['content']


def test_decompile_esql_panel() -> None:
    """Decompile handles esql panel type like lens."""
    dashboard = {
        'attributes': {
            'title': 'ES|QL test',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'e1',
                        'type': 'esql',
                        'embeddableConfig': {
                            'attributes': {'visualizationType': 'bar'},
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'esql' in panel
    assert panel['esql']['type'] == 'bar'


def test_decompile_search_with_direct_saved_search_id() -> None:
    """Decompile extracts savedSearchId directly from panel."""
    dashboard = {
        'attributes': {
            'title': 'Direct search',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 's1',
                        'type': 'search',
                        'savedSearchId': 'direct-id-123',
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['search']['saved_search_id'] == 'direct-id-123'


def test_decompile_search_unresolved_ref_falls_back_to_todo() -> None:
    """Decompile uses TODO placeholder when search ref cannot be resolved."""
    dashboard = {
        'attributes': {
            'title': 'Unresolved search',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 's2',
                        'type': 'search',
                        'embeddableConfig': {'savedSearchRefName': 'missing_ref'},
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['search']['saved_search_id'] == 'TODO_saved_search_id'


def test_decompile_markdown_todo_when_no_content() -> None:
    """Decompile uses TODO placeholder when markdown content is absent."""
    dashboard = {
        'attributes': {
            'title': 'Empty markdown',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'm1',
                        'type': 'markdown',
                        'embeddableConfig': {},
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'TODO(decompile)' in panel['markdown']['content']


def test_decompile_image_no_config_uses_todo() -> None:
    """Decompile uses TODO placeholder when image has no imageConfig."""
    dashboard = {
        'attributes': {
            'title': 'Empty image',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'i1',
                        'type': 'image',
                        'embeddableConfig': {},
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['image']['from_url'] == 'TODO_image_url'


def test_decompile_links_no_links_returns_empty_items() -> None:
    """Decompile returns empty items when links panel has no links array."""
    dashboard = {
        'attributes': {
            'title': 'Empty links',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l1',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {'layout': 'horizontal'},
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['links']['layout'] == 'horizontal'
    assert len(panel['links']['items']) == 0


def test_decompile_links_unknown_type_skipped() -> None:
    """Decompile skips link items with unknown type."""
    dashboard = {
        'attributes': {
            'title': 'Unknown link type',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l2',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'links': [
                                    {'type': 'unknownLink', 'id': 'skip-me'},
                                ],
                            },
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert len(panel['links']['items']) == 0


def test_decompile_external_link_no_destination_skipped() -> None:
    """Decompile skips external links without destination."""
    dashboard = {
        'attributes': {
            'title': 'No dest link',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l3',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'links': [
                                    {'type': 'externalLink', 'id': 'no-dest'},
                                ],
                            },
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert len(panel['links']['items']) == 0


def test_decompile_dashboard_link_no_ref_skipped() -> None:
    """Decompile skips dashboard links without destinationRefName."""
    dashboard = {
        'attributes': {
            'title': 'No ref link',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l4',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'links': [
                                    {'type': 'dashboardLink', 'id': 'no-ref'},
                                ],
                            },
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert len(panel['links']['items']) == 0


def test_decompile_dashboard_link_unresolved_ref_uses_todo() -> None:
    """Decompile generates TODO for unresolved dashboard link references."""
    dashboard = {
        'attributes': {
            'title': 'Unresolved link',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l5',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'links': [
                                    {
                                        'type': 'dashboardLink',
                                        'destinationRefName': 'missing_ref',
                                        'options': {},
                                    },
                                ],
                            },
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'TODO_dashboard_id_for_missing_ref' in panel['links']['items'][0]['dashboard']


def test_decompile_panel_no_grid_data() -> None:
    """Decompile handles panels without gridData."""
    dashboard = {
        'attributes': {
            'title': 'No grid',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'ng1',
                        'type': 'lens',
                        'embeddableConfig': {'attributes': {}},
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'size' not in panel
    assert 'position' not in panel


def test_decompile_panel_title_from_embeddable_config() -> None:
    """Decompile extracts title from embeddableConfig when panel title is absent."""
    dashboard = {
        'attributes': {
            'title': 'Embedded title',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'et1',
                        'type': 'lens',
                        'embeddableConfig': {
                            'title': 'From Embedded',
                            'attributes': {},
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['title'] == 'From Embedded'


def test_decompile_panel_empty_title_when_no_title_anywhere() -> None:
    """Decompile uses empty string when no title is found at any level."""
    dashboard = {
        'attributes': {
            'title': 'No panel title',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'nt1',
                        'type': 'lens',
                        'embeddableConfig': {'attributes': {}},
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['title'] == ''


def test_decompile_settings_empty_options_returns_none() -> None:
    """Decompile returns no settings when optionsJSON has no recognized fields."""
    dashboard = {
        'attributes': {
            'title': 'Empty options',
            'optionsJSON': json.dumps({'unknownField': True}),
            'panelsJSON': json.dumps([]),
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    assert 'settings' not in decompiled


def test_decompile_non_dict_panels_skipped() -> None:
    """Decompile skips non-dict items in panelsJSON list."""
    dashboard = {
        'attributes': {
            'title': 'Non-dict panels',
            'panelsJSON': json.dumps(
                [
                    'not-a-dict',
                    42,
                    None,
                    {'panelIndex': 'valid', 'type': 'lens', 'embeddableConfig': {'attributes': {}}},
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panels = result['dashboards'][0]['panels']
    assert len(panels) == 1
    assert panels[0]['id'] == 'valid'


def test_decompile_non_dict_references_skipped() -> None:
    """Decompile skips non-dict items in references list."""
    dashboard = {
        'references': [
            'not-a-dict',
            {'name': 'ref1', 'id': 'id1'},
        ],
        'attributes': {
            'title': 'Non-dict refs',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 's1',
                        'type': 'search',
                        'embeddableConfig': {'savedSearchRefName': 'ref1'},
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['search']['saved_search_id'] == 'id1'


def test_decompile_links_with_non_dict_link_items_skipped() -> None:
    """Decompile skips non-dict items in links array."""
    dashboard = {
        'attributes': {
            'title': 'Non-dict links',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l6',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'links': [
                                    'not-a-dict',
                                    {
                                        'type': 'externalLink',
                                        'destination': 'https://example.com',
                                    },
                                ],
                            },
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert len(panel['links']['items']) == 1


def test_decompile_link_without_options() -> None:
    """Decompile handles link items where options is missing."""
    dashboard = {
        'attributes': {
            'title': 'No options link',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'l7',
                        'type': 'links',
                        'embeddableConfig': {
                            'attributes': {
                                'links': [
                                    {
                                        'type': 'externalLink',
                                        'destination': 'https://example.com',
                                    },
                                ],
                            },
                        },
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    items = result['dashboards'][0]['panels'][0]['links']['items']
    assert len(items) == 1
    assert items[0]['url'] == 'https://example.com'
    assert 'new_tab' not in items[0]


def test_decompile_time_range_partial() -> None:
    """Decompile handles time range with only from or only to."""
    # Only 'from'
    result = decompile_dashboard(
        {
            'attributes': {
                'title': 'Partial time',
                'timeFrom': 'now-1h',
                'panelsJSON': json.dumps([]),
            },
        }
    )
    tr = result['dashboards'][0]['time_range']
    assert tr['from'] == 'now-1h'
    assert 'to' not in tr


def test_decompile_no_embeddable_config_on_panel() -> None:
    """Decompile handles panels without embeddableConfig."""
    dashboard = {
        'attributes': {
            'title': 'No embed config',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'ne1',
                        'type': 'lens',
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert 'lens' in panel


def test_decompile_image_no_embeddable_config() -> None:
    """Decompile handles image panel without embeddableConfig."""
    dashboard = {
        'attributes': {
            'title': 'No embed image',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'ni1',
                        'type': 'image',
                    }
                ]
            ),
        },
    }
    result = decompile_dashboard(dashboard)
    panel = result['dashboards'][0]['panels'][0]
    assert panel['image']['from_url'] == 'TODO_image_url'


def test_decompile_panels_json_as_dict() -> None:
    """Decompile handles panelsJSON passed as a raw list (not JSON string)."""
    dashboard = {
        'attributes': {
            'title': 'Raw list',
            'panelsJSON': [
                {
                    'panelIndex': 'r1',
                    'type': 'lens',
                    'embeddableConfig': {'attributes': {}},
                }
            ],
        },
    }
    result = decompile_dashboard(dashboard)
    panels = result['dashboards'][0]['panels']
    assert len(panels) == 1


def _make_lens_panel(
    vis_type: str,
    *,
    state: dict[str, object] | None = None,
    references: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build a minimal Kibana lens panel dict for testing."""
    attributes: dict[str, object] = {'visualizationType': vis_type}
    if state is not None:
        attributes['state'] = state
    if references is not None:
        attributes['references'] = references
    return {
        'panelIndex': 'p1',
        'type': 'lens',
        'embeddableConfig': {'attributes': attributes},
    }


def _decompile_single_panel(panel: dict[str, object]) -> Any:
    """Decompile a dashboard with a single panel and return that panel dict."""
    dashboard: dict[str, object] = {
        'attributes': {
            'title': 'Test',
            'panelsJSON': json.dumps([panel]),
        },
    }
    result = decompile_dashboard(dashboard)
    return result['dashboards'][0]['panels'][0]


# --- XY chart type extraction ---


def test_decompile_lnsxy_defaults_to_line() -> None:
    """LnsXY without preferredSeriesType defaults to line."""
    panel = _make_lens_panel('lnsXY')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'line'


def test_decompile_lnsxy_line() -> None:
    """LnsXY with preferredSeriesType=line yields line."""
    panel = _make_lens_panel('lnsXY', state={'visualization': {'preferredSeriesType': 'line'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'line'


def test_decompile_lnsxy_bar() -> None:
    """LnsXY with preferredSeriesType=bar yields bar."""
    panel = _make_lens_panel('lnsXY', state={'visualization': {'preferredSeriesType': 'bar'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'bar'


def test_decompile_lnsxy_bar_stacked() -> None:
    """LnsXY with preferredSeriesType=bar_stacked yields bar."""
    panel = _make_lens_panel('lnsXY', state={'visualization': {'preferredSeriesType': 'bar_stacked'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'bar'
    assert result['lens']['mode'] == 'stacked'


def test_decompile_lnsxy_bar_percentage_stacked_sets_percentage_mode() -> None:
    """LnsXY with preferredSeriesType=bar_percentage_stacked preserves percentage mode."""
    panel = _make_lens_panel('lnsXY', state={'visualization': {'preferredSeriesType': 'bar_percentage_stacked'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'bar'
    assert result['lens']['mode'] == 'percentage'


def test_decompile_lnsxy_area() -> None:
    """LnsXY with preferredSeriesType=area yields area."""
    panel = _make_lens_panel('lnsXY', state={'visualization': {'preferredSeriesType': 'area'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'area'


# --- Metric chart extraction ---


def test_decompile_lnsmetric() -> None:
    """LnsMetric maps to metric type."""
    panel = _make_lens_panel('lnsMetric')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'metric'


# --- Pie chart extraction ---


def test_decompile_lnspie_default() -> None:
    """LnsPie without shape defaults to pie."""
    panel = _make_lens_panel('lnsPie')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'pie'


def test_decompile_lnspie_donut() -> None:
    """LnsPie with shape=donut maps to pie with donut appearance."""
    panel = _make_lens_panel('lnsPie', state={'visualization': {'shape': 'donut'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'pie'
    assert result['lens']['appearance']['donut'] == 'medium'


def test_decompile_lnspie_treemap() -> None:
    """LnsPie with shape=treemap yields treemap."""
    panel = _make_lens_panel('lnsPie', state={'visualization': {'shape': 'treemap'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'treemap'


# --- Data view extraction ---


def test_decompile_data_view_from_references() -> None:
    """Extract data_view from index-pattern references."""
    panel = _make_lens_panel(
        'lnsMetric',
        references=[
            {'type': 'index-pattern', 'id': 'metrics-*', 'name': 'indexpattern-datasource-layer-abc'},
        ],
    )
    result = _decompile_single_panel(panel)
    assert result['lens']['data_view'] == 'metrics-*'


def test_decompile_data_view_picks_first_index_pattern() -> None:
    """Extract data_view uses first index-pattern reference."""
    panel = _make_lens_panel(
        'lnsMetric',
        references=[
            {'type': 'tag', 'id': 'tag-1', 'name': 'some-tag'},
            {'type': 'index-pattern', 'id': 'logs-*', 'name': 'indexpattern-datasource-layer-xyz'},
        ],
    )
    result = _decompile_single_panel(panel)
    assert result['lens']['data_view'] == 'logs-*'


# --- Simple metric extraction ---


def test_decompile_count_metric() -> None:
    """Extract count metric from form-based columns."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'count',
                                    'isBucketed': False,
                                    'sourceField': 'Records',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    primary = result['lens']['primary']
    assert primary['aggregation'] == 'count'
    assert 'field' not in primary


def test_decompile_sum_metric() -> None:
    """Extract sum metric with field from form-based columns."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'sum',
                                    'isBucketed': False,
                                    'sourceField': 'bytes',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    primary = result['lens']['primary']
    assert primary['aggregation'] == 'sum'
    assert primary['field'] == 'bytes'


def test_decompile_average_metric() -> None:
    """Extract avg metric mapped to average."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'avg',
                                    'isBucketed': False,
                                    'sourceField': 'response.time',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    primary = result['lens']['primary']
    assert primary['aggregation'] == 'average'
    assert primary['field'] == 'response.time'


# --- Dimension and breakdown extraction ---


def test_decompile_date_histogram_dimension() -> None:
    """Extract date_histogram dimension from bucketed columns."""
    panel = _make_lens_panel(
        'lnsXY',
        state={
            'visualization': {'preferredSeriesType': 'line'},
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'date_histogram',
                                    'isBucketed': True,
                                    'sourceField': '@timestamp',
                                    'params': {'interval': 'auto'},
                                },
                                'col2': {
                                    'operationType': 'count',
                                    'isBucketed': False,
                                    'sourceField': 'Records',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'line'
    dim = result['lens']['dimension']
    assert dim['type'] == 'date_histogram'
    assert dim['field'] == '@timestamp'
    assert 'minimum_interval' not in dim  # auto is omitted


def test_decompile_terms_breakdown() -> None:
    """Extract terms breakdown from bucketed columns."""
    panel = _make_lens_panel(
        'lnsXY',
        state={
            'visualization': {'preferredSeriesType': 'bar'},
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'terms',
                                    'isBucketed': True,
                                    'sourceField': 'host.name',
                                    'params': {'size': 10},
                                },
                                'col2': {
                                    'operationType': 'count',
                                    'isBucketed': False,
                                    'sourceField': 'Records',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    bd = result['lens']['breakdown']
    assert bd['type'] == 'values'
    assert bd['field'] == 'host.name'
    assert bd['size'] == 10


# --- Formula panels are skipped ---


def test_decompile_formula_panel_has_todo() -> None:
    """Unsupported formula operations keep a TODO metric placeholder."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'formula',
                                    'isBucketed': False,
                                    'sourceField': 'Records',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    assert '_todo' not in result['lens']
    assert result['lens']['primary']['aggregation'] == 'sum'
    assert result['lens']['primary']['field'] == 'TODO_unsupported_metric_field'


# --- ES|QL query extraction ---


def test_decompile_esql_query() -> None:
    """Extract ES|QL query from textBased datasource."""
    panel = {
        'panelIndex': 'p1',
        'type': 'esql',
        'embeddableConfig': {
            'attributes': {
                'visualizationType': 'metric',
                'state': {
                    'datasourceStates': {
                        'textBased': {
                            'layers': {
                                'layer1': {
                                    'query': {'esql': 'FROM logs-* | STATS count=COUNT()'},
                                },
                            },
                        },
                    },
                },
            }
        },
    }
    result = _decompile_single_panel(panel)
    assert result['esql']['query'] == 'FROM logs-* | STATS count=COUNT()'


# --- Controls extraction ---


def test_decompile_controls() -> None:
    """Extract controls from controlGroupInput."""
    dashboard = {
        'attributes': {
            'title': 'Controls test',
            'panelsJSON': json.dumps([]),
            'controlGroupInput': {
                'panelsJSON': json.dumps(
                    {
                        'ctrl-1': {
                            'type': 'optionsListControl',
                            'order': 0,
                            'explicitInput': {
                                'fieldName': 'host.name',
                                'title': 'Host',
                                'dataViewId': 'metrics-*',
                            },
                        },
                        'ctrl-2': {
                            'type': 'rangeSliderControl',
                            'order': 1,
                            'explicitInput': {
                                'fieldName': 'severity_number',
                                'title': 'Severity',
                                'dataViewId': 'logs-*',
                            },
                        },
                    }
                ),
            },
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    controls = decompiled['controls']
    assert len(controls) == 2

    assert controls[0]['type'] == 'options'
    assert controls[0]['field'] == 'host.name'
    assert controls[0]['label'] == 'Host'
    assert controls[0]['data_view'] == 'metrics-*'

    assert controls[1]['type'] == 'range'
    assert controls[1]['field'] == 'severity_number'
    assert controls[1]['data_view'] == 'logs-*'


def test_parse_controls_view_model_uses_reference_data_view() -> None:
    """Parse phase injects resolved data view into control view-model validation."""
    dashboard = {
        'references': [
            {'name': 'controlGroup_ctrl-1:optionsListDataView', 'type': 'index-pattern', 'id': 'metrics-*'},
        ],
        'attributes': {
            'title': 'Controls from references',
            'panelsJSON': json.dumps([]),
            'controlGroupInput': {
                'panelsJSON': json.dumps(
                    {
                        'ctrl-1': {
                            'type': 'optionsListControl',
                            'order': 0,
                            'explicitInput': {
                                'fieldName': 'host.name',
                                'title': 'Host',
                            },
                        },
                    }
                ),
            },
        },
    }
    parsed = parse_dashboard(dashboard)
    assert parsed.controls
    assert parsed.controls[0].data_view_id == 'metrics-*'
    assert parsed.controls[0].view_control is not None


# --- Filters extraction ---


def test_decompile_filters_phrase() -> None:
    """Extract phrase filters from searchSourceJSON."""
    dashboard = {
        'attributes': {
            'title': 'Filters test',
            'panelsJSON': json.dumps([]),
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'filter': [
                            {
                                'meta': {
                                    'type': 'phrase',
                                    'key': 'status',
                                    'params': {'query': 'error'},
                                },
                            },
                        ],
                    }
                ),
            },
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    filters = decompiled['filters']
    assert len(filters) == 1
    assert filters[0]['field'] == 'status'
    assert filters[0]['equals'] == 'error'


def test_decompile_filters_phrase_preserves_scalar_type() -> None:
    """Phrase filters preserve scalar value types."""
    dashboard = {
        'attributes': {
            'title': 'Filters scalar phrase test',
            'panelsJSON': json.dumps([]),
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'filter': [
                            {
                                'meta': {
                                    'type': 'phrase',
                                    'key': 'response.status_code',
                                    'params': {'query': 200},
                                },
                            },
                        ],
                    }
                ),
            },
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    filters = decompiled['filters']
    assert len(filters) == 1
    assert filters[0]['field'] == 'response.status_code'
    assert filters[0]['equals'] == 200
    assert isinstance(filters[0]['equals'], int)


def test_decompile_filters_phrases_preserves_scalar_types() -> None:
    """Phrases filters preserve scalar value types."""
    dashboard = {
        'attributes': {
            'title': 'Filters scalar phrases test',
            'panelsJSON': json.dumps([]),
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'filter': [
                            {
                                'meta': {
                                    'type': 'phrases',
                                    'key': 'status',
                                    'params': ['error', 500, True],
                                },
                            },
                        ],
                    }
                ),
            },
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    filters = decompiled['filters']
    assert len(filters) == 1
    assert filters[0]['field'] == 'status'
    assert filters[0]['in'] == ['error', 500, True]
    assert isinstance(filters[0]['in'][1], int)
    assert isinstance(filters[0]['in'][2], bool)


def test_decompile_filters_range_preserves_scalar_types() -> None:
    """Range filters preserve scalar bound types."""
    dashboard = {
        'attributes': {
            'title': 'Filters scalar range test',
            'panelsJSON': json.dumps([]),
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'filter': [
                            {
                                'meta': {
                                    'type': 'range',
                                    'key': 'response.status_code',
                                },
                                'range': {
                                    'response.status_code': {
                                        'gte': 200,
                                        'lt': 500,
                                    },
                                },
                            },
                        ],
                    }
                ),
            },
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    filters = decompiled['filters']
    assert len(filters) == 1
    assert filters[0]['field'] == 'response.status_code'
    assert filters[0]['gte'] == 200
    assert filters[0]['lt'] == 500
    assert isinstance(filters[0]['gte'], int)
    assert isinstance(filters[0]['lt'], int)


def test_decompile_filters_exists() -> None:
    """Extract exists filters from searchSourceJSON."""
    dashboard = {
        'attributes': {
            'title': 'Exists filter test',
            'panelsJSON': json.dumps([]),
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'filter': [
                            {
                                'meta': {
                                    'type': 'exists',
                                    'key': 'host.name',
                                },
                            },
                        ],
                    }
                ),
            },
        },
    }
    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    filters = decompiled['filters']
    assert len(filters) == 1
    assert filters[0]['exists'] == 'host.name'


def test_decompile_no_controls_when_absent() -> None:
    """No controls key when controlGroupInput is absent."""
    result = decompile_dashboard({'attributes': {'title': 'No controls', 'panelsJSON': json.dumps([])}})
    decompiled = result['dashboards'][0]
    assert 'controls' not in decompiled


def test_decompile_no_filters_when_absent() -> None:
    """No filters key when searchSourceJSON has no filters."""
    result = decompile_dashboard({'attributes': {'title': 'No filters', 'panelsJSON': json.dumps([])}})
    decompiled = result['dashboards'][0]
    assert 'filters' not in decompiled


def test_decompile_gauge_type() -> None:
    """LnsGauge maps to gauge type."""
    panel = _make_lens_panel('lnsGauge')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'gauge'


def test_decompile_heatmap_type() -> None:
    """LnsHeatmap maps to heatmap type."""
    panel = _make_lens_panel('lnsHeatmap')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'heatmap'


def test_decompile_tagcloud_type() -> None:
    """LnsTagcloud maps to tagcloud type."""
    panel = _make_lens_panel('lnsTagcloud')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'tagcloud'


def test_decompile_datatable_type() -> None:
    """LnsDatatable maps to datatable type."""
    panel = _make_lens_panel('lnsDatatable')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'datatable'


def test_decompile_metric_with_label() -> None:
    """Metric label is extracted from column."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'count',
                                    'isBucketed': False,
                                    'sourceField': 'Records',
                                    'label': 'Total Requests',
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    primary = result['lens']['primary']
    assert primary['label'] == 'Total Requests'


def test_decompile_metric_preserves_column_filter_and_format() -> None:
    """Metric extraction preserves per-column filter and format metadata."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col1': {
                                    'operationType': 'sum',
                                    'isBucketed': False,
                                    'sourceField': 'bytes',
                                    'filter': {'query': 'response.status_code >= 500', 'language': 'kuery'},
                                    'params': {
                                        'kql': 'response.status_code >= 200',
                                        'format': {
                                            'id': 'bytes',
                                            'params': {'decimals': 1, 'suffix': ' B', 'compact': True},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    primary = result['lens']['primary']

    assert primary['aggregation'] == 'sum'
    assert primary['field'] == 'bytes'
    assert primary['filter']['kql'] == 'response.status_code >= 500'
    assert primary['format']['type'] == 'bytes'
    assert primary['format']['decimals'] == 1
    assert primary['format']['suffix'] == ' B'
    assert primary['format']['compact'] is True


def test_decompile_form_based_uses_visualization_accessors() -> None:
    """Column extraction follows visualization accessors and skips helper columns."""
    panel = _make_lens_panel(
        'lnsXY',
        state={
            'visualization': {
                'preferredSeriesType': 'line',
                'layers': [
                    {
                        'layerId': 'layer1',
                        'xAccessor': 'col_time',
                        'splitAccessor': 'col_host',
                        'accessors': ['col_metric'],
                    }
                ],
            },
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col_helper': {
                                    'operationType': 'avg',
                                    'isBucketed': False,
                                    'sourceField': 'helper.value',
                                },
                                'col_metric': {
                                    'operationType': 'sum',
                                    'isBucketed': False,
                                    'sourceField': 'bytes',
                                },
                                'col_time': {
                                    'operationType': 'date_histogram',
                                    'isBucketed': True,
                                    'sourceField': '@timestamp',
                                    'params': {'interval': '1h'},
                                },
                                'col_host': {
                                    'operationType': 'terms',
                                    'isBucketed': True,
                                    'sourceField': 'host.name',
                                    'params': {'size': 5},
                                },
                            },
                        },
                    },
                },
            },
        },
    )
    result = _decompile_single_panel(panel)
    lens = result['lens']

    assert lens['metrics'][0]['aggregation'] == 'sum'
    assert lens['metrics'][0]['field'] == 'bytes'
    assert lens['dimension']['field'] == '@timestamp'
    assert lens['dimension']['minimum_interval'] == '1h'
    assert lens['breakdown']['field'] == 'host.name'


def test_decompile_form_based_uses_top_level_visualization_accessors() -> None:
    """Column extraction honors metric/gauge top-level visualization accessors."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'visualization': {
                'layerId': 'layer1',
                'metricAccessor': 'col_primary',
                'secondaryAccessor': 'col_secondary',
            },
            'datasourceStates': {
                'formBased': {
                    'layers': {
                        'layer1': {
                            'columns': {
                                'col_ignored': {
                                    'operationType': 'sum',
                                    'isBucketed': False,
                                    'sourceField': 'ignored.bytes',
                                },
                                'col_secondary': {
                                    'operationType': 'avg',
                                    'isBucketed': False,
                                    'sourceField': 'cpu.usage',
                                },
                                'col_primary': {
                                    'operationType': 'sum',
                                    'isBucketed': False,
                                    'sourceField': 'bytes',
                                },
                            }
                        }
                    }
                }
            },
        },
    )
    result = _decompile_single_panel(panel)
    lens = result['lens']

    assert lens['primary']['aggregation'] == 'sum'
    assert lens['primary']['field'] == 'bytes'
    assert lens['secondary']['aggregation'] == 'average'
    assert lens['secondary']['field'] == 'cpu.usage'


def test_decompile_lens_with_text_based_query_emits_esql_stub() -> None:
    """Lens textBased panels are emitted as ES|QL stubs with query + required metric field."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
            'query': {'esql': 'FROM metrics-* | STATS count = COUNT(*)'},
            'datasourceStates': {
                'textBased': {
                    'layers': {
                        'layer1': {
                            'columns': [{'columnId': 'col_metric', 'fieldName': 'count'}],
                        }
                    }
                },
            },
            'visualization': {'layerId': 'layer1', 'metricAccessor': 'col_metric'},
        },
    )
    result = _decompile_single_panel(panel)
    assert 'esql' in result
    assert result['esql']['query'] == 'FROM metrics-* | STATS count = COUNT(*)'
    assert result['esql']['primary']['field'] == 'count'


@pytest.mark.parametrize(
    'relative_yaml_path',
    [
        'filters-example.yaml',
        'system/01-metrics-overview.yaml',
        'crowdstrike/alert.yaml',
    ],
)
def test_compile_decompile_compile_roundtrip_examples(relative_yaml_path: str) -> None:
    """Roundtrip compile->decompile->compile should not error for representative examples."""
    yaml_path = _EXAMPLES_DIR / relative_yaml_path
    dashboards = load(str(yaml_path))
    assert len(dashboards) > 0

    for dashboard in dashboards:
        compiled_dashboard = render(dashboard).model_dump(by_alias=True)
        decompiled_yaml = decompile_dashboard(compiled_dashboard)
        roundtrip_config = DashboardConfig.model_validate(decompiled_yaml)
        assert len(roundtrip_config.dashboards) > 0
        for roundtrip_dashboard in roundtrip_config.dashboards:
            render(roundtrip_dashboard)


# ---------------------------------------------------------------------------
# Integration tests: real dashboards from elastic/integrations
# ---------------------------------------------------------------------------

_FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures' / 'elastic-integrations'


def _load_fixture(name: str) -> dict[str, Any]:
    with (_FIXTURES_DIR / name).open() as f:
        return cast('dict[str, Any]', json.load(f))


@pytest.mark.parametrize(
    'fixture_name',
    [
        'nginx-overview.json',
        'nginx-access-errors.json',
        'system-overview.json',
    ],
)
def test_decompile_real_dashboard_does_not_crash(fixture_name: str) -> None:
    """Decompiling real elastic/integrations dashboards must not crash."""
    dashboard = _load_fixture(fixture_name)
    result = decompile_dashboard(dashboard)
    dashboards = result['dashboards']
    assert len(dashboards) == 1
    assert isinstance(dashboards[0]['name'], str)
    assert len(dashboards[0]['name']) > 0
    assert len(dashboards[0]['panels']) > 0


@pytest.mark.parametrize(
    'fixture_name',
    [
        'nginx-overview.json',
        'nginx-access-errors.json',
        'system-overview.json',
    ],
)
def test_decompile_real_dashboard_produces_valid_yaml(fixture_name: str) -> None:
    """Decompiled real dashboards produce valid YAML that can be dumped."""
    dashboard = _load_fixture(fixture_name)
    result = decompile_dashboard(dashboard)
    yaml = YAML(typ='rt')
    stream = io.StringIO()
    yaml.dump(result, stream)
    output = stream.getvalue()
    assert 'dashboards:' in output
    assert 'panels:' in output


@pytest.mark.parametrize(
    'fixture_name',
    [
        'nginx-overview.json',
        'nginx-access-errors.json',
        'system-overview.json',
    ],
)
def test_decompile_real_dashboard_validates_as_dashboard_config(fixture_name: str) -> None:
    """Decompiled real dashboards validate as DashboardConfig (roundtrip parse)."""
    dashboard = _load_fixture(fixture_name)
    result = decompile_dashboard(dashboard)
    config = DashboardConfig.model_validate(result)
    assert len(config.dashboards) > 0
    for db in config.dashboards:
        assert db.name is not None


@pytest.mark.parametrize(
    'fixture_name',
    [
        'nginx-overview.json',
        'system-overview.json',
    ],
)
def test_decompile_real_dashboard_roundtrip_compiles(fixture_name: str) -> None:
    """Decompiled real dashboards can be re-compiled without errors."""
    dashboard = _load_fixture(fixture_name)
    result = decompile_dashboard(dashboard)
    config = DashboardConfig.model_validate(result)
    for db in config.dashboards:
        render(db)


def test_decompile_nginx_overview_extracts_chart_types() -> None:
    """Nginx overview dashboard has XY charts with correct types."""
    dashboard = _load_fixture('nginx-overview.json')
    result = decompile_dashboard(dashboard)
    panels = result['dashboards'][0]['panels']
    chart_types = set()
    for panel in panels:
        if 'lens' in panel:
            chart_types.add(panel['lens'].get('type'))
        elif 'esql' in panel:
            chart_types.add(panel['esql'].get('type'))
    assert len(chart_types) > 0


def test_decompile_system_overview_has_metric_panels() -> None:
    """System overview dashboard has metric panels with data_view."""
    dashboard = _load_fixture('system-overview.json')
    result = decompile_dashboard(dashboard)
    panels = result['dashboards'][0]['panels']
    metric_panels = [p for p in panels if 'lens' in p and p['lens'].get('type') == 'metric']
    assert len(metric_panels) > 0
    for panel in metric_panels:
        assert panel['lens'].get('data_view') is not None


def test_parse_real_dashboard_produces_typed_structure() -> None:
    """Parse phase produces fully typed ParsedDashboard from real JSON."""
    dashboard = _load_fixture('nginx-overview.json')
    parsed = parse_dashboard(dashboard)
    assert parsed.title is not None
    assert len(parsed.panels) > 0
    for panel in parsed.panels:
        assert panel.error is None, f'Panel {panel.panel_index} had parse error: {panel.error}'
        assert panel.lens is not None or panel.simple is not None


def test_parse_system_dashboard_detects_visualization_types() -> None:
    """Parse phase detects all visualization types in system overview."""
    dashboard = _load_fixture('system-overview.json')
    parsed = parse_dashboard(dashboard)
    vis_types = set()
    for panel in parsed.panels:
        if panel.lens is not None and panel.lens.visualization_type is not None:
            vis_types.add(panel.lens.visualization_type)
    assert 'lnsMetric' in vis_types
    assert 'lnsDatatable' in vis_types or 'lnsHeatmap' in vis_types


def test_parse_real_dashboard_validates_visualization_view_models() -> None:
    """Parse phase threads real Lens visualization state through Kbn* view models."""
    dashboard = _load_fixture('system-overview.json')
    parsed = parse_dashboard(dashboard)
    view_models = [
        panel.lens.view_visualization for panel in parsed.panels if panel.lens is not None and panel.lens.view_visualization is not None
    ]
    assert view_models


def test_parse_dashboard_validates_settings_filters_and_controls_view_models() -> None:
    """Parse phase validates dashboard-level parts against Kbn* view models when available."""
    dashboard = {
        'attributes': {
            'title': 'Typed bits',
            'optionsJSON': json.dumps(
                {
                    'useMargins': False,
                    'syncColors': True,
                    'syncCursor': True,
                    'syncTooltips': False,
                    'hidePanelTitles': True,
                }
            ),
            'kibanaSavedObjectMeta': {
                'searchSourceJSON': json.dumps(
                    {
                        'query': {'language': 'kuery', 'query': 'host.name : "web-01"'},
                        'filter': [
                            {
                                '$state': {'store': 'appState'},
                                'meta': {
                                    'disabled': False,
                                    'negate': False,
                                    'key': 'host.name',
                                    'field': 'host.name',
                                    'type': 'phrase',
                                    'params': {'query': 'web-01'},
                                },
                                'query': {'match_phrase': {'host.name': 'web-01'}},
                            }
                        ],
                    }
                )
            },
            'controlGroupInput': {
                'panelsJSON': json.dumps(
                    {
                        'control-1': {
                            'type': 'optionsListControl',
                            'grow': False,
                            'order': 0,
                            'width': 'medium',
                            'explicitInput': {
                                'id': 'control-1',
                                'fieldName': 'host.name',
                                'title': 'Host',
                                'dataViewId': 'metrics-*',
                                'searchTechnique': 'prefix',
                                'selectedOptions': [],
                                'sort': {'by': '_count', 'direction': 'desc'},
                            },
                        }
                    }
                )
            },
        }
    }

    parsed = parse_dashboard(dashboard)

    assert parsed.settings is not None
    assert parsed.settings.view_options is not None
    assert parsed.query == {'kql': 'host.name : "web-01"'}
    assert parsed.filters
    assert parsed.filters[0].view_filter is not None
    assert parsed.controls
    assert parsed.controls[0].view_control is not None

    result = decompile_dashboard(dashboard)
    decompiled = result['dashboards'][0]
    assert decompiled['query'] == {'kql': 'host.name : "web-01"'}


def test_parse_json_field_invalid_json_returns_none() -> None:
    """Malformed stringified JSON is ignored in best-effort parse mode."""
    assert parse_json_field('{not-json') is None


def test_get_int_excludes_bools() -> None:
    """Boolean values are not treated as integers."""
    assert get_int({'order': True}, 'order') is None
    assert get_int({'order': 1}, 'order') == 1


def test_parse_panel_ref_name_without_embedded_attributes_sets_error() -> None:
    """Unresolved panel references produce explicit parse errors."""
    dashboard = {
        'attributes': {
            'title': 'Panel references',
            'panelsJSON': json.dumps(
                [
                    {
                        'panelIndex': 'p1',
                        'type': 'lens',
                        'panelRefName': 'panel_ref_0',
                    }
                ]
            ),
        }
    }
    parsed = parse_dashboard(dashboard)
    assert len(parsed.panels) == 1
    assert parsed.panels[0].error == 'unresolved panel reference: panel_ref_0'
    assert parsed.panels[0].lens is None
    assert parsed.panels[0].simple is None
