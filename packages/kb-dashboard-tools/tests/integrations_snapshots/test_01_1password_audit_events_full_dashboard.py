"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/1password/kibana/dashboard/1password-audit-events-full-dashboard.json`."""
    assert integrations_yaml_for('packages/1password/kibana/dashboard/1password-audit-events-full-dashboard.json') == snapshot("""\
dashboards:
- name: Audit Events [1Password]
  id: 1password-audit-events-full-dashboard
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: a9a9a507-ae79-422c-ac05-2f4d9a2bb5e6
    title: ''
    size: {w: 31, h: 15}
    position: {x: 0, y: 0}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_a9a9a507-ae79-422c-ac05-2f4d9a2bb5e6'}
  - id: 5191f658-f717-49ec-9d3c-7c881c07a502
    title: ''
    size: {w: 17, h: 15}
    position: {x: 31, y: 0}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: 7521b1b8-37a6-4890-a450-631bf653fb93
    title: Audit Events over time [1Password]
    size: {w: 24, h: 11}
    position: {x: 0, y: 15}
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
  - id: c76ab1dd-2177-4b19-8d0f-a44cd7280a79
    title: ''
    size: {w: 24, h: 11}
    position: {x: 24, y: 15}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: e1868285-62c1-b8c0-a668-0883f6013da8
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 1815f4d9-4f4d-5e1a-6d48-db1a08531383, type: values, size: 5, field: \n\
          user.id}
  - id: 6785d29f-971b-445d-8997-dd97f302814d
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 26}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 06d37e60-cf62-1329-cbe0-97ca8d3e11ed
      data_view: logs-*
      metrics:
      - {id: a27df444-1804-d42c-480f-4a2e1e2bcd2f, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 104c363e-2b3a-4497-1bc0-00d896626b28, type: values, size: 5, field: \n\
          event.action}
  - id: 60da356b-c843-4d41-8bf4-04e04ef77734
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 26}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 28a3257e-2b4f-f978-707b-247bbfa4fb47
      data_view: logs-*
      metrics:
      - {id: a27df444-1804-d42c-480f-4a2e1e2bcd2f, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 0f607a96-502a-16a1-cf06-275a8d952efd, type: values, size: 5, field: \n\
          onepassword.object_type}
""")
