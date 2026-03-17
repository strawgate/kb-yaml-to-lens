"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/airflow/kibana/dashboard/airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b.json`."""
    assert integrations_yaml_for('packages/airflow/kibana/dashboard/airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b.json') == snapshot("""\
dashboards:
- name: '[Metrics Airflow] Overview'
  id: airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: airflow.statsd}
  controls:
  - id: e077536e-412b-783d-f0ce-528c5cb595f9
    label: host.hostname
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: f3313a2c-2e29-490e-b586-8d281a96faa4
    title: ''
    hide_title: true
    size: {w: 16, h: 11}
    position: {x: 0, y: 0}
    markdown: {content: "## Apache Airflow\\n\\nThis dashboard provides an overview
        of Apache Airflow performance and health, including Directed Acyclic Graph
        (DAG) run statuses, task execution times, and scheduling delays. Use it to
        monitor workflows, identify bottlenecks, and ensure smooth orchestration of
        data pipelines.", font_size: 12, links_in_new_tab: false}
  - id: 48c3b9c1-81aa-42ff-9572-669c9cf73728
    title: Scheduler heartbeat
    size: {w: 16, h: 11}
    position: {x: 16, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: dfa3d71f-88cc-eb74-70f7-5957db290514
        label: Hearbeats reported
        filter: {kql: '"airflow.scheduler_heartbeat.count": *'}
        aggregation: last_value
        field: airflow.scheduler_heartbeat.count
      id: fc08e1bf-4349-1da5-c007-fb108c7c56c1
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 45fc2d9e-d648-4ac4-b339-c013caad550b
    title: Scheduler tasks
    size: {w: 16, h: 11}
    position: {x: 32, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 3ba057ff-541f-46d4-b0a4-55823631880b
        label: Executable
        filter: {kql: '"airflow.task_executable.value": *'}
        aggregation: last_value
        field: airflow.task_executable.value
      - id: 0fb96067-0caf-95ee-3232-88fc0034b682
        label: Starving
        filter: {kql: '"airflow.task_starving.value": *'}
        aggregation: last_value
        field: airflow.task_starving.value
      id: da66f719-5d83-60bf-833d-ca97e5b6ee37
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Tasks}
      mode: stacked
  - id: ad7f08e5-4141-4c17-a619-8f7b370d1b78
    title: Mean DAG run schedule delay
    size: {w: 24, h: 15}
    position: {x: 0, y: 11}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 0e3e717a-5db2-f6ec-0268-4c905461ae63
        label: Mean delay
        format: {type: duration, decimals: 0, compact: true}
        filter: {kql: '"airflow.dag_schedule_delay.mean": *'}
        aggregation: last_value
        field: airflow.dag_schedule_delay.mean
      breakdown: {id: ed2ff3f5-ca41-eb1b-c4ff-c871637bb3a4, type: values, size: \n\
          5, field: airflow.dag_id}
      id: 041d8875-b01e-f64f-dbc0-58218093ae9d
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      mode: stacked
  - id: 4c9299a4-d135-4340-81f2-69da0e6602c8
    title: DAG bag size
    size: {w: 24, h: 15}
    position: {x: 24, y: 11}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 02519b17-0141-dfbb-3f09-034009a85593
        label: DAGs
        filter: {kql: '"airflow.dag_bag_size.value": *'}
        aggregation: last_value
        field: airflow.dag_bag_size.value
      id: 97dd1732-a6d4-caaf-ba38-ae1c95e71a1c
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 3eea737e-6f17-49f0-9c07-624055b9f41b
    title: Mean Successful DAG duration
    size: {w: 24, h: 15}
    position: {x: 0, y: 26}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 65204d5c-b2ce-904f-f943-0d2ca74b50d3
        label: Duration
        format: {type: duration, decimals: 1, compact: true}
        filter: {kql: '"airflow.success_dag_duration.mean": *'}
        aggregation: last_value
        field: airflow.success_dag_duration.mean
      breakdown: {id: ed2ff3f5-ca41-eb1b-c4ff-c871637bb3a4, type: values, size: \n\
          5, field: airflow.dag_id}
      id: edc5cd15-6de8-ad0c-da69-6ecae321c1cb
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      mode: stacked
  - id: 13a49310-419c-4666-9348-db529b9ed17b
    title: Mean Failed DAG duration
    size: {w: 24, h: 15}
    position: {x: 24, y: 26}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 4072bc17-aca6-7d26-8790-096c2f6ee837
        label: Duration
        format: {type: duration, decimals: 1, compact: true}
        filter: {kql: '"airflow.failed_dag_duration.mean": *'}
        aggregation: last_value
        field: airflow.failed_dag_duration.mean
      breakdown: {id: ed2ff3f5-ca41-eb1b-c4ff-c871637bb3a4, type: values, size: \n\
          5, field: airflow.dag_id}
      id: 5e6f85ee-9b0b-9585-de83-a2ebd34b4d9b
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      mode: stacked
  - id: e6c5b713-d20c-4ec1-9193-68caded2fc98
    title: DAG total parse time
    size: {w: 24, h: 15}
    position: {x: 0, y: 41}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 9276a7c0-89dc-ba0c-2ad1-a652d6d8a850
        label: DAG Total parse time
        format: {type: duration, decimals: 1, compact: true}
        filter: {kql: '"airflow.dag_total_parse_time.value": *'}
        aggregation: last_value
        field: airflow.dag_total_parse_time.value
      id: 5e0af697-9925-6231-ddfb-485ecc2e47cf
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Duration}
      mode: stacked
  - id: b65e9e91-49ee-4559-981c-c1cff459bb54
    title: DAG import errors
    size: {w: 24, h: 15}
    position: {x: 24, y: 41}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 63287037-d549-41e9-c231-edc99a541e8b
        label: Errors
        filter: {kql: '"airflow.dag_import_errors.value": *'}
        aggregation: last_value
        field: airflow.dag_import_errors.value
      id: cb895526-0e91-12ae-d91a-acb581cf8b0d
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: c18206fd-60a2-40be-bbb7-e0210b9be725
    title: Executor tasks
    size: {w: 24, h: 15}
    position: {x: 0, y: 56}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 4e589d4d-8809-4947-c5b4-f7c1a45d4d64
        label: Running
        filter: {kql: '"airflow.executor_running_tasks.value": *'}
        aggregation: last_value
        field: airflow.executor_running_tasks.value
      - id: b003343b-b68b-7f77-2e66-b4264ac8197f
        label: Queued
        filter: {kql: '"airflow.executor_queued_tasks.value": *'}
        aggregation: last_value
        field: airflow.executor_queued_tasks.value
      - id: 77310ce6-9cb1-436b-9a58-6cb3fff97956
        label: Open Slots
        filter: {kql: '"airflow.executor_open_slots.value": *'}
        aggregation: last_value
        field: airflow.executor_open_slots.value
      id: 969152c4-3545-9831-d783-55fb7ce185b3
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Tasks}
      mode: stacked
  - id: 04bbf1c9-724e-4f4b-a671-c0540e552d8d
    title: Pool task slots
    size: {w: 24, h: 15}
    position: {x: 24, y: 56}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 4cabc59c-f0a1-233b-0249-0d74642887cd
        label: Open
        filter: {kql: '"airflow.pool_open_slots.value": *'}
        aggregation: last_value
        field: airflow.pool_open_slots.value
      - id: de7b4d68-9eb0-04c5-1a64-b32d6a4106ee
        label: Queued
        filter: {kql: '"airflow.pool_queued_slots.value": *'}
        aggregation: last_value
        field: airflow.pool_queued_slots.value
      - id: b8b51524-4716-341c-4a05-23f5d8404b39
        label: Running
        filter: {kql: '"airflow.pool_running_slots.value": *'}
        aggregation: last_value
        field: airflow.pool_running_slots.value
      - id: 778dd06a-9137-4719-9b60-b8711db86e85
        label: Starving
        filter: {kql: '"airflow.pool_starving_tasks.value": *'}
        aggregation: last_value
        field: airflow.pool_starving_tasks.value
      breakdown: {id: e792cd4a-4e21-9df1-3726-8e09283027fe, type: values, size: \n\
          3, field: airflow.pool_name}
      id: 846c670c-6d7a-b4cc-d62c-a81aa6ff7ceb
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      appearance:
        y_left_axis: {title: Slots}
      mode: stacked
""")
