"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/activemq/kibana/dashboard/activemq-8a0cbc90-f916-11ec-9736-016ee09668f5.json`."""
    assert integrations_yaml_for('packages/activemq/kibana/dashboard/activemq-8a0cbc90-f916-11ec-9736-016ee09668f5.json') == snapshot("""\
dashboards:
- name: '[Metrics ActiveMQ] Broker'
  id: activemq-8a0cbc90-f916-11ec-9736-016ee09668f5
  description: The dashboard presents metric data describing ActiveMQ broker. \n\
    Metrics show statistics of enqueued and dequeued messages, consumers, \n\
    producers and memory usage (broker, store, temp).
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: activemq.broker}
  panels:
  - id: 0bb4a077-65fc-4d3a-a6e6-39a7ec01e01f
    title: Broker Messages [Metrics ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 90aa54b0-7456-147a-4dcb-fe7cd36a851e, label: Maximum of \n\
          activemq.broker.messages.dequeue.count, aggregation: max, field: \n\
          activemq.broker.messages.dequeue.count}
      - {id: 046be75c-f3bd-4433-04c2-e1bd4eed63cc, label: Maximum of \n\
          activemq.broker.messages.enqueue.count, aggregation: max, field: \n\
          activemq.broker.messages.enqueue.count}
      - {id: 046be75c-f3bd-4433-04c2-e1bd4eed63cc, label: Maximum of \n\
          activemq.broker.messages.enqueue.count, aggregation: max, field: \n\
          activemq.broker.messages.enqueue.count}
      id: ecb853cd-4d39-fc01-5c43-9aaf3bdb4937
      legend: {visible: show, position: bottom, show_single_series: true}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 9719ed38-5a0d-4132-b504-1bae29b20369
    title: Broker Consumers/Producers [Metrics ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 24, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: f1d58744-ac02-7dba-68a5-0f6765f114ff, label: Producers, aggregation: \n\
          max, field: activemq.broker.producers.count}
      - {id: a8028813-78d9-64ea-0d5a-379279dd848a, label: Consumers, aggregation: \n\
          max, field: activemq.broker.consumers.count}
      id: 9abc42af-3ca4-38d7-26ae-bd591af09e3e
      legend: {visible: show, position: bottom, show_single_series: true}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 7f00478e-0bf9-409c-89b7-2fc3f4ee50a9
    title: Broker Connections [Metrics ActiveMQ]
    size: {w: 24, h: 18}
    position: {x: 0, y: 15}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 3bb3c5bc-7544-c831-a70a-2fecd9b30ed4, label: Maximum of \n\
          activemq.broker.connections.count, aggregation: max, field: \n\
          activemq.broker.connections.count}
      id: 811e751b-38c8-82e9-71da-09fcd7fe9a23
      legend: {visible: show, position: bottom, show_single_series: true}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: b82bc348-18ce-4a6c-8d6d-4e90340f1690
    title: Broker Memory Usage [Metrics ActiveMQ]
    size: {w: 24, h: 6}
    position: {x: 24, y: 15}
    lens:
      type: gauge
      appearance: {ticks_position: bands}
      id: 2d75fa88-b0bc-f268-5ee4-a552cc075ceb
      data_view: metrics-*
      metric:
        id: ab2845d5-f80c-59b3-000f-4656370799ac
        label: Broker Memory
        format: {type: percent, decimals: 2}
        aggregation: max
        field: activemq.broker.memory.broker.pct
  - id: 3716faab-9aeb-4431-8fab-0fed419689f5
    title: Broker Store Memory Usage [Metrics ActiveMQ]
    size: {w: 24, h: 6}
    position: {x: 24, y: 21}
    lens:
      type: gauge
      appearance: {ticks_position: bands}
      id: f0f726b7-192e-0080-2160-4163ca54b745
      data_view: metrics-*
      metric:
        id: d3546dfc-b2ce-b4fb-6924-3f69aff8a86f
        label: Store Memory
        format: {type: percent, decimals: 2}
        aggregation: max
        field: activemq.broker.memory.store.pct
  - id: c20b98fb-92f8-4933-ac32-18119552b57a
    title: Broker Temp Memory Usage [Metrics ActiveMQ]
    size: {w: 24, h: 6}
    position: {x: 24, y: 27}
    lens:
      type: gauge
      appearance: {ticks_position: bands}
      id: a8027a65-d8e4-752a-fe95-6d6c17521bcc
      data_view: metrics-*
      metric:
        id: d2a399b3-0d58-d676-8293-98d5e27d90f5
        label: Temp Memory
        format: {type: percent, decimals: 2}
        aggregation: max
        field: activemq.broker.memory.temp.pct
""")
