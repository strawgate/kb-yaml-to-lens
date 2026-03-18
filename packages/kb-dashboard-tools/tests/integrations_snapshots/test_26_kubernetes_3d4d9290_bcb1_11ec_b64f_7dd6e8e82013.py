"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json`."""
    assert integrations_yaml_for('packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json') == snapshot("""\
dashboards:
- name: '[Metrics Kubernetes] Pods'
  id: kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013
  description: Metrics about Pods
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: f992c139-e52a-09be-55ae-0c599b288c7a
    label: Cluster Name
    type: options
    field: orchestrator.cluster.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: aa9b8e58-ee0f-cecb-5d96-5173d12d6d6a
    label: Namespace Name
    type: options
    field: kubernetes.namespace
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: e26f06c6-cfa3-00d2-d82d-7c25ee6e7d30
    label: Pod Name
    type: options
    field: kubernetes.pod.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: c0a8dc23-df25-4618-8603-15b76ee0ae86
    title: Kubernetes Dashboards [Metrics Kubernetes]
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: '[Kubernetes Overview](#/view/kubernetes-f4dc26db-1b53-4ea2-a78b-1bfab8ea267c),
        [Kubernetes Nodes](#/view/kubernetes-b945b7b0-bcb1-11ec-b64f-7dd6e8e82013),
        [Kubernetes Pods](#/view/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013),  [Kubernetes
        Deployments](#/view/kubernetes-5be46210-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        StatefulSets](#/view/kubernetes-21694370-bcb2-11ec-b64f-7dd6e8e82013),  [Kubernetes
        DaemonSets](#/view/kubernetes-85879010-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        CronJobs](#/view/kubernetes-0a672d50-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        Jobs](#/view/kubernetes-9bf990a0-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        Volumes](#/view/kubernetes-3912d9a0-bcb2-11ec-b64f-7dd6e8e82013), [Kubernetes
        PV/PVC](#/view/kubernetes-dd081350-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        Services](#/view/kubernetes-ff1b3850-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        API Server](#/view/kubernetes-d3bd9650-0c14-11ed-b760-5d1bccb47f56)', \n\
        font_size: 10, links_in_new_tab: false}
  - id: c077515d-1668-487f-9942-2448a0c25e70
    title: Status per Pod [Metrics Kubernetes]
    size: {w: 48, h: 15}
    position: {x: 0, y: 4}
    lens:
      type: datatable
      appearance: {row_height: auto, header_row_height: single, \n\
          header_row_height_lines: 1, density: normal}
      paging: {enabled: true, page_size: 10}
      id: 9c9f9cf0-1bdf-ec1f-2b3b-d54df09c5848
      data_view: metrics-*
      metrics:
      - id: 0179ab06-e0af-bbe4-5b22-fe4dfbc1b209
        label: Phase
        filter: {kql: 'kubernetes.pod.status.phase: *'}
        aggregation: last_value
        field: kubernetes.pod.status.phase
      - id: 90ac78d9-ba09-1fd7-0312-1e73917829ed
        label: Ready
        filter: {kql: 'kubernetes.pod.status.ready: *'}
        aggregation: last_value
        field: kubernetes.pod.status.ready
      - id: 090e75fd-f7cc-a5d1-da29-a84b5c6efc1e
        label: Scheduled
        filter: {kql: 'kubernetes.pod.status.scheduled: *'}
        aggregation: last_value
        field: kubernetes.pod.status.scheduled
      breakdowns:
      - {id: b438d745-cf29-3a05-f104-ba7988a77c5a, type: values, size: 1000, \n\
          field: kubernetes.pod.name}
  - id: 23852bac-d857-4a32-95f3-8100d6abd976
    title: CPU Usage as Pct of the Total Node CPU [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 19}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 85ac8c09-a57a-b784-a69e-2e36358fc6be
        label: CPU Usage
        format: {type: percent, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: average
        field: kubernetes.pod.cpu.usage.node.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: d5f69190-d095-d772-3801-b916647eda20
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 9567b72e-6e79-479b-a5b1-1d9f81d258bd
    title: CPU Usage as Pct of the Defined Pod Limit [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 24, y: 19}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 7ed7789e-a47b-45be-843a-2a230b8e0d99
        label: CPU Usage
        format: {type: percent, decimals: 2}
        aggregation: average
        field: kubernetes.pod.cpu.usage.limit.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: 0fc9b6d5-427e-f5e2-ec3c-77c198bebd6e
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 6b939075-346d-4aa1-b634-bf57b8cc1532
    title: Memory Usage as Pct of the Total Node Memory [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 34}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 95e57d73-0b62-bc82-0755-c9f1c4b3f0c6
        label: Memory Usage
        format: {type: percent, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: average
        field: kubernetes.pod.memory.usage.node.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: d6cc9df9-bea7-9c63-c6ff-27b458c2f8b4
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 54bfc973-09ca-4ebe-a777-c790087c3a91
    title: Memory Usage as Pct of the Defined Pod Limit [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 24, y: 34}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: e313a86f-c819-7ec6-42b9-85bc4d7b7eb1
        label: Memory Usage
        format: {type: percent, decimals: 2}
        aggregation: average
        field: kubernetes.pod.memory.usage.limit.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: a70eccd1-b3e4-8dae-07ef-133f8f90d191
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 6459a5c9-80c5-46d8-968f-5b0a40b2eee0
    title: Working Set Memory Usage as Pct of the Defined Pod Limit [Metrics \n\
      Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 49}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 2398ea7a-eaf2-24cd-edaf-7da2382d04c4
        label: Memory Usage
        format: {type: percent, decimals: 2}
        aggregation: average
        field: kubernetes.pod.memory.working_set.limit.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: e93febb2-216b-c2ae-0cb0-28aac27787b1
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 06ded777-f88c-40c8-93fa-1f0ed71ed43a
    title: Network Outgoing Bytes per Pod [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 24, y: 49}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: b942c2f5-1abc-49f5-025b-573c822206ff
        label: Network Usage
        format: {type: bytes, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: last_value
        field: kubernetes.pod.network.tx.bytes
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: fbe2d09f-eb69-ceeb-9493-f856e43fa055
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 83f2689a-838b-4d73-8d92-8dd358c33329
    title: Network Incoming Bytes per Pod [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 64}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 6a8cd549-4911-a234-a683-af180bae572b
        label: Network Usage
        format: {type: bytes, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: last_value
        field: kubernetes.pod.network.rx.bytes
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: 669a7ae0-73ae-ad6a-39b9-0a89ed9ab15c
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
""")
