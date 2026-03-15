"""Tests for dashboard decompiler tool."""

import io
import json
from typing import Any

from ruamel.yaml import YAML

from kb_dashboard_tools.decompile import decompile_dashboard


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
    """LnsPie with shape=donut yields donut."""
    panel = _make_lens_panel('lnsPie', state={'visualization': {'shape': 'donut'}})
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'donut'


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


# --- Formula panels should have TODO ---


def test_decompile_formula_panel_has_todo() -> None:
    """Formula operations emit TODO comment in _todo field."""
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
    assert 'primary' not in result['lens']
    assert 'metrics' not in result['lens']


# --- ES|QL query extraction ---


def test_decompile_esql_query() -> None:
    """Extract ES|QL query from textBased datasource."""
    panel = _make_lens_panel(
        'lnsMetric',
        state={
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
    )
    result = _decompile_single_panel(panel)
    assert result['lens']['query'] == 'FROM logs-* | STATS count=COUNT()'


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
    """LnsDatatable maps to table type."""
    panel = _make_lens_panel('lnsDatatable')
    result = _decompile_single_panel(panel)
    assert result['lens']['type'] == 'table'


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
