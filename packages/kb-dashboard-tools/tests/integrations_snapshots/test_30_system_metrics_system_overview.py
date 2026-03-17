"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/system/kibana/dashboard/system-Metrics-system-overview.json`."""
    assert integrations_yaml_for('packages/system/kibana/dashboard/system-Metrics-system-overview.json') == snapshot("""\
dashboards:
- name: '[Metrics System] Overview'
  id: system-Metrics-system-overview
  description: Overview of system metrics
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [system.process, system.fsstat, system.cpu, system.memory, \n\
        system.network]
  panels:
  - id: 471f7546-e704-4a38-a041-d8b11869d7cc
    title: System Navigation
    hide_title: true
    size: {w: 48, h: 5}
    position: {x: 0, y: 0}
    markdown: {content: "# System overview\\n\\nTo view host details, select a host
        from the list below by clicking the respective label.", font_size: 12, \n\
        links_in_new_tab: false}
  - id: aa7fddcf-8146-4d85-b3d7-d37a99a5ff32
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 0, y: 5}
    lens:
      id: 1e5b399d-681f-0b61-85cb-826bc084e826
      type: metric
      data_view: metrics-*
      primary:
        id: 49948a83-0e0b-fc06-d408-6408223553ba
        label: Memory used
        format: {type: percent, compact: true}
        filter: {kql: 'system.memory.actual.used.pct: *'}
        aggregation: last_value
        field: system.memory.actual.used.pct
  - id: 9fc7a050-de1b-495b-8ca7-2a852ed5a28c
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 9, y: 5}
    lens:
      id: 03e69969-5962-dc34-36ce-0f5fe61debe1
      type: metric
      data_view: metrics-*
      primary:
        id: 74e34c2f-6c02-b4b8-624d-0de03644791a
        label: CPU used
        format: {type: percent, compact: true}
        filter: {kql: 'system.cpu.total.norm.pct: *'}
        aggregation: last_value
        field: system.cpu.total.norm.pct
  - id: 234c40f8-f787-49a9-b1d3-1d3340e0ebaa
    title: Top Hosts by CPU
    hide_title: true
    size: {w: 30, h: 21}
    position: {x: 18, y: 5}
    lens:
      type: datatable
      id: 35965e26-8165-1adc-1618-16907eefc1f6
      data_view: TODO_data_view
      metrics:
      - id: 9bf8fdfb-d02e-0662-e44e-4e36a552ae99
        label: CPU usage
        format: {type: percent}
        filter: {kql: '"system.cpu.total.norm.pct": *'}
        aggregation: last_value
        field: system.cpu.total.norm.pct
      - id: 601d050d-9c29-eb5e-a631-5ae5a082877b
        label: Memory usage
        format: {type: percent}
        filter: {kql: '"system.memory.actual.used.pct": *'}
        aggregation: last_value
        field: system.memory.actual.used.pct
      breakdowns:
      - {id: ce2d4ae7-0c85-a2d6-f606-b1cd016bc589, type: values, size: 1000, \n\
          field: host.name}
  - id: f95d2a8f-0ec2-4252-b3e8-8771b9165241
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 0, y: 12}
    lens:
      id: 70dd394c-840e-735a-1813-a834e4841a23
      type: metric
      data_view: metrics-*
      primary: {id: b7966ae2-9ab7-5a96-b3aa-c7cf6f859afc, label: Hosts, formula: \n\
          unique_count(host.name)}
      secondary: {id: 1b2e0a6b-24c9-a866-7559-702820af3e8c, label: Part of Hosts,
        aggregation: unique_count, field: host.name}
  - id: 4a59a56e-e5fd-4ff3-b2f0-8a1c07be572b
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 9, y: 12}
    lens:
      id: 4c3f868b-b07f-9934-f672-8d945f6842ec
      type: metric
      data_view: metrics-*
      primary:
        id: a50f00c3-90b7-f788-d613-5bb0e6ee222b
        label: Disk used
        format: {type: percent, compact: true}
        formula: 'last_value(system.fsstat.total_size.used)/last_value(system.fsstat.total_size.total) '
      secondary:
        id: d9761885-2890-9c8f-814a-1564b66a9fb9
        label: Part of Disk used
        filter: {kql: '"system.fsstat.total_size.used": *'}
        aggregation: last_value
        field: system.fsstat.total_size.used
  - id: 4fdb14ab-c349-489b-afc1-55603ddb52f3
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 0, y: 19}
    lens:
      id: c95f2503-75ca-90d5-b31a-231b19c9a359
      type: metric
      data_view: metrics-*
      primary:
        id: ef238bd0-3843-eb3c-dcc4-a4510f88792a
        label: Inbound traffic per second
        format: {type: bytes, decimals: 2}
        formula: (max(system.network.in.bytes, reducedTimeRange='30s') - \n\
          min(system.network.in.bytes, reducedTimeRange='30s')) / 30
      secondary: {id: 4d71a8ea-5063-0095-d2db-2435f5e6bf45, label: Part of \n\
          Inbound Traffic per second, aggregation: max, field: \n\
          system.network.in.bytes}
  - id: fe4dd8cc-1c8d-4b88-8db3-4a286b33984f
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 9, y: 19}
    lens:
      id: 035c6a75-3c54-f2b8-e68d-4be7de591263
      type: metric
      data_view: metrics-*
      primary:
        id: acd50f90-caee-9706-98de-e4253ed6eef0
        label: Outbound traffic per second
        format: {type: bytes, decimals: 2}
        formula: (max(system.network.out.bytes, reducedTimeRange='30s') - \n\
          min(system.network.out.bytes, reducedTimeRange='30s')) / 30
      secondary: {id: f63a1eb6-47fa-eff6-c4bd-107179e2c576, label: Part of \n\
          Outbound Traffic per second, aggregation: max, field: \n\
          system.network.out.bytes}
  - id: e6f8fdab-5f7e-42b1-9093-36c017e0d26d
    title: Top hosts by CPU usage over time
    size: {w: 48, h: 15}
    position: {x: 0, y: 26}
    lens:
      type: heatmap
      id: 74a4b7a9-af0c-9d2d-3323-9ebcc92ad871
      data_view: metrics-*
      x_axis: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram, \n\
          field: '@timestamp'}
      y_axis: {id: 9e654e1c-02e0-7f4b-b5c0-93958e779b8f, type: values, size: 20, \n\
          field: host.name}
      metric:
        id: c7e21c64-ad6c-5791-5b06-80703124f1e3
        label: CPU Usage
        format: {type: percent, decimals: 0}
        aggregation: average
        field: system.cpu.user.norm.pct
  - id: e6f6cabf-ecec-482f-b7b5-634e323e9a15
    title: Top hosts by memory usage over time
    size: {w: 48, h: 16}
    position: {x: 0, y: 41}
    lens:
      type: heatmap
      id: 45c80a3b-eb7c-7fb0-9e12-6d4025f79ebd
      data_view: metrics-*
      x_axis: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram, \n\
          field: '@timestamp'}
      y_axis: {id: 9e654e1c-02e0-7f4b-b5c0-93958e779b8f, type: values, size: 20, \n\
          field: host.name}
      metric:
        id: d39c121c-1182-d4e8-cd09-89d74dc90d92
        label: Memory Usage
        format: {type: percent, decimals: 0}
        formula: average(system.memory.actual.used.pct)
""")
