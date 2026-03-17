"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/apache_otel/kibana/dashboard/apache_otel-overview.json`."""
    assert integrations_yaml_for('packages/apache_otel/kibana/dashboard/apache_otel-overview.json') == snapshot("""\
dashboards:
- name: '[Apache OTel] Overview'
  id: apache_otel-overview
  description: Overview of Apache HTTP Server health and performance from \n\
    OpenTelemetry metrics.
  time_range: {from: now-1h, to: now}
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: apachereceiver.otel}
  controls:
  - id: 9ee7a268-5cc6-b546-db6e-96929c9a955b
    label: Server name
    type: options
    field: resource.attributes.apache.server.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: a18657f3-9386-7419-0c1e-db380f1b3b06
    label: Host
    type: options
    field: resource.attributes.host.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 887981e6-1ee5-4087-096b-af81cff49944
    title: ''
    hide_title: true
    size: {w: 16, h: 12}
    position: {x: 0, y: 0}
    markdown: {content: "## [Apache OTel] Overview\\n\\nThis dashboard provides an overview
        of Apache HTTP Server health and performance via OpenTelemetry metrics:\\n\\
        - Request rate and traffic throughput\\n- Worker pool utilization (busy vs
        idle)\\n- Active and asynchronous connection counts\\n- Server load averages
        (1m, 5m, 15m)\\n- CPU load and CPU time breakdown by mode\\n", font_size: \n\
        12, links_in_new_tab: false}
  - id: f1e0d86e-84d4-93fe-5f7b-bef3ab9bdfa0
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 16, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.uptime IS NOT NULL\\n\\
        | STATS uptime_sec = MAX(LAST_OVER_TIME(apache.uptime))"
      time_field: '@timestamp'
      id: 90b82132-fb95-b61d-b25b-6b3a956ce5eb
      type: metric
      primary: {id: 44133068-323b-27ee-8a35-ea6eebf2ccb7, field: uptime_sec, \n\
          label: Uptime}
  - id: e520f2f7-162a-8ae2-3c9d-4fe5cd5508d9
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 24, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.requests IS NOT NULL\\n\\
        | STATS request_rate = SUM(RATE(apache.requests))"
      time_field: '@timestamp'
      id: db068471-9f05-5d3f-b158-d86dcc864f46
      type: metric
      primary: {id: f691e6c3-1940-ecdf-ae31-22236c2ed15c, field: request_rate, \n\
          label: Request Rate}
  - id: 81c12fbb-84e1-8af8-787e-7f8943490b9c
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 32, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.traffic IS NOT NULL\\n\\
        | STATS traffic_rate = SUM(RATE(apache.traffic))"
      time_field: '@timestamp'
      id: 7aeafe3b-f369-eda5-460e-e5e53785bd91
      type: metric
      primary: {id: 7fdc8059-0203-19b4-0ccf-4ca2acae8937, field: traffic_rate, \n\
          label: Traffic Rate}
  - id: ac7d975a-8037-c750-c277-27b39069530a
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 40, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.cpu.load IS NOT NULL\\n\\
        | STATS cpu_load = MAX(AVG_OVER_TIME(apache.cpu.load))"
      time_field: '@timestamp'
      id: 24978926-fa37-f2b2-dacf-9db16feb3b04
      type: metric
      primary: {id: f785719f-38a0-74e3-8cb4-644a0cfeb76e, field: cpu_load, label: \n\
          CPU Load}
  - id: 2e15537b-ed9c-bf4c-8f36-c383700afb65
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 16, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.current_connections
        IS NOT NULL\\n| STATS connections = MAX(LAST_OVER_TIME(apache.current_connections))"
      time_field: '@timestamp'
      id: 471e31b4-4a2a-3aeb-c11d-1a753aae5a0a
      type: metric
      primary: {id: a6d083cf-a04d-f4c1-17f9-781c30adb518, field: connections, \n\
          label: Active Connections}
  - id: 8c951b8b-02a8-fc7d-6960-273855fb0feb
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 24, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.workers IS NOT NULL
        AND attributes.state == \\"busy\\"\\n| STATS busy = MAX(LAST_OVER_TIME(apache.workers))"
      time_field: '@timestamp'
      id: 2d6dc306-bba4-3998-0e48-22e604615f9b
      type: metric
      primary: {id: ea066e13-d6ca-622e-8415-661dd57f65af, field: busy, label: \n\
          Busy Workers}
  - id: efdc2bf8-ae2d-b2e2-164c-cbff0bca4550
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 32, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.workers IS NOT NULL
        AND attributes.state == \\"idle\\"\\n| STATS idle = MAX(LAST_OVER_TIME(apache.workers))"
      time_field: '@timestamp'
      id: 158b44d3-5497-dd45-78bc-9094f10cc1d9
      type: metric
      primary: {id: fcedf5a1-dde1-e721-a0b1-dc298ae48674, field: idle, label: \n\
          Idle Workers}
  - id: cb8ead79-d8c5-13fa-1f94-520e63c21f06
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 40, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE `apache.load.1` IS NOT NULL\\n\\
        | STATS load_1m = MAX(AVG_OVER_TIME(`apache.load.1`))"
      time_field: '@timestamp'
      id: 115d9abc-72ea-3071-4ffe-243954e8f55a
      type: metric
      primary: {id: b0862e2f-b189-d0bb-fffc-38901971f703, field: load_1m, label: \n\
          Server Load (1m)}
  - id: efc3c390-5ded-e443-91d9-88410c2a103b
    title: ''
    hide_title: true
    size: {w: 48, h: 3}
    position: {x: 0, y: 12}
    markdown: {content: '## Traffic & Performance', font_size: 12, \n\
        links_in_new_tab: false}
  - id: 8359485a-f93f-f780-cc8b-d2316ce56e05
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 15}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.requests IS NOT NULL\\n\\
        | STATS request_rate = SUM(RATE(apache.requests)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend)\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: 20a5f645-16df-2295-5f8c-a639f8a0b834, field: request_rate, label: \n\
          Requests/sec}
      id: 34a18afa-b0ee-1117-a900-1668525d48b4
      type: line
  - id: 399a4d4b-22a8-537f-9a47-f9e6e51582e0
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 15}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.traffic IS NOT NULL\\n\\
        | STATS traffic_rate = SUM(RATE(apache.traffic)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend)\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: 1cffc5ee-5721-36ea-20a4-f375da433660, field: traffic_rate, label: \n\
          Bytes/sec}
      id: 1d2ecf37-e43a-fff0-d4b9-cf8320451f99
      type: line
  - id: f63c8a06-4917-e9eb-d460-342789708dbe
    title: ''
    hide_title: true
    size: {w: 48, h: 3}
    position: {x: 0, y: 27}
    markdown: {content: '## Workers & Connections', font_size: 12, \n\
        links_in_new_tab: false}
  - id: d4db9150-8807-90e5-632d-679e4b1129fe
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 30}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.workers IS NOT NULL\\n\\
        | STATS workers = MAX(LAST_OVER_TIME(apache.workers)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend), attributes.state\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: d792695a-ae0d-bfc2-f5fd-84f1919c72e4, field: workers, label: \n\
          Workers}
      breakdown: {id: 425bd375-1fdb-eef3-859e-fe6500560791, field: \n\
          attributes.state}
      id: 4345524e-523e-6c06-ab0d-bd1544843bd7
      type: area
      mode: stacked
  - id: 80006d9a-5de5-4b99-12ce-486e55a7d0ce
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 30}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.current_connections
        IS NOT NULL\\n| STATS connections = MAX(LAST_OVER_TIME(apache.current_connections))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend)\\n| SORT time_bucket
        ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: b4602782-87fb-a673-4fca-7574bd6340b5, field: connections, label: \n\
          Active Connections}
      id: 767699aa-7077-3ca1-7cd0-5b649ae5ecfc
      type: line
  - id: ff32905c-4ec6-d1bd-0bee-be75d4bca877
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 42}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.scoreboard IS NOT NULL\\n\\
        | STATS count = MAX(LAST_OVER_TIME(apache.scoreboard)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend), attributes.state\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: b07c5df4-6511-8380-b79d-e8622dd87569, field: count, label: Workers}
      breakdown: {id: 425bd375-1fdb-eef3-859e-fe6500560791, field: \n\
          attributes.state}
      id: 5a64a6d7-9074-a7c6-dc32-591c29c0e1f2
      type: bar
      mode: stacked
  - id: f04ea16d-49bf-689f-3dcf-43d35ccf3ca6
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 42}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.connections.async IS
        NOT NULL\\n| STATS connections = MAX(LAST_OVER_TIME(apache.connections.async))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend), attributes.connection_state\\n\\
        | SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: bf4dc9e5-57d7-18cb-47a1-9ec9265607d2, field: connections, label: \n\
          Connections}
      breakdown: {id: 154b1775-0ddc-a99c-002e-399606d8644b, field: \n\
          attributes.connection_state}
      id: e9b984cc-aa1d-8753-2abd-8a9776bea5c1
      type: area
      mode: stacked
  - id: 3613a751-e533-3134-cccd-cdb572c26b67
    title: ''
    hide_title: true
    size: {w: 48, h: 3}
    position: {x: 0, y: 54}
    markdown: {content: '## System Resources', font_size: 12, links_in_new_tab: \n\
        false}
  - id: f9e49625-213d-5db0-c983-de18f7dc82d9
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 57}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| FORK ( WHERE `apache.load.1` IS
        NOT NULL | STATS load = MAX(AVG_OVER_TIME(`apache.load.1`)) BY time_bucket
        = BUCKET(@timestamp, 20, ?_tstart, ?_tend) | EVAL period = \\"1 minute\\" )
        ( WHERE `apache.load.5` IS NOT NULL | STATS load = MAX(AVG_OVER_TIME(`apache.load.5`))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend) | EVAL period =
        \\"5 minutes\\" ) ( WHERE `apache.load.15` IS NOT NULL | STATS load = MAX(AVG_OVER_TIME(`apache.load.15`))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend) | EVAL period =
        \\"15 minutes\\" )\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: d0850dfa-7c38-ae70-cde6-58bd8bb16418, field: load, label: Load}
      breakdown: {id: 88724d8b-0208-c6bc-f465-65feba363b95, field: period}
      id: 76e16332-23ef-62ec-dfe4-1e5d5dbb3e25
      type: line
  - id: a9a36696-a097-1cd0-83af-34af4ad26fda
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 57}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.cpu.time IS NOT NULL\\n\\
        | STATS cpu_time_rate = SUM(RATE(apache.cpu.time)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend), attributes.mode\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: 87218855-948b-e42e-fc25-e1cd715ebca9, field: cpu_time_rate, label: \n\
          CPU jiffs/sec}
      breakdown: {id: d054a2a0-63c2-f3a0-6bd3-0f6d670141a3, field: \n\
          attributes.mode}
      id: dd4b99d3-4bce-f113-ad76-a143a555d682
      type: area
      mode: stacked
""")
