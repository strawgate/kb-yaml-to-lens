"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/armis/kibana/dashboard/armis-68592f5a-9c7b-4398-a723-510d5e48a8b1.json`."""
    assert integrations_yaml_for('packages/armis/kibana/dashboard/armis-68592f5a-9c7b-4398-a723-510d5e48a8b1.json') == snapshot("""\
dashboards:
- name: '[Logs Armis] Vulnerabilities'
  id: armis-68592f5a-9c7b-4398-a723-510d5e48a8b1
  description: This dashboard shows Vulnerabilities logs collected by the Armis \n\
    integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: armis.vulnerability}
  controls:
  - id: 823d5ff7-b7fe-2c56-bc84-bf66df5f6555
    label: Attack Complexity
    type: options
    field: armis.vulnerability.attack_complexity
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 961932ae-73f1-1783-c2d8-c0b440fdc9b0
    label: Availability Impact
    type: options
    field: armis.vulnerability.availability_impact
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 3bbd0658-79bf-8b38-cf15-61747d437402
    label: Integrity Impact
    type: options
    field: armis.vulnerability.integrity_impact
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: d0c46267-27b2-d677-99b1-65f0f372cd4d
    label: Status
    type: options
    field: armis.vulnerability.status
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 7bb1d8fd-50a1-b4b0-1b5f-e2e78853140f
    label: Type
    type: options
    field: armis.vulnerability.type
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 4437d991-8e37-691c-042f-33399ab0fd49
    label: Severity
    type: options
    field: vulnerability.severity
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 7591e61c-8c55-4f9d-9aad-8c233dbfe1a4
    title: Table of Content
    size: {w: 18, h: 23}
    position: {x: 0, y: 0}
    markdown: {content: "**Navigation**\\n\\n**Armis**\\n\\n- [Alerts](#/dashboard/armis-8a59c91d-69fd-4cf4-ab75-e9205ecbd095)\\n\\
        - [Devices](#/dashboard/armis-f988ffbb-80b9-42c2-8009-bbcc59d33347)\\n- **Vulnerabilities**\\n\\
        \\n**Overview**\\n\\nThis dashboard provides insights into vulnerabilities, allowing
        users to monitor security risks effectively. It includes a Control Panel for
        filtering by attack complexity, availability impact, integrity impact, status,
        and type. It displays total vulnerabilities, total threat actors, and total
        affected devices, along with key visualizations such as top 10 users, top
        10 threat actors, vulnerabilities over last detected by severity. It also
        offers breakdown of vulnerabilities by attack complexity, status, type, confidentiality
        impact, availability impact, user interaction and scope. A detailed essential
        vulnerability information, enabling deeper investigation.\\n\\n[**Integrations
        Page**](/app/integrations/detail/armis/overview)", font_size: 12, \n\
        links_in_new_tab: false}
  - id: 4041b01a-6e4b-4efd-b496-5c8de4bb391e
    title: ''
    size: {w: 12, h: 12}
    position: {x: 18, y: 0}
    lens:
      id: 791a2bfa-a7aa-9237-f5f4-1fe8bb091958
      type: metric
      data_view: logs-*
      primary:
        id: 2e550ab9-a7cd-fe84-2eb9-c82400d43b87
        label: Total Vulnerabilities
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
  - id: 8e096782-9acf-42dc-a22b-e724b11a1f9a
    title: ''
    size: {w: 18, h: 6}
    position: {x: 30, y: 0}
    lens:
      id: 57d65a47-d2b9-1560-980d-e208aff98fb3
      type: metric
      data_view: logs-*
      primary:
        id: a758c2fa-d45b-96e6-f345-57eabd268936
        label: Total Affected Devices
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: host.id
  - id: df3f5930-63b3-4726-875e-ed50afbe2709
    title: ''
    size: {w: 18, h: 6}
    position: {x: 30, y: 6}
    lens:
      id: 4e8eb987-9d00-c61b-8b4f-b7eb4eccd6b3
      type: metric
      data_view: logs-*
      primary:
        id: 7405f10b-6aa8-3ff4-6902-c2887c087f05
        label: Total Threat Actors
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: armis.vulnerability.threat_actors
  - id: 3a24ecf9-e21e-474b-a603-0286be40c20b
    title: Vulnerabilities over Last Detected by Severity [Logs Armis]
    size: {w: 30, h: 11}
    position: {x: 18, y: 12}
    lens:
      data_view: logs-*
      dimension: {id: 7f458694-2a6d-f0a1-3061-7474f89f8128, type: date_histogram,
        field: armis.vulnerability.last_detected}
      metrics:
      - id: 260bd7d4-c13d-6b77-5d3d-fb658dae7311
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdown: {id: fc9a02e9-5e1e-b0d9-7b3a-135e4b5901c7, type: values, size: \n\
          10, field: vulnerability.severity}
      id: 491a9a33-3e9d-2c73-81b0-7c51cebe5b4e
      legend: {visible: show, show_single_series: true, truncate_labels: 0}
      type: line
      appearance: {missing_values: linear}
  - id: ea3dea8b-d8e2-427f-915c-9d710e2c05bb
    title: Vulnerabilities by Attack Complexity [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 0, y: 23}
    lens:
      id: 1c064b60-b852-6295-1cd2-53031e44a591
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 25f372f1-103f-3452-2da7-ea85bc15e48b
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: 54c5aa48-f823-64aa-fcec-5fcc98dc974b, type: values, size: 5, field: \n\
          armis.vulnerability.attack_complexity}
  - id: 544b580f-7564-4d9e-8a23-42935f5c77cb
    title: Vulnerabilities by Confidentiality Impact [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 24, y: 23}
    lens:
      id: 951766a3-3c55-fbce-3707-68fa2cfbcaba
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 25f372f1-103f-3452-2da7-ea85bc15e48b
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: 7f0550be-ea57-e028-ad48-a1c1c8e9b5b5, type: values, size: 5, field: \n\
          armis.vulnerability.confidentiality_impact}
  - id: 20783847-a6f8-42d6-8146-9104ed669a02
    title: Vulnerabilities by Type [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 0, y: 38}
    lens:
      id: a0603a10-4baf-4727-48e8-d204cc177630
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 25f372f1-103f-3452-2da7-ea85bc15e48b
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: e56e3019-708a-969e-17e5-d99ee1fad325, type: values, size: 5, field: \n\
          armis.vulnerability.type}
  - id: 754c8138-c534-4740-82fc-ef45d0129b96
    title: Vulnerabilities by Availability Impact [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 24, y: 38}
    lens:
      id: 1565da81-46d3-0d5a-0731-6ac059498db4
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 25f372f1-103f-3452-2da7-ea85bc15e48b
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: b9cd8a2e-48fd-986f-f871-7091ad95ff89, type: values, size: 5, field: \n\
          armis.vulnerability.availability_impact}
  - id: be300acb-58ee-4d86-a2be-79b3c805eb3e
    title: Vulnerabilities by Status [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 0, y: 53}
    lens:
      id: 3361a30c-baaa-ab7a-04d5-7243b02bd4c6
      type: pie
      legend: {visible: show, truncate_labels: 0}
      data_view: logs-*
      metrics:
      - id: 25f372f1-103f-3452-2da7-ea85bc15e48b
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: 4cf899c9-a7f1-14dd-83e6-c0690285a1d1, type: values, size: 5, field: \n\
          armis.vulnerability.status}
  - id: 07e4c439-efc6-4a04-8918-26594f250f19
    title: Vulnerabilities by User Interaction [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 24, y: 53}
    lens:
      data_view: logs-*
      dimension: {id: de0b3e17-d944-ce94-6bc1-06952fa0056a, type: values, size: \n\
          10, field: armis.vulnerability.user_interaction}
      metrics:
      - id: 260bd7d4-c13d-6b77-5d3d-fb658dae7311
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      id: c670cdf4-264c-8b4f-7219-17408f040d0a
      legend: {visible: show, truncate_labels: 0}
      type: bar
      mode: stacked
  - id: f9abc45f-d604-4424-9ecd-430a01ad442e
    title: Vulnerabilities by Scope [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 0, y: 68}
    lens:
      data_view: logs-*
      dimension: {id: 949074e1-2f6f-703f-7798-6bc819b57b67, type: values, size: \n\
          10, field: armis.vulnerability.scope}
      metrics:
      - id: 260bd7d4-c13d-6b77-5d3d-fb658dae7311
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      id: 33030e7a-89d3-5f9e-bda9-5bbf1c5554c1
      legend: {visible: show, truncate_labels: 0}
      type: bar
      mode: stacked
  - id: 29ae1214-cc78-4264-a6d3-df385732c2a7
    title: Top 10 User with Highest Vulnerabilities [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 24, y: 68}
    lens:
      type: datatable
      id: 7689bd7d-f7bc-14b2-fda0-e59d4c9f3a25
      data_view: logs-*
      metrics:
      - id: e1ac1b38-e83f-2eba-8b4b-46c98be65b8e
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: 9e554af4-a6ce-9259-e73d-ac7c382aef4d, type: values, size: 10, field: \n\
          user.name}
  - id: 4b042bfe-7820-4232-be43-961a8b1c83f1
    title: Top 10 Threat Actor with Highest Vulnerabilities [Logs Armis]
    size: {w: 48, h: 16}
    position: {x: 0, y: 83}
    lens:
      type: datatable
      id: 54977627-f8dd-7559-c9d4-3152b7db94ef
      data_view: logs-*
      metrics:
      - id: e1ac1b38-e83f-2eba-8b4b-46c98be65b8e
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdowns:
      - {id: ce98efc6-2fcc-460d-e6cf-5bd65fabc43f, type: values, size: 10, field: \n\
          armis.vulnerability.threat_actors}
  - id: 3d38e8cd-465c-4b53-a1a4-a4e040950c28
    title: Vulnerabilities Essential Details [Logs Armis]
    size: {w: 48, h: 21}
    position: {x: 0, y: 99}
    search: {saved_search_id: TODO_saved_search_id}
""")
