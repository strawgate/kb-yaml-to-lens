"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3.json`."""
    assert integrations_yaml_for(
        'packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3.json'
    ) == snapshot("""\
dashboards:
- name: '[Logs Amazon Security Lake] Overview'
  id: amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3
  description: Overview of the Common logs collected by the Amazon Security Lake
    Integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: b8a5ac3b-8e57-c6e8-f744-dae56d1c3dac
    label: Severity
    type: options
    field: ocsf.severity
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 9761baf5-5922-8fdb-edb6-979c56534a57
    label: Vendor Name
    type: options
    field: ocsf.metadata.product.vendor_name
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 09da8105-29e2-e39e-ca5d-bf76f580a2f9
    label: Class Name
    type: options
    field: ocsf.class_name
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 4927d3c0-18f7-97c9-a79d-9dd15526b4d5
    label: Category Name
    type: options
    field: ocsf.category_name
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 07e3f8ea-c992-0183-4673-2279442981bd
    label: Activity Name
    type: options
    field: ocsf.activity_name
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 275166f2-756b-9a94-4f00-07a90c8077f0
    label: Status
    type: options
    field: ocsf.status
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: e155cda7-38a2-040c-3e6a-33339866c123
    label: Cloud Account ID
    type: options
    field: cloud.account.id
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 9acdbabc-b3a8-47e3-b782-4fe29dce3841
    title: Table of Contents
    size: {w: 10, h: 29}
    position: {x: 0, y: 0}
    markdown: {content: "**Navigation**\\n\\n**Amazon Security Lake**  \\n\\n**[Overview
        Dashboard](/app/dashboards#/view/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3)**\\
        \\   \\n- [System Activity](/app/dashboards#/view/amazon_security_lake-9f829d40-7e1e-11ee-8bb4-f99e39910112)\\
        \\  \\n- [Findings](/app/dashboards#/view/amazon_security_lake-ed18e3a0-2565-11ee-be5c-17edc959116c)\\
        \\  \\n- [Identity & Access Management](/app/dashboards#/view/amazon_security_lake-41b73270-25fe-11ee-983a-17fb20a3b25d)\\
        \\  \\n- Network Activity\\n    - [Network Activity (4001)](/app/dashboards#/view/amazon_security_lake-1bbac7b0-2632-11ee-a94e-bfa24df19b15)\\
        \\  \\n    - [DNS Activity (4003)](/app/dashboards#/view/amazon_security_lake-15b6e140-24a3-11ee-bb84-975fc16e8386)\\
        \\  \\n    - [HTTP (4002), DHCP (4004), RDP (4005), SMB (4006), SSH (4007),
        FTP (4008), Network File Activity (4010)](/app/dashboards#/view/amazon_security_lake-48997710-7d65-11ee-8bb4-f99e39910112)\\n\\
        \\    - [Email Activity (4009), Email File Activity (4011), Email URL Activity
        (4012)](/app/dashboards#/view/amazon_security_lake-3ec9b110-7d82-11ee-8bb4-f99e39910112)\\
        \\  \\n- [Discovery](/app/dashboards#/view/amazon_security_lake-c2efb230-7d48-11ee-8bb4-f99e39910112)\\
        \\  \\n- [Application Activity](/app/dashboards#/view/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1)\\
        \\  \\n\\n**Overview**\\n\\nThis dashboard shows an overview of the most common
        data collected from the Amazon Security Lake Integration.\\n\\nPlease visit
        the [Base Event](https://schema.ocsf.io/1.1.0/base_event) documentation for
        more information.\\n\\n[**Integration Page**](/app/integrations/detail/amazon_security_lake/overview)\\n\\
        \\n", font_size: 12, links_in_new_tab: false}
  - id: 6d129c0e-ddf1-48df-b38a-bee772e29a0b
    title: Categories Count[Logs Amazon Security Lake]
    hide_title: true
    size: {w: 38, h: 14}
    position: {x: 10, y: 0}
    lens:
      id: f1674dd2-14d1-2121-7967-c4d057ccc641
      type: metric
      data_view: logs-*
      primary:
        id: 54f83914-6974-49ac-6aeb-35484f467d02
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 5622b716-8e50-32fd-1783-a5c76443c0c4, type: values, size: \n\
          6, field: ocsf.category_name}
  - id: efb10252-f73d-4f0d-ac12-55b3bf39eb87
    title: Events by Status [Logs Amazon Security Lake]
    size: {w: 19, h: 15}
    position: {x: 10, y: 14}
    lens:
      id: 7022f5d0-3f2d-2d28-f4db-6d80f423fce0
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
      - {id: 8e5d3da2-d39c-4293-aa8c-85123d687d1d, type: values, size: 5, field: \n\
          ocsf.status}
  - id: f6b60a1b-9416-4066-8037-5c31282c5c09
    title: Events by Region [Logs Amazon Security Lake]
    size: {w: 19, h: 15}
    position: {x: 29, y: 14}
    lens:
      id: 332f9ba0-a39c-195c-81c0-348148b097ae
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
      - {id: e467f700-21bd-4f80-e408-bde21e7dee11, type: values, size: 5, field: \n\
          cloud.region}
  - id: 877cc6e8-0997-4702-9ce7-4e61b34e1afa
    title: Events by Severity [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 0, y: 29}
    lens:
      id: e743612e-6c9e-8013-a649-256d7d9b5d25
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
      - {id: a500cafb-0a93-f1b1-0905-dd56d4052a67, type: values, size: 5, field: \n\
          ocsf.severity}
  - id: 0835ddad-4601-411b-b5c1-1e838c0608c5
    title: Events by Vendor Name [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 24, y: 29}
    lens:
      data_view: logs-*
      dimension: {id: 48eb9b4a-3999-a196-449f-0bde4554679e, type: values, size: \n\
          10, field: ocsf.metadata.product.vendor_name}
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      id: 669c5db9-654e-ed51-dd78-f71aa8d5395a
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 3875494b-7f90-4064-896e-76ac9391edbc
    title: Events by Class [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 0, y: 44}
    lens:
      data_view: logs-*
      dimension: {id: f0689ebb-4352-aff6-dded-cd99b0b193ad, type: values, size: \n\
          33, field: ocsf.class_name}
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      id: c22a6299-0c74-d8f5-926d-312ea10f30fe
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: fd7315e0-aa9b-4ea6-a415-6547f732c14a
    title: Events by Product Name [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 24, y: 44}
    lens:
      data_view: logs-*
      dimension: {id: 33951eb0-8073-043a-4ce7-ca4e4aa8019d, type: values, size: \n\
          10, field: ocsf.metadata.product.name}
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      id: f9d86083-eac4-e9ed-045e-6429e330aa7a
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 5a5c0ff1-5286-445e-b95d-6ca234e09614
    title: Severity over Time [Logs Amazon Security Lake]
    size: {w: 48, h: 14}
    position: {x: 0, y: 59}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 8728e3ab-9762-f275-b2d2-6015c66db81e
        label: Severity
        format: {type: number, decimals: 0}
        aggregation: count
        field: event.severity
      id: 9df57957-788b-a532-369d-9033ac9875ee
      legend: {visible: show, truncate_labels: 0}
      type: line
""")
