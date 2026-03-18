"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/arista_ngfw/kibana/dashboard/arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798.json`."""
    assert integrations_yaml_for('packages/arista_ngfw/kibana/dashboard/arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798.json') == snapshot("""\
dashboards:
- name: Arista NG Firewall Session Stats
  id: arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798
  description: ''
  settings:
    margins: false
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 20d48459-770b-4cde-8ede-72b084ea1772
    title: ''
    hide_title: true
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: '# Arista NG Firewall Session Stats'}
  - id: 13262519-30cf-49ea-a20e-e68cd2ed1a44
    title: ''
    size: {w: 48, h: 4}
    position: {x: 0, y: 4}
    links:
      layout: horizontal
      items:
      - {id: arista_ngfw-86b139ff-92ab-4aae-b0d8-c33e3be132f1, label: Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-86b139ff-92ab-4aae-b0d8-c33e3be132f1_dashboard}
      - {id: arista_ngfw-2b026f60-1cf1-11ee-b346-5b9e0073e798, label: Admin \n\
          Login, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-2b026f60-1cf1-11ee-b346-5b9e0073e798_dashboard}
      - {id: arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798, label: Session \n\
          Stats, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798_dashboard}
      - {id: arista_ngfw-c61b1eb0-1cf7-11ee-b346-5b9e0073e798, label: Web Filter,
        dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-c61b1eb0-1cf7-11ee-b346-5b9e0073e798_dashboard}
      - {id: arista_ngfw-0f3dafe6-c66a-4d1e-a9e9-fa3fb418bfaf, label: Intrusion \n\
          Prevention, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-0f3dafe6-c66a-4d1e-a9e9-fa3fb418bfaf_dashboard}
      - {id: arista_ngfw-93596b63-d808-4a2f-9cbf-d0e9c4003079, label: System \n\
          Stats, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-93596b63-d808-4a2f-9cbf-d0e9c4003079_dashboard}
      - {id: arista_ngfw-a4bb8521-b9d4-4d33-be52-b4ccefb2eee1, label: Interface \n\
          Stats, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-a4bb8521-b9d4-4d33-be52-b4ccefb2eee1_dashboard}
  - id: 07dd66c3-cfbf-450e-835d-a2d1d15560b3
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 0, y: 8}
    lens:
      id: 38f6e595-d72c-afd6-7393-c4e0d5413bcf
      type: metric
      data_view: logs-*
      primary:
        id: 60f0e2e9-80aa-c60f-c9ac-4315f30ac797
        label: Total Network Bytes
        format: {type: bytes, decimals: 2}
        aggregation: sum
        field: network.bytes
  - id: ff518a08-7f9c-439b-92e1-488179e73e27
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 9, y: 8}
    lens:
      id: 788bab94-e278-d2bd-17b8-50faeed3c0ba
      type: metric
      data_view: logs-*
      primary:
        id: 553fc9d2-2640-b373-7038-7b43516fbb74
        label: Unique Source IP Addresses
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: source.ip
  - id: e13dda86-df4f-4f15-842c-dc5c757c36f5
    title: Bytes Transferred Over Time
    size: {w: 30, h: 16}
    position: {x: 18, y: 8}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: ff3cd2d8-387a-7746-c37c-28931d933d67
        label: Network Bytes
        format: {type: bytes, decimals: 2}
        filter: {kql: 'network.bytes: *'}
        aggregation: last_value
        field: network.bytes
      id: 764dcbe8-2e89-1b65-3985-fa51b2982520
      legend: {visible: hide, width: large, truncate_labels: 0}
      type: bar
      mode: stacked
  - id: 6d7ec786-8684-41e7-bee4-fcb34344e506
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 0, y: 16}
    lens:
      id: 611c5992-43c7-d115-9681-759f1b1fd3b4
      type: metric
      data_view: logs-*
      primary: {id: 9659d1ad-3346-6601-fd44-abb8ddca185e, label: Unique Sessions,
        aggregation: unique_count, field: event.id}
  - id: fc886fe0-c926-430c-b91d-2d5dde9f4ccf
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 9, y: 16}
    lens:
      id: f4fc2c85-f148-5a54-5a46-93f8a57f2f32
      type: metric
      data_view: logs-*
      primary:
        id: 828620bd-d524-ad12-485e-8b1d35276796
        label: Unique Destination IP Addresses
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: destination.ip
  - id: 86e18a08-a067-481c-a16c-af7ae7d17eec
    title: Top 500 Source IP's by Bytes Transferred
    size: {w: 11, h: 24}
    position: {x: 0, y: 24}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: 7373d679-ddbb-5f04-a077-69ca19958b06
      data_view: logs-*
      metrics:
      - id: ac60419e-296d-5ab4-1456-4d1264965548
        label: Total Source Bytes
        format: {type: bytes, decimals: 2}
        aggregation: sum
        field: source.bytes
      breakdowns:
      - {id: 5b9dbf18-3fa2-dc61-f776-d851d26efde1, type: values, size: 500, \n\
          field: source.ip}
  - id: 5b9db7a3-da2a-4bbf-b828-26c28337a81c
    title: Top 500 Destination IP's by Bytes Transferred
    size: {w: 11, h: 24}
    position: {x: 11, y: 24}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: e673ae2a-bcfd-1d8d-4681-2d5a8d5b11bd
      data_view: logs-*
      metrics:
      - id: 209245a0-3f5d-412d-a3ab-20d9f3ac7c7b
        label: Total Destination Bytes
        format: {type: bytes, decimals: 2}
        aggregation: sum
        field: destination.bytes
      breakdowns:
      - {id: 26d1ab6d-96a8-8f39-250b-87f07964d50f, type: values, size: 500, \n\
          field: destination.ip}
  - id: 7355a77d-85cd-41ed-b1da-f238a3ea84bd
    title: ''
    size: {w: 48, h: 40}
    position: {x: 0, y: 48}
    search: {saved_search_id: TODO_saved_search_id}
  - id: 6ae5c6ae-a667-49e2-aa53-2fe5a2d5b6d8
    title: Events by Source to Destination GeoLocation
    size: {w: 26, h: 24}
    position: {x: 22, y: 24}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
""")
