"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/apache/kibana/dashboard/apache-Metrics-Apache-HTTPD-server-status.json`."""
    assert integrations_yaml_for('packages/apache/kibana/dashboard/apache-Metrics-Apache-HTTPD-server-status.json') == snapshot("""\
dashboards:
- name: '[Metrics Apache] Overview'
  id: apache-Metrics-Apache-HTTPD-server-status
  description: Overview of Apache server status
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: apache.status}
  controls:
  - id: 2bb288fa-d4b0-8b0e-caea-8bb16f92be0a
    label: Hostname
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 7b7a1f18-e274-4f4e-a3b3-3760e7896897
    title: Uptime [Metrics Apache]
    size: {w: 16, h: 7}
    position: {x: 0, y: 0}
    lens:
      id: 7fe7c15b-3101-5368-71fb-0b2b787af31d
      type: metric
      data_view: TODO_data_view
      primary:
        id: 6a0b603f-2e53-3418-1d5e-e2eef541f20b
        label: Uptime
        format: {type: duration, decimals: 2}
        aggregation: max
        field: apache.status.uptime.uptime
  - id: bcaad3c3-d62c-44bd-8e76-f00cb8a7f0eb
    title: Total accesses [Metrics Apache]
    size: {w: 16, h: 7}
    position: {x: 16, y: 0}
    lens:
      id: b59cab30-64cf-587e-28d4-0c88937c3670
      type: metric
      data_view: metrics-*
      primary: {id: 683329d5-9fbc-5fd2-c839-6a8b018a9b6c, label: ' Total accesses',
        aggregation: max, field: apache.status.total_accesses}
  - id: ea52006e-efe5-499a-88e7-2843258d6905
    title: Total egress [Metrics Apache]
    size: {w: 16, h: 7}
    position: {x: 32, y: 0}
    lens:
      id: 7ef8a433-10a5-2185-453e-f4788d8e5c99
      type: metric
      data_view: metrics-*
      primary:
        id: edd4edb6-368e-9953-054b-ad2eeac4293f
        label: Total egress
        format: {type: bytes, decimals: 1}
        aggregation: max
        field: apache.status.total_bytes
  - id: 9386f867-d876-448b-b5fb-cc39eefb09cd
    title: Requests per sec [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 22}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 64c7d943-72f7-fe95-19eb-7f57ef3f64b3, label: Requests per sec, \n\
          aggregation: average, field: apache.status.requests_per_sec}
      id: cfab55f1-a9b0-0f14-313c-54b4668ae2a3
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Requests per sec}
        missing_values: linear
  - id: fb9f73a9-022d-4f08-a176-a4af0618cfc6
    title: Scoreboard [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 7}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: e55fe8b6-966c-7df0-71c4-7b83c4b61410, label: Closing connection, \n\
          aggregation: average, field: \n\
          apache.status.scoreboard.closing_connection}
      - {id: 9884ef4b-21ec-ea11-1e78-5acee20fe6a5, label: DNS lookup, \n\
          aggregation: average, field: apache.status.scoreboard.dns_lookup}
      - {id: ee5696fa-79af-5ba5-6ba2-2bd7208f1197, label: Gracefully finishing, \n\
          aggregation: average, field: \n\
          apache.status.scoreboard.gracefully_finishing}
      - {id: c2c72109-59ae-ec6c-046f-b083b158ba99, label: Idle cleanup, \n\
          aggregation: average, field: apache.status.scoreboard.idle_cleanup}
      - {id: 50173818-3646-6cdd-eb6b-fcc95e22f035, label: Keepalive, aggregation: \n\
          average, field: apache.status.scoreboard.keepalive}
      - {id: 46ae596e-bf2b-c988-48e6-61d98b06d271, label: Logging, aggregation: \n\
          average, field: apache.status.scoreboard.logging}
      - {id: 3698d8fc-3697-f767-ef90-d5ba4347fae9, label: Open slot, aggregation: \n\
          average, field: apache.status.scoreboard.open_slot}
      - {id: f1ef9469-ae70-066e-d71f-7bcb2009cd50, label: Reading request, \n\
          aggregation: average, field: apache.status.scoreboard.reading_request}
      - {id: 48f7e06c-a65d-618d-8876-a6a530d8e964, label: Sending reply, \n\
          aggregation: average, field: apache.status.scoreboard.sending_reply}
      - {id: 739f03ed-239c-3552-f94e-ffcaed2292b1, label: Starting up, \n\
          aggregation: average, field: apache.status.scoreboard.starting_up}
      - {id: f5945c27-6f19-5e58-6004-a5204aadba74, label: Total, aggregation: \n\
          average, field: apache.status.scoreboard.total}
      - {id: f5e6c708-9039-a605-74d7-21c2f79f30e2, label: Waiting for connection,
        aggregation: average, field: \n\
          apache.status.scoreboard.waiting_for_connection}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: 89879482-c9df-afd0-f2e4-0f6e95414cb5
      legend: {visible: show, width: extra_large, show_single_series: true, \n\
          truncate_labels: 0}
      type: line
      appearance:
        y_left_axis: {title: Count}
        missing_values: linear
        show_as_dotted: true
  - id: 44d1c271-bc9a-41a8-b30c-ca8b04f04277
    title: Total connections [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 37}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: ca70564f-f304-1d14-d521-cf5e8d4bfef0, label: Total, aggregation: \n\
          max, field: apache.status.connections.total}
      id: fc5ebf77-4bca-ba59-5d27-ba44c107ba11
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Connections}
        missing_values: linear
  - id: 7f45f1dc-cc1c-42a6-a691-a1a602ace63c
    title: Bytes per sec [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 22}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: f5a8af46-8adf-6c21-7a2a-3b5e99601572, label: Bytes per sec, \n\
          aggregation: average, field: apache.status.bytes_per_sec}
      id: a9ee0679-bf85-6bd2-1361-22071c6c3dd1
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Bytes per sec}
        missing_values: linear
  - id: 58f100e1-c5f9-4843-9bdf-a7ae9061ca20
    title: Workers [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 7}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 56fb37bf-ba98-9f61-fd55-abd62d91abf3, label: Busy workers, \n\
          aggregation: average, field: apache.status.workers.busy}
      - {id: cd81b842-c71b-fc3d-8a05-ccb62b1a508e, label: Idle workers, \n\
          aggregation: average, field: apache.status.workers.idle}
      id: 3da7285a-6c18-ef55-995b-7f237a879e0f
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Workers}
        missing_values: linear
  - id: de79f71b-cc47-40e7-b958-63d87a14fa97
    title: Connections [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 37}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: cb9b1a8a-369d-fb4d-b164-cf494238f345, label: Writing, aggregation: \n\
          max, field: apache.status.connections.async.writing}
      - {id: fe37b92a-9203-5cc5-b4a4-108e4c532052, label: Keep alive, \n\
          aggregation: max, field: apache.status.connections.async.keep_alive}
      - {id: d2302f47-c20e-948f-d1a4-45b4e2d710ce, label: Closing, aggregation: \n\
          max, field: apache.status.connections.async.closing}
      id: dcfa4cb9-1f71-c16d-df50-d85d22b1c293
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Connections}
        missing_values: linear
  - id: a855f0c8-cac9-4ebe-bce1-91fff3c18668
    title: Average server load [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 52}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 2d8eb50a-79c8-d7a8-59f2-7f5c73037dfb, label: Load per 1 min, \n\
          aggregation: average, field: apache.status.load.1}
      - {id: e06f3139-c859-d085-81a9-ccf153227a45, label: Load per 5 min, \n\
          aggregation: average, field: apache.status.load.5}
      - {id: fc05a8f0-f16c-30ca-5d96-d82976b2b2e4, label: Load per 15 min, \n\
          aggregation: average, field: apache.status.load.15}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: 4d99c97f-86e9-a09b-38ee-ff495b513af9
      legend: {visible: show, width: extra_large, truncate_labels: 0}
      type: line
      appearance:
        y_left_axis: {title: Count}
        missing_values: linear
        show_as_dotted: true
  - id: 908bb0f9-4d98-469d-9351-424a5196803f
    title: CPU usage [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 52}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 79753695-025e-6514-8d80-24b0694d7a1c, label: CPU load, aggregation: \n\
          average, field: apache.status.cpu.load}
      - {id: f825ed16-57aa-f482-41f4-4b7c09c1329e, label: CPU user, aggregation: \n\
          average, field: apache.status.cpu.user}
      - {id: 37d9b62d-6b15-512d-df3e-10826ce5346a, label: CPU system, \n\
          aggregation: average, field: apache.status.cpu.system}
      - {id: 25f43d03-76bd-bbda-737a-5e6738142f4e, label: CPU children user, \n\
          aggregation: average, field: apache.status.cpu.children_user}
      - {id: b155ec09-757f-9488-f529-f3ee676ca507, label: CPU children system, \n\
          aggregation: average, field: apache.status.cpu.children_system}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: cc954e7d-56b9-8bb8-c86d-0de3ca47033e
      legend: {visible: show, width: extra_large, truncate_labels: 0}
      type: line
      appearance:
        y_left_axis: {title: Count}
        missing_values: linear
        show_as_dotted: true
""")
