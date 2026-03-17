"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json`."""
    assert integrations_yaml_for('packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json') == snapshot("""\
dashboards:
- name: '[Logs Apache] Access and error logs'
  id: apache-Logs-Apache-Dashboard
  description: Logs Apache integration dashboard
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [apache.access, apache.error]
  controls:
  - id: 7acd8a6f-d64f-22c6-b1ed-4fa6a18fd97c
    label: Hostname
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 665ee316-bf0f-4182-ab1b-2763a7fffc06
    title: Response codes over time [Logs Apache]
    size: {w: 32, h: 12}
    position: {x: 0, y: 45}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 1eed8a07-2b0b-c18b-dbb4-56b960301da2, type: values, size: \n\
          5, field: http.response.status_code}
      id: 36a3f3e1-ec27-a4c8-1cfa-d568ed431b2d
      legend: {visible: show, show_single_series: true}
      type: bar
      mode: stacked
  - id: 3f8742ea-3414-4259-99d3-83f02bedf868
    title: Operating systems breakdown [Logs Apache]
    size: {w: 16, h: 12}
    position: {x: 32, y: 45}
    lens:
      id: c1c94846-a23f-a236-968a-c21352aa2c11
      type: pie
      appearance: {donut: medium}
      legend: {visible: show}
      data_view: logs-*
      metrics:
      - {id: a2ec6baa-deb0-ed51-ea49-ecda62f4d18d, label: Unique count of \n\
          source.address, aggregation: unique_count, field: source.address}
      breakdowns:
      - {id: 9b452332-016c-bcaa-da7d-3a64576877e8, type: values, size: 5, field: \n\
          user_agent.os.name}
      - {id: d79d6a24-a93f-82d0-e626-686a13d42cfc, type: values, size: 5, field: \n\
          user_agent.os.version}
  - id: b95f2642-7f5e-4cfa-8c1a-ecccf384e840
    title: Top URLs by response code [Logs Apache]
    size: {w: 32, h: 12}
    position: {x: 0, y: 57}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: f180759b-b457-10f9-04cb-f0ee57f419c2
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 8b6266d7-9c02-52e0-f729-9b06c65b3530, type: values, size: 5, field: \n\
          http.response.status_code}
      - {id: 5e69f278-138f-664d-e8bb-1135746e09d1, type: values, size: 5, field: \n\
          url.original}
  - id: 1df4688c-8f4c-455f-a260-bb57e3445861
    title: Browsers breakdown [Logs Apache]
    size: {w: 16, h: 12}
    position: {x: 32, y: 57}
    lens:
      id: 45d02f70-2869-1c3a-cbc6-a21f6608f721
      type: pie
      appearance: {donut: medium}
      legend: {visible: show}
      data_view: logs-*
      metrics:
      - {id: a2ec6baa-deb0-ed51-ea49-ecda62f4d18d, label: Unique count of \n\
          source.address, aggregation: unique_count, field: source.address}
      breakdowns:
      - {id: d4851aa4-86e3-f23c-2c38-2eed2a74a815, type: values, size: 5, field: \n\
          user_agent.name}
      - {id: 9a18218e-26be-a284-a001-d72ea3c56daf, type: values, size: 5, field: \n\
          user_agent.version}
  - id: 4c8d6353-2787-475f-bd46-5b21239aa072
    title: Error logs over time [Logs Apache]
    size: {w: 48, h: 9}
    position: {x: 0, y: 69}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: cce5efe2-b956-597b-69f9-9a771b3a0b2a, type: values, size: \n\
          5, field: log.level}
      id: 0872f3f6-ec5d-4754-5a29-2a9231686cdc
      legend: {visible: show, show_single_series: true}
      type: bar
      mode: stacked
  - id: d9771ad7-cec0-4e4b-a51e-bbc880a8af0d
    title: Unique IPs map [Logs Apache]
    size: {w: 48, h: 15}
    position: {x: 0, y: 30}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: a39e73b9-4e6c-422e-a7bb-3dbbb53c7274
    title: Apache errors log [Logs Apache]
    size: {w: 48, h: 15}
    position: {x: 0, y: 93}
    search: {saved_search_id: TODO_saved_search_id}
""")
