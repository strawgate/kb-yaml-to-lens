"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json`."""
    assert integrations_yaml_for('packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json') == snapshot("""\
dashboards:
- name: '[Logs System] Syslog dashboard'
  id: system-Logs-syslog-dashboard
  description: Syslog dashboard from the Logs System integration
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: system.syslog}
  panels:
  - id: '4'
    title: Dashboards
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: system-Logs-syslog-dashboard, label: Syslog, dashboard: \n\
          TODO_dashboard_id_for_link_system-Logs-syslog-dashboard_dashboard, \n\
          new_tab: false, with_time: true, with_filters: false}
      - {id: system-277876d0-fa2c-11e6-bbd3-29c986c96e5a, label: Sudo commands, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_system-277876d0-fa2c-11e6-bbd3-29c986c96e5a_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: system-5517a150-f9ce-11e6-8115-a7c18106d86a, label: SSH logins, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_system-5517a150-f9ce-11e6-8115-a7c18106d86a_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: system-0d3f2380-fa78-11e6-ae9b-81e5311e8cab, label: New users and \n\
          groups, dashboard: \n\
          TODO_dashboard_id_for_link_system-0d3f2380-fa78-11e6-ae9b-81e5311e8cab_dashboard,
        new_tab: false, with_time: true, with_filters: false}
  - id: 1c0a80d4-cd4d-488a-a06d-e9b816e733a8
    title: Syslog events by hostname
    size: {w: 32, h: 16}
    position: {x: 0, y: 4}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: cacf4e9a-9fb7-5f22-4c5f-a37b28c41fc8
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      mode: stacked
  - id: 30ce1a8d-6460-45b6-be1a-841db5ca7c8b
    title: Syslog hostnames and processes
    size: {w: 16, h: 16}
    position: {x: 32, y: 4}
    lens:
      id: 9faf9364-addc-80f3-946a-5018ca596574
      type: treemap
      appearance:
        values: {decimal_places: 2}
      legend: {visible: hide, position: bottom, truncate_labels: 1}
      data_view: logs-*
      metric: {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: 5, field: \n\
          host.hostname}
      - {id: cf40b962-6df3-09a0-9724-8adf72638e3e, type: values, size: 5, field: \n\
          process.name}
  - id: f08ec141-4b46-4e87-9b1c-3bb1bb502d3e
    title: Syslog logs
    size: {w: 48, h: 28}
    position: {x: 0, y: 20}
    search: {saved_search_id: TODO_saved_search_id}
""")
