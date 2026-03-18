"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/1password/kibana/dashboard/1password-signin-attempts-full-dashboard.json`."""
    assert integrations_yaml_for('packages/1password/kibana/dashboard/1password-signin-attempts-full-dashboard.json') == snapshot("""\
dashboards:
- name: Sign-in Attempts [1Password]
  id: 1password-signin-attempts-full-dashboard
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 944e346e-36df-430b-9734-5d91da79bdc1
    title: ''
    size: {w: 31, h: 15}
    position: {x: 0, y: 0}
    search: {saved_search_id: TODO_saved_search_id}
  - id: 5a635dbb-4cb6-46f8-9d4c-dd12078b184f
    title: ''
    size: {w: 17, h: 15}
    position: {x: 31, y: 0}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: b778af01-c0b6-4b57-a675-d39d1c6db832
    title: Sign-in Attempts unsuccessful [1Password]
    size: {w: 11, h: 9}
    position: {x: 0, y: 15}
    lens:
      id: 7fe11da5-5ad7-9c76-e9f0-66cf6fbb22d7
      type: metric
      data_view: logs-*
      primary: {id: 5880480d-6ce5-b13e-4a11-0bf4d6444efc, label: Failed Signin \n\
          Attempts, aggregation: count, field: ___records___}
  - id: 51433376-546a-492a-906e-9ca7f5d34f68
    title: Sign-in Attempts over time [1Password]
    size: {w: 20, h: 9}
    position: {x: 11, y: 15}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      id: 629f4f74-7f0a-5ab5-f057-470b4e466205
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        y_left_axis:
          title: Count
          extent: {mode: data_bounds}
      mode: stacked
  - id: 8f8ae43c-e8d4-4425-b418-224a7db57e86
    title: Sign-in Attempts categories over time [1Password]
    size: {w: 17, h: 9}
    position: {x: 31, y: 15}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 208bfe09-9d04-9a3c-f6f5-80128d02dbe2, type: values, size: \n\
          10, field: event.action}
      id: e32d4517-ebb2-fe33-a04a-291e3c4c31ff
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        y_left_axis:
          title: Count
          extent: {mode: data_bounds}
      mode: stacked
  - id: 63f0a044-8a96-4664-9a05-cb8f4503b133
    title: Sign-in Attempts hot users [1Password]
    size: {w: 48, h: 9}
    position: {x: 0, y: 24}
    lens:
      type: datatable
      id: 2bc68fca-a9aa-86c0-039b-1b4c7eadef8c
      data_view: logs-*
      metrics:
      - {id: a27df444-1804-d42c-480f-4a2e1e2bcd2f, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 6f07e67c-e270-6bb6-1ac6-8cff766e9df0, type: values, size: 10, field: \n\
          user.id}
      - {id: 542b05be-ab2d-11ca-9cb7-74e8a5562fa4, type: values, size: 10, field: \n\
          user.full_name}
      - {id: 2b90eb88-cd3a-1cc2-01f7-158e7a7be000, type: values, size: 10, field: \n\
          user.email}
""")
