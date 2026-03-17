"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/auditd/kibana/dashboard/auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb.json`."""
    assert integrations_yaml_for('packages/auditd/kibana/dashboard/auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb.json') == snapshot("""\
dashboards:
- name: '[Logs Auditd] Audit Events'
  id: auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb
  description: Dashboard for the Auditd Logs integration
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: '1'
    title: Event types breakdown [Logs Auditd]
    size: {w: 16, h: 16}
    position: {x: 0, y: 0}
    lens:
      id: 903abd3b-90dc-73c8-d2c8-e515a7b6992e
      type: pie
      appearance:
        donut: medium
        values: {decimal_places: 2}
      legend: {visible: hide, truncate_labels: 1}
      data_view: logs-*
      metrics:
      - {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: ade70d6e-e7a0-ff05-784e-d503e3fa785d, type: values, size: 50, field: \n\
          event.action}
  - id: '2'
    title: Top Exec Commands [Logs Auditd]
    size: {w: 16, h: 16}
    position: {x: 32, y: 0}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 15d555ac-ffdc-1bb5-7840-593cc044986b
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 74d2078a-75aa-7938-5e47-4df6b852e788, type: values, size: 30, field: \n\
          auditd.log.a0}
  - id: '7'
    title: ''
    size: {w: 48, h: 20}
    position: {x: 0, y: 28}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_7'}
  - id: d84a9a87-e40f-465c-9114-4d343ffb6481
    title: Event Account Tag Cloud [Logs Auditd]
    size: {w: 16, h: 16}
    position: {x: 16, y: 0}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: 904b21e5-b428-ebb8-f57d-ecfacf9618dc
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 005c89df-8ef9-fb6d-3700-75e21e4ed54d, type: values, size: 20, field: \n\
          user.name}
  - id: e1817f83-5b41-4dd8-8108-ffe725dc9cd2
    title: Event Results [Logs Auditd]
    size: {w: 24, h: 12}
    position: {x: 0, y: 16}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 2ee316f6-f221-ade4-14b6-c17eb4102f59
        label: Success
        filter: {kql: 'event.outcome : "success" '}
        aggregation: count
        field: ___records___
      - id: a877fdf6-7537-e4c5-a433-f7ba92760b34
        label: Failure
        filter: {kql: 'event.outcome : "failure"'}
        aggregation: count
        field: ___records___
      id: 25e76f0f-b803-ff74-b0bc-0f6c2ac6b2c8
      legend: {visible: show}
      type: line
      appearance:
        y_left_axis: {title: Count}
  - id: 09f4ba02-a62c-410f-8d43-31e9e5278826
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 16}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
""")
