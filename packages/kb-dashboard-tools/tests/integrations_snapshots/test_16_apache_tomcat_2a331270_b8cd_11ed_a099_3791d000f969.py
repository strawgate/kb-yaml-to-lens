"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/apache_tomcat/kibana/dashboard/apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969.json`."""
    assert integrations_yaml_for(
        'packages/apache_tomcat/kibana/dashboard/apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969.json'
    ) == snapshot("""\
dashboards:
- name: '[Metrics Apache Tomcat] Session'
  id: apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969
  description: This Apache Tomcat dashboard visualizes session data stream \n\
    metrics.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: apache_tomcat.session}
  controls:
  - id: 04c6559b-711b-5cd4-22e9-91f2c26da973
    label: Host Name
    type: options
    field: service.address
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: 482ce94f-ef28-d3f2-dec0-a672173c6f01
    label: Application Name
    type: options
    field: apache_tomcat.session.application_name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: a39adf70-8e40-4d80-a127-a1747a75be1f
    title: Created sessions over time [Metrics Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: cef84950-71d9-e11e-6aad-928834e010f2
        label: Created
        format: {type: number, decimals: 0}
        filter: {kql: 'apache_tomcat.session.create.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.create.total
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: 96abbff7-e5ce-37d1-f982-d6495ce96460
      legend: {visible: show, width: large}
      type: line
      appearance:
        y_left_axis: {title: Sessions}
  - id: 91d26f64-351f-420e-a37b-88a882ecba0e
    title: Expired sessions per application [Metrics Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 24, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 2b38d0cb-f503-a865-39a8-3750631d2c7d
        label: Expired
        format: {type: number, decimals: 0}
        filter: {kql: 'apache_tomcat.session.expire.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.expire.total
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: 6abc7ea5-cd47-57b2-056b-d419084740ce
      legend: {visible: show, width: large, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Sessions}
        values: {visible: true}
  - id: 5922510e-e6a2-4f9c-aceb-83715cc3b539
    title: Current active sessions over time [Metrics Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 0, y: 14}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 8ca54818-6d8a-e9e5-4f6f-27325d3c050a
        label: Current active
        format: {type: number, decimals: 0}
        filter: {kql: 'apache_tomcat.session.active.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.active.total
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: 3d7208fd-3115-498f-41ec-5b7fcfecca93
      legend: {visible: show}
      type: line
      appearance:
        y_left_axis: {title: Sessions}
  - id: 2d408e1c-da52-4aed-b760-812f89f48184
    title: Session expiration processing time [Metric Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 24, y: 14}
    lens:
      data_view: metrics-*
      dimension: {id: 60c5cd97-dac4-a4f9-f29e-20385961beea, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      metrics:
      - id: 2d84e1c1-8d7c-fa96-7ce2-9be39561172b
        label: Processing time(ms)
        filter: {kql: 'apache_tomcat.session.processing_time: *'}
        aggregation: last_value
        field: apache_tomcat.session.processing_time
      id: f82d4473-af05-84fd-bee4-ff53938aa474
      legend: {visible: show}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 8ce83532-0623-4974-9280-b6c56c6b0c27
    title: Sessions overview [Metrics Apache Tomcat]
    size: {w: 48, h: 15}
    position: {x: 0, y: 28}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: 69c706e4-2afb-5494-e7a3-b7030c4ace22
      data_view: metrics-*
      metrics:
      - id: 23c60d24-dbab-15d5-f3fa-c7f0a1e27e75
        label: Created
        filter: {kql: 'apache_tomcat.session.create.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.create.total
      - id: 6126988d-5f3e-750b-f4e1-d37980e33279
        label: Current active
        filter: {kql: 'apache_tomcat.session.active.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.active.total
      - id: 3f6193ef-9ebf-6b72-4e7e-3d63221f85b1
        label: Expired
        filter: {kql: 'apache_tomcat.session.expire.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.expire.total
      - id: 9feae62a-7de4-263b-e099-de8c4d8077b9
        label: Rejected
        filter: {kql: 'apache_tomcat.session.rejected.count: *'}
        aggregation: last_value
        field: apache_tomcat.session.rejected.count
      breakdowns:
      - {id: f5fb6326-26af-f495-421b-7b423475aa29, type: values, size: 10000, \n\
          field: apache_tomcat.session.application_name}
""")
