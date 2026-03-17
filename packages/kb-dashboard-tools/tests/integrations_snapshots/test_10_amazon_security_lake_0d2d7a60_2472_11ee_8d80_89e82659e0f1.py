"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1.json`."""
    assert integrations_yaml_for(
        'packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1.json'
    ) == snapshot("""\
dashboards:
- name: '[Logs Amazon Security Lake] Application Activity'
  id: amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1
  description: Overview of Application Activity logs collected by the Amazon \n\
    Security Lake Integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: 09da8105-29e2-e39e-ca5d-bf76f580a2f9
    label: Class Name
    type: options
    field: ocsf.class_name
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: b8a5ac3b-8e57-c6e8-f744-dae56d1c3dac
    label: Severity
    type: options
    field: ocsf.severity
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
  - id: 07e3f8ea-c992-0183-4673-2279442981bd
    label: Activity Name
    type: options
    field: ocsf.activity_name
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
  - id: e155cda7-38a2-040c-3e6a-33339866c123
    label: Cloud Account ID
    type: options
    field: cloud.account.id
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: f5b306a1-0dfb-40a3-8f01-897f41098d59
    title: Table of Contents
    size: {w: 10, h: 28}
    position: {x: 0, y: 0}
    markdown: {content: "**Navigation**\\n\\n**Amazon Security Lake**  \\n\\n[Overview
        Dashboard](/app/dashboards#/view/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3)\\
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
        \\  \\n- **[Application Activity](/app/dashboards#/view/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1)**\\
        \\  \\n\\n**Overview**\\n\\nThis dashboard shows an overview of detailed information
        about the behavior of applications and services.\\n\\nPlease visit the [Application
        Activity](https://schema.ocsf.io/1.1.0/categories/application) documentation
        for more information.\\n\\n[**Integration Page**](/app/integrations/detail/amazon_security_lake/overview)\\n",
      font_size: 12, links_in_new_tab: false}
  - id: a56f200e-1ed0-4d67-9209-8794163953a4
    title: Count of App [Logs Amazon Security Lake]
    hide_title: true
    size: {w: 19, h: 12}
    position: {x: 10, y: 0}
    lens:
      id: 15ba3af5-f760-010c-e25a-f70381efe768
      type: metric
      data_view: logs-*
      primary:
        id: cd134d32-0853-4f55-d630-adb5c66e8833
        label: Total Application
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
  - id: 0fbd6b6c-0068-465b-ad20-0cbe2cabb99e
    title: Web Resources By Type [Logs Amazon Security Lake]
    size: {w: 19, h: 12}
    position: {x: 29, y: 0}
    lens:
      id: b7e992fa-735f-610a-cc62-54b2afd0419c
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
      - {id: 2d5350b4-19e6-63d8-d709-307a005d18c7, type: values, size: 5, field: \n\
          package.type}
  - id: 26a6a474-72b4-48f9-bba1-760b79947ace
    title: Events by Application Vendor [Logs Amazon Security Lake]
    size: {w: 19, h: 16}
    position: {x: 10, y: 12}
    lens:
      id: d8025215-6e75-ba05-c301-5e3777626e76
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
      - {id: fa79cf87-88d0-fa96-1c00-75cd95abc430, type: values, size: 5, field: \n\
          ocsf.app.vendor_name}
  - id: 1b312846-0250-4c85-b330-35bfbf3daf0a
    title: Events by Activity [Logs Amazon Security Lake]
    size: {w: 19, h: 16}
    position: {x: 29, y: 12}
    lens:
      data_view: logs-*
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 03e7cb98-3a81-b117-6b7f-b29ee7784de8, type: values, size: \n\
          10, field: ocsf.activity_name}
      id: f388061e-db59-53e7-9462-e6e7ab415d90
      legend: {visible: show, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: efb41cd8-6a78-461f-8787-a61e80618115
    title: Top 10 Source IP [Logs Amazon Security Lake]
    size: {w: 24, h: 16}
    position: {x: 0, y: 28}
    lens:
      type: datatable
      appearance: {row_height: single, row_height_lines: 1, header_row_height: \n\
          auto, density: normal}
      paging: {enabled: false, page_size: 10}
      id: 5945db29-47d5-cc85-6946-1a7003beb449
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
  - id: da28d9c3-198a-4986-aee2-f9dd5979d8b2
    title: Top 10 Destination IP [Logs Amazon Security Lake]
    size: {w: 24, h: 16}
    position: {x: 24, y: 28}
    lens:
      type: datatable
      paging: {enabled: false, page_size: 10}
      id: 2a179d30-12f0-d6af-966e-7c97d6e33030
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: d00fa247-9907-95b8-ede5-883320962db2, type: values, size: 10, field: \n\
          destination.ip}
  - id: d2166881-ac57-4662-a196-ce6b6af93126
    title: Top 10 Web Resources [Logs Amazon Security Lake]
    size: {w: 24, h: 16}
    position: {x: 0, y: 44}
    lens:
      type: datatable
      id: d738442e-b7b2-9f34-7c11-553fa5f5d266
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: 4e6fabca-f827-69ea-1cd3-4606a2b3ef62, type: values, size: 10, field: \n\
          package.name}
  - id: 91e008ad-1307-4cf7-b0d7-b201141160e2
    title: Top 10 Affected Resources [Logs Amazon Security Lake]
    size: {w: 24, h: 16}
    position: {x: 24, y: 44}
    lens:
      type: datatable
      id: 450f9113-7a6e-3fb8-1bcc-6b1e7fbedd7a
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: 82ea0287-a604-e56b-556d-0ec07c331d48, type: values, size: 10, field: \n\
          ocsf.resources.name}
  - id: 30183f08-3be7-4802-8eda-8fd8acc498fa
    title: Top 10 Affected Application [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 24, y: 60}
    lens:
      type: datatable
      id: d97f20c3-b0e3-3b52-9559-d1d4e027aff7
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: 2464756d-e78c-c660-b3de-cb12712b901a, type: values, size: 10, field: \n\
          ocsf.app.name}
  - id: acd5d520-6f2c-4ec0-b55a-0e480e849573
    title: Top 10 URL with Highest Access [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 0, y: 60}
    lens:
      type: datatable
      id: f1c926d1-3b90-2101-e26e-13fa5369f5b3
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: 2dfb06a3-0dd7-51e2-bc3f-5f6b06c4bb50, type: values, size: 10, field: \n\
          ocsf.web_resources.url_string}
  - id: 480b0cc8-c699-4cd6-ba48-d526764ad79b
    title: Top 10 URL with Highest Denied [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 0, y: 75}
    lens:
      type: datatable
      id: f1c926d1-3b90-2101-e26e-13fa5369f5b3
      data_view: logs-*
      metrics:
      - id: 9893f855-4c35-cf1f-b8aa-0e707634a9ee
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdowns:
      - {id: 2dfb06a3-0dd7-51e2-bc3f-5f6b06c4bb50, type: values, size: 10, field: \n\
          ocsf.web_resources.url_string}
  - id: 7047cace-d1ab-4132-b446-80309dcf6563
    title: API Operation by Account ID [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 24, y: 90}
    lens:
      data_view: logs-*
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 4567c6a0-259e-ca7a-661e-c7af3527ba1b, type: values, size: \n\
          10, field: ocsf.actor.user.account.uid}
      id: 04e6aec6-da7f-6799-465d-6c5e9ec73fbf
      legend: {visible: show, show_single_series: true, truncate_labels: 0}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 45eebc37-b634-45c6-8e06-5c2dca8d2da4
    title: API Activity by Service over Time [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 0, y: 90}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 16308a59-c307-8d65-632f-741e5dadfdb0, type: values, size: \n\
          10, field: ocsf.api.service.name}
      id: c3fc9d56-12e7-cdd1-69a2-c1e2888800cc
      legend: {visible: show, width: large, show_single_series: true, \n\
          truncate_labels: 0}
      type: line
  - id: a7d4bad3-6882-4334-9e93-32bfa8b92fc1
    title: Web Resource Access Events by Activity [Logs Amazon Security Lake]
    size: {w: 24, h: 15}
    position: {x: 24, y: 75}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: e069b586-3554-c013-6c8a-0229d0772fb2
        label: Web Resource Access Events
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 03e7cb98-3a81-b117-6b7f-b29ee7784de8, type: values, size: \n\
          10, field: ocsf.activity_name}
      id: 6c4dc332-59bc-29c7-a6e2-49f85a00161f
      legend: {visible: show, show_single_series: true, truncate_labels: 0}
      type: line
  - id: bafa4a84-cd88-474c-b184-abf585029430
    title: ''
    size: {w: 48, h: 15}
    position: {x: 0, y: 105}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_bafa4a84-cd88-474c-b184-abf585029430'}
  - id: 96e95a12-c91a-4ecb-aa52-52884e5af866
    title: API Operation by Service [Logs Amazon Security Lake]
    size: {w: 48, h: 15}
    position: {x: 0, y: 120}
    lens:
      type: heatmap
      id: 5c214e73-edb2-c347-e945-6d831263edfc
      data_view: logs-*
      x_axis: {id: 67e64ad9-cfc4-92b1-a192-87dafea58540, type: values, field: \n\
          TODO_field}
      y_axis: {id: 4df83456-1aef-00fd-a339-52b59a175204, type: values, size: 5, \n\
          field: ocsf.api.operation}
      metric:
        id: 97eb71b4-0976-a4ed-a27e-255aae5b58d9
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
""")
