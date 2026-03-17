"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json`."""
    assert integrations_yaml_for('packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json') == snapshot("""\
dashboards:
- name: '[Logs MySQL] Overview'
  id: mysql-Logs-MySQL-Dashboard
  description: Overview dashboard for the Logs MySQL integration
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [mysql.error, mysql.slowlog]
  panels:
  - id: '1'
    title: Top slowest queries [Logs MySQL]
    size: {w: 24, h: 20}
    position: {x: 0, y: 28}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 3f68aff4-efd0-853c-a305-f819a28c83ca
      data_view: logs-*
      metrics:
      - id: e2ad6534-dddb-8f6e-50c0-9335b78ab605
        label: Query time (ms)
        format: {type: number, decimals: 2}
        formula: max(event.duration)/1000000
      - {id: 9ce5a389-ce65-794f-f251-099e2eb8c699, label: Part of Query time, \n\
          aggregation: max, field: event.duration}
      breakdowns:
      - {id: 5d3c36e4-47ea-6d0c-56df-ae4db7870141, type: values, size: 5, field: \n\
          mysql.slowlog.query}
      - {id: 8796bbeb-09f2-cde1-db44-f3876594529f, type: values, size: 5, field: \n\
          user.name}
  - id: '2'
    title: Slow queries over time [Logs MySQL]
    size: {w: 24, h: 12}
    position: {x: 0, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 6b279897-7436-6186-81e5-53853d38f824, label: Slow queries, \n\
          aggregation: count, field: ___records___}
      id: 439152fd-f182-38ae-2ee0-6d95fa50ca8e
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        x_axis: {title: '@timestamp per 30 seconds'}
        y_left_axis: {title: Slow queries}
      mode: stacked
  - id: '3'
    title: Error logs over time [Logs MySQL]
    size: {w: 24, h: 12}
    position: {x: 24, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 0bdd6627-4c9b-2fb2-eda7-ed6d4cc3d49a, label: Error logs, \n\
          aggregation: count, field: ___records___}
      id: 0bd158c8-0a10-108a-63f1-baf3267dd775
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        x_axis: {title: '@timestamp per 30 seconds'}
        y_left_axis: {title: Error logs}
      mode: stacked
  - id: '5'
    title: Error logs levels breakdown [Logs MySQL]
    size: {w: 24, h: 16}
    position: {x: 24, y: 12}
    lens:
      id: 79334a28-b3c6-076d-e9d8-4658fde81a01
      type: pie
      appearance:
        values: {decimal_places: 2}
      legend: {visible: show, position: bottom, truncate_labels: 1}
      data_view: logs-*
      metrics:
      - {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: cce5efe2-b956-597b-69f9-9a771b3a0b2a, type: values, size: 5, field: \n\
          log.level}
  - id: '6'
    title: Slow logs breakdown [Logs MySQL]
    size: {w: 24, h: 16}
    position: {x: 0, y: 12}
    lens:
      id: 68eeb524-7985-7df7-e4f2-eab0d00db9ca
      type: pie
      appearance:
        values: {decimal_places: 2}
      legend: {visible: show, position: bottom, truncate_labels: 1}
      data_view: logs-*
      metrics:
      - {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: c3744947-3e00-020e-b25d-b3b051be5ead, type: values, size: 5, field: \n\
          mysql.slowlog.query}
  - id: 4d60bed6-79cf-4852-bf1b-224bd94635fe
    title: Error logs [Logs MySQL]
    size: {w: 24, h: 20}
    position: {x: 24, y: 28}
    search: {saved_search_id: TODO_saved_search_id}
""")
