"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/apache_spark/kibana/dashboard/apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156.json`."""
    assert integrations_yaml_for(
        'packages/apache_spark/kibana/dashboard/apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156.json'
    ) == snapshot("""\
dashboards:
- name: '[Metrics Apache Spark] Overview'
  id: apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [apache_spark.driver, apache_spark.executor, apache_spark.node, \n\
        apache_spark.application]
  panels:
  - id: a3339a86-6f2b-4f1a-85b8-4619c417a110
    title: Memory usage over time [Metrics Apache Spark]
    size: {w: 24, h: 17}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 1a54dd5d-a969-d5ce-4213-892431969123, label: Memory, aggregation: \n\
          last_value, field: apache_spark.driver.memory.used}
      id: 1ac511bc-4ed9-6cae-500a-13ce5dfafa55
      legend: {visible: show, position: top, show_single_series: true}
      type: bar
      appearance:
        x_axis: {title: Timestamp}
        y_left_axis: {title: Memory}
      mode: stacked
  - id: 2943002d-504e-4a30-a581-cd92fd621fe1
    title: Number of stages completed [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 24, y: 0}
    lens:
      id: f1623b37-00ca-b828-895d-1b01da0678ef
      type: metric
      data_view: metrics-*
      primary: {id: 12ae267e-6f3b-468f-347a-fff2c1606c72, label: Number of \n\
          Stages Completed, aggregation: last_value, field: \n\
          apache_spark.driver.stages.completed_count}
  - id: 784e4a18-20e7-48ef-8737-3a8a4643c4fe
    title: Number of stages skipped [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 32, y: 0}
    lens:
      id: ee79c08d-28ba-5a87-dee3-2c63e508d783
      type: metric
      data_view: metrics-*
      primary: {id: c3f30df0-0d28-fe44-37ef-5d436370fa08, label: Number of \n\
          Stages Skipped, aggregation: last_value, field: \n\
          apache_spark.driver.stages.skipped_count}
  - id: 19bd059b-ca79-4fb0-b450-f8adeb8acc8f
    title: Number of failed stages [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 40, y: 0}
    lens:
      id: 728b902b-3e3e-e9e1-c4ca-b9a79fd13b40
      type: metric
      data_view: metrics-*
      primary: {id: f80df669-bb9f-53c9-1132-fb4842037f5f, label: Number of \n\
          Stages Failed, aggregation: last_value, field: \n\
          apache_spark.driver.stages.failed_count}
  - id: f84a1cd9-1b4b-484e-87f7-953c2f645570
    title: Number of Tasks over time [Metrics Apache Spark]
    size: {w: 24, h: 17}
    position: {x: 24, y: 6}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 18444f3d-68cc-046a-a78e-aeb4e36ff26a, label: Failed, aggregation: \n\
          max, field: apache_spark.driver.tasks.failed}
      - {id: c3df3636-9c49-71e1-da25-323692093d22, label: Skipped, aggregation: \n\
          max, field: apache_spark.driver.tasks.skipped}
      - {id: 81c00cab-5bda-dcdf-b198-696a99109d5c, label: Completed, aggregation: \n\
          max, field: apache_spark.driver.tasks.completed}
      id: b61fab9a-ecd0-48a6-5590-53552d48eb07
      legend: {visible: show, position: top, show_single_series: true}
      type: area
      appearance:
        x_axis: {title: Timestamp}
        y_left_axis: {title: Tasks}
        missing_values: linear
      mode: stacked
  - id: 64cbf207-795a-4818-915c-137eaebc6198
    title: Maximum amount of memory available for storage [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 0, y: 17}
    lens:
      id: 3fa4fe7e-45f4-3d86-0d75-1d2b42531415
      type: metric
      data_view: metrics-*
      primary: {id: 42ffb9f2-13de-6a37-672c-bfdb788d7282, label: Max Memory (MB),
        aggregation: last_value, field: apache_spark.driver.memory.max_mem}
  - id: 62c6f93e-b6c1-4004-b780-535ed730ebaa
    title: Number of jobs failed [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 8, y: 17}
    lens:
      id: 506f906a-5a47-089b-ce48-d53fc518f8f7
      type: metric
      data_view: metrics-*
      primary: {id: 72bd30ea-2107-93a4-a18c-0965b1914815, label: Failed Jobs, \n\
          aggregation: last_value, field: apache_spark.driver.jobs.failed}
  - id: bb9eb57d-fbf2-41a4-8187-5cead0c80faa
    title: Number of Succeeded jobs [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 16, y: 17}
    lens:
      id: 92cbd651-6968-11da-15c0-2db61b29ef72
      type: metric
      data_view: metrics-*
      primary: {id: 35193231-73bb-3639-25ca-b579f8f2e905, label: Succeeded Jobs, \n\
          aggregation: last_value, field: apache_spark.driver.jobs.succeeded}
  - id: b5caa5d1-221e-400d-a11a-ea539f1f4546
    title: Number of Threadpool tasks over time [Metrics Apache Spark]
    size: {w: 26, h: 13}
    position: {x: 0, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 5a731654-572a-2926-1618-5e23b60af9c8, label: Completed, aggregation: \n\
          max, field: apache_spark.executor.threadpool.complete_tasks}
      - {id: feda6127-29d3-28e6-5e66-1fef23285e53, label: Active, aggregation: \n\
          max, field: apache_spark.executor.threadpool.active_tasks}
      - {id: 6382d955-3cd5-6a7a-c570-508dc2a93726, label: Started, aggregation: \n\
          max, field: apache_spark.executor.threadpool.started_tasks}
      id: 669d64ce-5a60-b85a-0817-ad3bfdd7c512
      legend: {visible: show, position: top, show_single_series: true}
      type: area
      appearance:
        x_axis: {title: Timestamp}
        y_left_axis: {title: Threadpool Tasks}
        missing_values: linear
      mode: stacked
  - id: 7a729bca-db45-4ffe-b1bf-51fdc30e3b18
    title: ''
    hide_title: true
    size: {w: 8, h: 5}
    position: {x: 26, y: 23}
    lens:
      id: c10ae0f8-1336-018c-6b37-003f77f2f0dc
      type: metric
      data_view: metrics-*
      primary:
        id: b8eac41f-d6ff-24a2-bfa5-f03aa63881da
        label: Bytes Read
        format: {type: bytes, decimals: 2}
        aggregation: last_value
        field: apache_spark.executor.bytes.read
  - id: 0595e44f-e6b0-4d93-868f-040f2eb0de31
    title: ''
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 34, y: 23}
    lens:
      id: cdf509ba-1fdf-cb28-b153-f6f8bb5acd78
      type: metric
      data_view: metrics-*
      primary:
        id: f2f2cdbe-3bba-a953-5190-9632763d5fbe
        label: Bytes Written
        format: {type: bytes, decimals: 2}
        aggregation: last_value
        field: apache_spark.executor.bytes.written
  - id: ab8c87f3-ec56-4ddc-b0b0-7bb8a21366c2
    title: Number of Applications waiting [Metrics Apache Spark]
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 41, y: 23}
    lens:
      id: f72b49e1-d6ad-b7af-af5a-2d0151f7ee29
      type: metric
      data_view: metrics-*
      primary: {id: c991b463-7f1f-f067-36b3-e1e1c1eafc6e, label: Waiting \n\
          Applications, aggregation: last_value, field: \n\
          apache_spark.node.main.applications.waiting}
  - id: 75c23769-a2bd-4825-b20a-d140aeb36175
    title: Number of Records Read [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 5}
    position: {x: 26, y: 28}
    lens:
      id: 95f31d30-ef5a-366c-ba03-c5fb8592b7cb
      type: metric
      data_view: metrics-*
      primary: {id: 9147aade-65b8-d845-b936-ccf0480a2118, label: Records Read, \n\
          aggregation: last_value, field: apache_spark.executor.records.read}
  - id: ab9316b5-5728-4b03-aadb-a93e22da9257
    title: Number of Records Written [Metrics Apache Spark]
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 34, y: 28}
    lens:
      id: f67d6ae9-9836-c3b0-ae66-2402e1afba51
      type: metric
      data_view: metrics-*
      primary: {id: e3096189-d04a-c527-7bff-a46de39bdb59, label: Records Written,
        aggregation: last_value, field: apache_spark.executor.records.written}
  - id: ab2aa190-2b49-4ec6-9479-ad4a4ade95ad
    title: Total number of Applications [Metrics Apache Spark]
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 41, y: 28}
    lens:
      id: fe53dcfd-cff1-04f2-a713-98ea7ea6a073
      type: metric
      data_view: metrics-*
      primary: {id: 81aa9980-5075-3ae2-fbd8-171b8ae9ba11, label: Total \n\
          Applications, aggregation: last_value, field: \n\
          apache_spark.node.main.applications.count}
  - id: cfbdf185-1437-478f-a856-eedbe62d1de2
    title: Number of Workers Alive [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 26, y: 33}
    lens:
      id: 3555b769-c9f2-dbef-778a-41b2c910cbf0
      type: metric
      data_view: metrics-*
      primary: {id: 34a76bc2-bcb5-e506-80d2-c745f7c9a313, label: Workers Alive, \n\
          aggregation: last_value, field: apache_spark.node.main.workers.alive}
  - id: 78e81e12-c659-4d89-a80d-14ec4e49368a
    title: Application Source Status [Metrics Apache Spark]
    size: {w: 14, h: 12}
    position: {x: 34, y: 33}
    lens:
      id: ade884fd-bcbc-b85c-f327-ea048e60555e
      type: pie
      appearance:
        donut: medium
        values: {format: hide}
      legend: {visible: show}
      data_view: metrics-*
      metrics:
      - {id: 8419b0f5-d93e-229b-78df-1ba30cdd0a05, label: Application Name, \n\
          aggregation: unique_count, field: apache_spark.application.name}
      breakdowns:
      - {id: 6a815d04-365d-75d8-a2bf-9810bf0f3f56, type: values, size: 5, field: \n\
          apache_spark.application.status}
  - id: fa3bca1d-df9c-4e2b-8785-cfe9211a7843
    title: Number of Cores used [Metrics Apache Spark]
    hide_title: true
    size: {w: 13, h: 9}
    position: {x: 0, y: 36}
    lens:
      id: 515fffaf-9d04-caad-75aa-f91b14489999
      type: metric
      data_view: metrics-*
      primary: {id: 7f527134-c934-5889-e48d-d344f8ee4050, label: Number of Cores
          Used, aggregation: last_value, field: \n\
          apache_spark.node.worker.cores.used}
  - id: 18c0d3d3-912f-42e4-a322-a5fcaa9002b0
    title: Memory Used [Metrics Apache Spark]
    hide_title: true
    size: {w: 13, h: 9}
    position: {x: 13, y: 36}
    lens:
      id: 9df1121d-0f58-d173-8ada-204a85982939
      type: metric
      data_view: metrics-*
      primary: {id: a7d99814-449a-c718-7a61-d57c7430a625, label: Memory Used \n\
          (MB), aggregation: last_value, field: \n\
          apache_spark.node.worker.memory.used}
  - id: 54e6714e-c9b2-4e0b-85f4-500ca898eb4d
    title: Total Workers [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 26, y: 39}
    lens:
      id: 46f73568-3fc3-3449-c826-38fa3d5eb033
      type: metric
      data_view: metrics-*
      primary: {id: b368cd2d-f33a-43a7-f042-616d1d4bd993, label: Total Workers, \n\
          aggregation: last_value, field: apache_spark.node.main.workers.count}
""")
