"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/activemq/kibana/dashboard/activemq-f98d0c50-f916-11ec-9736-016ee09668f5.json`."""
    assert integrations_yaml_for('packages/activemq/kibana/dashboard/activemq-f98d0c50-f916-11ec-9736-016ee09668f5.json') == snapshot("""\
dashboards:
- name: '[Logs ActiveMQ] Log'
  id: activemq-f98d0c50-f916-11ec-9736-016ee09668f5
  description: This dashboard shows application logs collected by the ActiveMQ \n\
    logs integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: activemq.log}
  panels:
  - id: b6bdc4b4-745a-4fa2-9928-9f7cb783f5b9
    title: Application Event Results [Logs ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 0, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 9a67312b-1682-a72c-7a73-945c2481482a, type: values, size: \n\
          15, field: log.level}
      id: 28d90856-3822-15b3-584e-59b6b991ecc6
      legend: {visible: show, show_single_series: true}
      type: bar
      appearance:
        y_left_axis: {title: Count}
      mode: stacked
  - id: 843b2c29-7386-41ac-acdd-286021471008
    title: Top Error Callers [Logs ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 24, y: 0}
    lens:
      type: datatable
      id: a9e2d24a-a220-24e2-4728-b3270adf7626
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: c5578263-cddd-0537-786f-ce84c050ac4e, type: values, size: 10, field: \n\
          activemq.log.caller}
  - id: 58c5e9cf-4342-4a2c-a893-98de182dc283
    title: Application Events [Logs ActiveMQ]
    size: {w: 48, h: 22}
    position: {x: 0, y: 15}
    search: {saved_search_id: TODO_saved_search_id}
""")
