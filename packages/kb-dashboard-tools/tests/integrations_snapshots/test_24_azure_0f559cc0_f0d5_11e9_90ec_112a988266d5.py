"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/azure/kibana/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5.json`."""
    assert integrations_yaml_for('packages/azure/kibana/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5.json') == snapshot("""\
dashboards:
- name: '[Logs Azure] Alerts Overview'
  id: azure-0f559cc0-f0d5-11e9-90ec-112a988266d5
  description: This dashboard provides expanded alerts overview for Azure cloud.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: azure.activitylogs}
  controls:
  - id: d617c958-32bc-5a3b-503e-1244328b809f
    label: Subscription
    type: options
    field: azure.subscription_id
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 9d1a26e6-2ff0-4d3e-bab3-7bb3c50cd060
    title: Navigation Alerts
    size: {w: 21, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: "### Azure Monitoring\\n\\n[Overview](#/dashboard/azure-41e84340-ec20-11e9-90ec-112a988266d5)
        | [Users](#/dashboard/azure-87095750-f05a-11e9-90ec-112a988266d5) | [**Alerts**](#/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5) ",
      font_size: 10, links_in_new_tab: false}
  - id: e5e45365-c81a-4f7f-b58b-8d2d781329a5
    title: Alerts Overview
    size: {w: 27, h: 15}
    position: {x: 21, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 1bf73098-7576-cda2-b39e-c5aabbebd628
        label: Activated
        filter: {kql: 'azure.activitylogs.result_type: "Activated"'}
        aggregation: count
        field: '@timestamp'
      - id: 79be1122-26d2-ade8-c990-5f299529a7f9
        label: Resolved/Succeeded
        filter: {kql: 'azure.activitylogs.result_type: "Resolved" or azure.activitylogs.result_type:
            "Succeeded"'}
        aggregation: count
        field: '@timestamp'
      id: cedc252e-1aae-48fa-f5e7-b45876c77793
      legend: {visible: hide}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 36fb5c08-80d9-4a1c-8fde-9c063381fdd8
    title: Alerts Heatmap
    size: {w: 21, h: 20}
    position: {x: 0, y: 4}
    lens:
      type: heatmap
      id: d03e8dc1-a13b-fac2-3127-7c6a294dfef5
      data_view: logs-*
      x_axis: {id: 67e64ad9-cfc4-92b1-a192-87dafea58540, type: values, field: \n\
          TODO_field}
      y_axis: {id: cc39073e-b1ab-221c-1f1f-4150ee172e9b, type: values, size: 5, \n\
          field: azure.resource.provider}
      metric: {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, \n\
          aggregation: count, field: ___records___}
  - id: 162fb43e-fff3-4f50-aa9b-a713418bd651
    title: Alerts Count
    size: {w: 27, h: 9}
    position: {x: 21, y: 15}
    lens:
      id: bd676e9d-7a12-b074-4273-cf92c544a797
      type: metric
      data_view: logs-*
      primary: {id: 68928132-55cb-befc-37f2-9c98607e83b8, label: Alerts, \n\
          aggregation: count, field: ___records___}
      breakdown:
        id: e0b7c278-4422-8706-dfac-5d3bf3aeb931
        type: filters
        filters:
        - query: {kql: 'azure.activitylogs.result_type : "Activated"'}
          label: Activated
        - query: {kql: 'azure.activitylogs.result_type : "Resolved"'}
          label: Resolved
        - query: {kql: 'azure.activitylogs.result_type : "Succeeded"'}
          label: Succeeded
""")
