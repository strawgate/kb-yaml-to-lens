"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json`."""
    assert integrations_yaml_for('packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json') == snapshot("""\
dashboards:
- name: '[Metrics Nginx] Overview'
  id: nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129
  description: Overview dashboard for the Nginx integration in Metrics
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: true}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: nginx.stubstatus}
  controls:
  - id: adc4ed90-888b-a0a5-f7bb-874592448bfa
    label: Nginx instance
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 634a8822-9fdf-4abd-a881-b22fa0a43883
    title: Total requests
    size: {w: 16, h: 10}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 815327a7-9499-b336-1de4-6e81839d589b, label: Total, aggregation: \n\
          max, field: nginx.stubstatus.requests}
      id: 15c2ccbd-b4ca-bcc0-3066-79cd638721aa
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Total}
        missing_values: linear
        show_as_dotted: true
  - id: 7feb4b0c-7f27-4f31-9745-e93376a773b5
    title: Processed requests
    size: {w: 16, h: 10}
    position: {x: 16, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 01ed5bb2-612f-f097-6988-29ecb3535f6d, label: Processed, aggregation: \n\
          max, field: nginx.stubstatus.handled}
      id: bbfe074b-7d12-2417-070c-d28d33e53c99
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance: {missing_values: linear, show_as_dotted: true}
  - id: 16841075-2904-4a7e-b305-988646a2e88a
    title: Heartbeat / Up
    size: {w: 16, h: 10}
    position: {x: 32, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 0abfce95-8220-354b-6220-7f92ef4e5f83, label: Up, aggregation: \n\
          unique_count, field: host.hostname}
      id: 52c615bd-917d-8ede-ad90-119f999ab953
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance: {missing_values: linear, show_as_dotted: true}
  - id: 45dee013-0721-4e1f-8d06-b8fb5e6ec462
    title: Active connections
    size: {w: 23, h: 13}
    position: {x: 0, y: 10}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: aee3ce5e-608c-d03c-a2e7-899c43fea927
        label: Active
        format: {type: number, decimals: 0}
        aggregation: average
        field: nginx.stubstatus.active
      id: e7cd0234-3e6d-155c-07a3-0c665c753489
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Active}
  - id: 194effcd-61a9-4239-8b53-9d8793cefde1
    title: Reading / Writing / Waiting Rates
    size: {w: 25, h: 13}
    position: {x: 23, y: 10}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: bc872dd7-fa35-1d39-3ccb-581b326711f1
        label: Reading
        format: {type: number, decimals: 1}
        aggregation: average
        field: nginx.stubstatus.reading
      - id: c82a421f-1b8a-52bc-510e-10734c630b25
        label: Writing
        format: {type: number, decimals: 1}
        aggregation: average
        field: nginx.stubstatus.writing
      - id: 2582d3cf-9c2b-9305-3812-c53e99b22605
        label: Waiting
        format: {type: number, decimals: 1}
        aggregation: average
        field: nginx.stubstatus.waiting
      id: 6394953b-a86d-5046-73af-52dd258d7c67
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
  - id: ffa68274-1f0b-468e-9ff5-f486a1501307
    title: Request Rate
    size: {w: 16, h: 12}
    position: {x: 0, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 1dda1d54-5b38-9be6-0e41-c6bb7c04a040, label: Maximum of \n\
          nginx.stubstatus.requests, aggregation: max, field: \n\
          nginx.stubstatus.requests}
      id: 241c67fe-1287-6b49-6440-75874416033f
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
  - id: 1711ea62-d9f5-418c-b244-81dc1832b9ef
    title: Accepts and Handled Rate
    size: {w: 16, h: 12}
    position: {x: 16, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: b83e05a4-3e1a-b372-ff61-7cae32f570e3, label: Maximum of \n\
          nginx.stubstatus.accepts, aggregation: max, field: \n\
          nginx.stubstatus.accepts}
      - {id: 8f41cf89-53b1-3479-5838-c69bd211b0a1, label: Maximum of \n\
          nginx.stubstatus.handled, aggregation: max, field: \n\
          nginx.stubstatus.handled}
      id: b714cdd1-b31a-7158-c8bb-60f3cacc047b
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
  - id: 8fd75d58-0b72-47f4-b500-d0091e60bf3e
    title: Drops Rate
    size: {w: 16, h: 12}
    position: {x: 32, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: e8c4132d-a05a-6f5d-472b-7d1217283b12, label: Maximum of \n\
          nginx.stubstatus.dropped, aggregation: max, field: \n\
          nginx.stubstatus.dropped}
      id: 7d1d37fb-546c-347e-87c1-f85339ecc467
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
""")
