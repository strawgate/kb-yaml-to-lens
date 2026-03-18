"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/auth0/kibana/dashboard/auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf.json`."""
    assert integrations_yaml_for('packages/auth0/kibana/dashboard/auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf.json') == snapshot("""\
dashboards:
- name: Auth0
  id: auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 1a13814d-17bf-42cf-8ef9-2dc599fb6766
    title: Auth0 Log Stream Event Types
    size: {w: 15, h: 10}
    position: {x: 0, y: 0}
    lens:
      id: fddb976d-8c26-b8c6-135a-8821d498482d
      type: pie
      data_view: logs-*
      metrics:
      - {id: 45862133-3a58-d112-d754-dfbd3642a4e4, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 1fafb44f-baf9-8729-727f-25292d26b071, type: values, size: 5, field: \n\
          event.category}
  - id: 6089a77e-3c96-4414-9932-eda55ced3d07
    title: Rate of events
    size: {w: 14, h: 10}
    position: {x: 15, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 80593e81-2240-09ce-0ed4-72a28e5c7453, label: Unique count of \n\
          event.type, aggregation: unique_count, field: event.type}
      id: cb4380fc-2f0b-9732-4221-917b1eaad048
      legend: {visible: show}
      type: line
  - id: 5124c723-8890-477e-aad5-bc4fd529bd46
    title: ''
    size: {w: 9, h: 5}
    position: {x: 29, y: 0}
    lens:
      id: 21ea12b7-2d60-a974-def7-6b5d51f7274c
      type: metric
      data_view: logs-*
      primary: {id: 76ebcc27-9947-fb34-0237-d105829dbf47, label: Count of Failed
          Logins, aggregation: count, field: ___records___}
  - id: cb337534-d263-480b-b6a3-80cc4f14d73b
    title: Number of Successful Logins
    size: {w: 10, h: 5}
    position: {x: 38, y: 0}
    lens:
      id: 95ece390-67c3-5f41-ab17-78545af3fb48
      type: metric
      data_view: logs-*
      primary: {id: 90c68c7b-bef9-4068-3235-0b7c27368a11, label: Count of \n\
          Successful Logins, aggregation: count, field: ___records___}
  - id: f35d9f39-29b5-4ea3-b43a-36da7af3b2af
    title: Number of Failed Signups
    size: {w: 9, h: 5}
    position: {x: 29, y: 5}
    lens:
      id: 8afc7342-3c96-b073-5544-1cba9c548b25
      type: metric
      data_view: logs-*
      primary: {id: d7c62aa6-2fac-4195-2e9c-91d77d584800, label: Count of Failed
          Signups, aggregation: count, field: ___records___}
  - id: 27dafd73-8177-4243-b93c-426f70bc5fea
    title: Number of Successful Signups
    size: {w: 10, h: 5}
    position: {x: 38, y: 5}
    lens:
      id: 5db2d673-3b8d-c208-bd22-64e6f6bcdadf
      type: metric
      data_view: logs-*
      primary: {id: b0d33e81-cbb1-49db-8ffa-5c25d7a8af51, label: Count of \n\
          Successful Signups, aggregation: count, field: ___records___}
  - id: d00429d4-502f-41d8-8a2b-7300859930ea
    title: Rate of Successful Logins
    size: {w: 15, h: 12}
    position: {x: 0, y: 10}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 28ba3e0b-7a41-30d4-9377-96a097cfc685, label: Count of records, \n\
          aggregation: count, field: ___records___}
      id: 3c3713e4-cc81-1e3c-25fd-e6f3a6b28680
      legend: {visible: show}
      type: line
  - id: c1a1b718-c5f1-4029-9fda-0cd7ed38b3a8
    title: Rate of Failed Logins
    size: {w: 14, h: 12}
    position: {x: 15, y: 10}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 28ba3e0b-7a41-30d4-9377-96a097cfc685, label: Count of records, \n\
          aggregation: count, field: ___records___}
      id: 3c3713e4-cc81-1e3c-25fd-e6f3a6b28680
      legend: {visible: show}
      type: line
  - id: 7f0587d4-ef04-4913-9ccb-cd2c93f470df
    title: IP Addresses of failed logins
    size: {w: 19, h: 12}
    position: {x: 29, y: 10}
    lens:
      data_view: logs-*
      dimension: {id: 9c163176-a698-fe32-8f76-536c715679a5, type: values, size: \n\
          10, field: source.ip}
      metrics:
      - {id: 28ba3e0b-7a41-30d4-9377-96a097cfc685, label: Count of records, \n\
          aggregation: count, field: ___records___}
      id: 70cff741-cb3a-5dfe-ca54-9dbcc122d702
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 253f1007-1537-4012-a663-48bccf233f4c
    title: ''
    size: {w: 48, h: 11}
    position: {x: 0, y: 22}
    search: {saved_search_id: TODO_saved_search_id}
""")
