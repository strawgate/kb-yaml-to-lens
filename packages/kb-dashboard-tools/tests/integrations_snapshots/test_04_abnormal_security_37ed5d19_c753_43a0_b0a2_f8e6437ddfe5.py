"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/abnormal_security/kibana/dashboard/abnormal_security-37ed5d19-c753-43a0-b0a2-f8e6437ddfe5.json`."""
    assert integrations_yaml_for(
        'packages/abnormal_security/kibana/dashboard/abnormal_security-37ed5d19-c753-43a0-b0a2-f8e6437ddfe5.json'
    ) == snapshot("""\
dashboards:
- name: '[Logs Abnormal AI] Audit Overview'
  id: abnormal_security-37ed5d19-c753-43a0-b0a2-f8e6437ddfe5
  description: This dashboard shows Audit logs collected by the Abnormal AI \n\
    integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: abnormal_security.audit}
  controls:
  - id: 4355d78d-d525-00e5-cbe1-1c16dd6c7c63
    label: Category
    type: options
    field: abnormal_security.audit.category
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: d5bb3b4a-6e3e-bee9-cc0d-91144f92f3f9
    label: Tenant Name
    type: options
    field: cloud.account.name
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 2858a0e8-1148-a197-ab37-de2e1e4f8697
    label: Status
    type: options
    field: event.outcome
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: ca5ffc5c-93d1-4505-b795-313668967c10
    title: Overview
    size: {w: 12, h: 23}
    position: {x: 0, y: 4}
    markdown: {content: "This dashboard displays key statistics and visualizations
        based on Audit logs from the Abnormal AI integration. It includes the top
        10 users and source IPs, a breakdown of events by category, action and tenant
        name, as well as essential details about the Audit data.\\n\\n[**Integration
        Page**](/app/integrations/detail/abnormal_security/overview)", font_size: \n\
        12, links_in_new_tab: false}
  - id: c7a61847-bf18-4297-a0e2-2fc16216a962
    title: Audit Events by Tenant Name [Logs Abnormal AI]
    size: {w: 36, h: 12}
    position: {x: 12, y: 4}
    lens:
      data_view: logs-*
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 991ef1ed-0396-c7bb-6fcd-66ab121830e9, type: values, size: \n\
          10, field: cloud.account.name}
      id: 98d9951f-9592-1f5c-ec9b-70b89c514df8
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: cb3ce987-ba73-42ca-ae20-bb4868145bd5
    title: Audit Events by Action [Logs Abnormal AI]
    size: {w: 36, h: 11}
    position: {x: 12, y: 16}
    lens:
      data_view: logs-*
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 208bfe09-9d04-9a3c-f6f5-80128d02dbe2, type: values, size: \n\
          10, field: event.action}
      id: 0fe75dc7-ad26-9eba-9c74-9f5ad57f30ae
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 943d8454-266a-4430-a16a-468ad4e8ab35
    title: Audit Events by Category [Logs Abnormal AI]
    size: {w: 17, h: 18}
    position: {x: 0, y: 27}
    lens:
      id: 19b85489-6af3-f650-24f3-f7705bdf2b93
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 97eb71b4-0976-a4ed-a27e-255aae5b58d9
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: e9b8c05c-fc70-dedc-74ec-14382e8770c0, type: values, size: 5, field: \n\
          abnormal_security.audit.category}
  - id: 876c8eff-917a-4366-b2e0-8d635bf76593
    title: Top 10 Users [Logs Abnormal AI]
    size: {w: 15, h: 18}
    position: {x: 17, y: 27}
    lens:
      type: datatable
      id: 66b77843-24f5-691e-9aaa-8c775d9b6a55
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: 2b90eb88-cd3a-1cc2-01f7-158e7a7be000, type: values, size: 10, field: \n\
          user.email}
  - id: 898fe80b-6dab-4c13-bd89-d0442dac4d08
    title: Top 10 Source IP [Logs Abnormal AI]
    size: {w: 16, h: 18}
    position: {x: 32, y: 27}
    lens:
      type: datatable
      id: 4ee28d94-c75d-a961-8e9a-c8c13e67ecd7
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: a2755665-9aab-e4b4-54ff-df26fe3282cd, type: values, size: 10, field: \n\
          source.ip}
  - id: 24aca30e-7efb-4dcc-9290-bb261aa10a33
    title: Audit Essential Details [Logs Abnormal AI]
    size: {w: 48, h: 16}
    position: {x: 0, y: 45}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_24aca30e-7efb-4dcc-9290-bb261aa10a33'}
  - id: a627f997-3e5f-4eae-949c-79579ef9004c
    title: ''
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: 33400c81-5fb1-4da4-934d-32b65afcf558, label: AI Security Mailbox \n\
          Overview, dashboard: \n\
          TODO_dashboard_id_for_link_33400c81-5fb1-4da4-934d-32b65afcf558_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 030a5e00-a69a-4332-9b69-48142c1efb12, label: AI Security Mailbox \n\
          Not Analyzed Overview, dashboard: \n\
          TODO_dashboard_id_for_link_030a5e00-a69a-4332-9b69-48142c1efb12_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 2557a28a-de07-40e2-9303-845f1fab3e64, label: Audit Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_2557a28a-de07-40e2-9303-845f1fab3e64_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 9250b058-50f6-4978-9a80-df5ca5ac7198, label: Case Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_9250b058-50f6-4978-9a80-df5ca5ac7198_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: d5f9a705-db40-48a9-bb9b-92267aab6d4b, label: Threat Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_d5f9a705-db40-48a9-bb9b-92267aab6d4b_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 0044e276-8253-4288-bbf9-fe324340602e, label: Vendor Case Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_0044e276-8253-4288-bbf9-fe324340602e_dashboard,
        new_tab: false, with_time: false, with_filters: false}
""")
