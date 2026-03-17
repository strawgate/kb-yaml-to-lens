"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/abnormal_security/kibana/dashboard/abnormal_security-f6562262-e429-470d-af45-4c80afdcf664.json`."""
    assert integrations_yaml_for(
        'packages/abnormal_security/kibana/dashboard/abnormal_security-f6562262-e429-470d-af45-4c80afdcf664.json'
    ) == snapshot("""\
dashboards:
- name: '[Logs Abnormal AI] Case Overview'
  id: abnormal_security-f6562262-e429-470d-af45-4c80afdcf664
  description: This dashboard shows Case logs collected by the Abnormal AI \n\
    integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: abnormal_security.case}
  controls:
  - id: c0aeaa57-56a2-0164-d021-c8744609b5fb
    label: Case Status
    type: options
    field: abnormal_security.case.status
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 51c21e60-713f-9172-f90d-161cccaae1b9
    label: Remediation Status
    type: options
    field: abnormal_security.case.remediation_status
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: be8848ae-d86d-b26f-aad1-2ddfb7de6708
    label: Severity Level
    type: options
    field: abnormal_security.case.severity_level
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 2bb6c91f-2422-4267-9e2b-a801bb5ed541
    title: Overview
    size: {w: 12, h: 23}
    position: {x: 0, y: 4}
    markdown: {content: "This dashboard displays key statistics and visualizations
        based on Case logs from the Abnormal AI integration. It includes the top 10
        affected employees, a breakdown of events by remediation status, severity,
        analysis and status, as well as essential details about the Case data and
        total cases.\\n\\n[**Integration Page**](/app/integrations/detail/abnormal_security/overview)",
      font_size: 12, links_in_new_tab: false}
  - id: 3bdeee33-c138-47da-94ff-98253e939476
    title: ''
    hide_title: true
    size: {w: 16, h: 11}
    position: {x: 12, y: 4}
    lens:
      id: 125c6758-3c69-dbe3-5b5b-becf589bce7b
      type: metric
      data_view: logs-*
      primary:
        id: 53a15432-814b-ca42-052c-8fea60809eea
        label: Total Cases
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: event.id
  - id: e4bfcebf-3ee1-41af-aca3-b60b2dc3e6e8
    title: Cases by Remediation Status [Logs Abnormal AI]
    size: {w: 20, h: 11}
    position: {x: 28, y: 4}
    lens:
      id: cd585d48-3dad-c705-f327-b0c37416146a
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 0580f231-7bca-b3dd-a484-3aabc94ceb50
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: event.id
      breakdowns:
      - {id: e89704c6-d41d-9b63-fcb3-31a2a7631642, type: values, size: 5, field: \n\
          abnormal_security.case.remediation_status}
  - id: ca37b426-e916-49b2-a23b-d107c1521078
    title: Cases by Severity [Logs Abnormal AI]
    size: {w: 36, h: 12}
    position: {x: 12, y: 15}
    lens:
      data_view: logs-*
      metrics:
      - id: d6fe7b8d-f48e-614c-2d81-2eef048666d3
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: event.id
      breakdown: {id: bc879a1f-6629-1989-7f75-ec11fecfe51e, type: values, size: \n\
          10, field: abnormal_security.case.severity}
      id: 4346f987-1363-5439-b233-413ccf2912e5
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 38a68b80-ba46-4d76-b78a-5bdf65239cc3
    title: Top 10 Affected Employee [Logs Abnormal AI]
    size: {w: 24, h: 15}
    position: {x: 0, y: 27}
    lens:
      type: datatable
      id: 6eaa955d-f644-696d-b68f-daf2bd910bb2
      data_view: logs-*
      metrics:
      - id: f682e063-8032-cb26-cc3e-4f1592c7a72e
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: event.id
      breakdowns:
      - {id: e3332620-ca16-4231-b612-53d15cddb194, type: values, size: 10, field: \n\
          abnormal_security.case.affected_employee}
  - id: 9d8f7d6f-4e3b-4191-be31-718d245f12c2
    title: Cases by Analysis [Logs Abnormal AI]
    size: {w: 24, h: 15}
    position: {x: 24, y: 27}
    lens:
      data_view: logs-*
      metrics:
      - id: d6fe7b8d-f48e-614c-2d81-2eef048666d3
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: event.id
      breakdown: {id: 208bfe09-9d04-9a3c-f6f5-80128d02dbe2, type: values, size: \n\
          10, field: event.action}
      id: 25503908-1064-3b49-1c72-4eff0e8a8b52
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: e931b4fe-2549-4dec-afcf-d4b087ee117d
    title: Cases by Status [Logs Abnormal AI]
    size: {w: 48, h: 14}
    position: {x: 0, y: 42}
    lens:
      data_view: logs-*
      metrics:
      - id: d6fe7b8d-f48e-614c-2d81-2eef048666d3
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: event.id
      breakdown: {id: 3d5074b4-df53-ca3b-a6e3-cb00b64f1f76, type: values, size: \n\
          10, field: abnormal_security.case.status}
      id: 5c4fa40b-538c-e28f-a663-a4bdbf82e1ae
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 8bd32713-657b-4f64-ae58-baf252cb30c0
    title: Cases Essential Details [Logs Abnormal AI]
    size: {w: 48, h: 14}
    position: {x: 0, y: 56}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_8bd32713-657b-4f64-ae58-baf252cb30c0'}
  - id: 4dc07419-868c-4a14-a445-659c20c4aecc
    title: ''
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: 339b4371-c55d-4460-bc2a-58e3207296b9, label: AI Security Mailbox \n\
          Overview, dashboard: \n\
          TODO_dashboard_id_for_link_339b4371-c55d-4460-bc2a-58e3207296b9_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: fbafcc58-b3e5-440a-ac56-55886fd5f943, label: AI Security Mailbox \n\
          Not Analyzed Overview, dashboard: \n\
          TODO_dashboard_id_for_link_fbafcc58-b3e5-440a-ac56-55886fd5f943_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 8e234aa8-69ac-4be5-b990-e3a2fdbdea99, label: Audit Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_8e234aa8-69ac-4be5-b990-e3a2fdbdea99_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: f807017e-eabd-4fc9-82a1-a164a6d1ac72, label: Case Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_f807017e-eabd-4fc9-82a1-a164a6d1ac72_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 334b473c-0ccb-4600-8158-56eec465cb1a, label: Threat Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_334b473c-0ccb-4600-8158-56eec465cb1a_dashboard,
        new_tab: false, with_time: false, with_filters: false}
      - {id: 0c7df8d9-4c8b-4841-a0a3-ec77b23cd00e, label: Vendor Case Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_0c7df8d9-4c8b-4841-a0a3-ec77b23cd00e_dashboard,
        new_tab: false, with_time: false, with_filters: false}
""")
