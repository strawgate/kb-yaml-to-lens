"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/1password/kibana/dashboard/1password-item-usages-full-dashboard.json`."""
    assert integrations_yaml_for('packages/1password/kibana/dashboard/1password-item-usages-full-dashboard.json') == snapshot("""\
dashboards:
- name: Item Usages [1Password]
  id: 1password-item-usages-full-dashboard
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 33e47a7b-72d2-4721-818c-8df8d710c5ea
    title: ''
    size: {w: 31, h: 15}
    position: {x: 0, y: 0}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_33e47a7b-72d2-4721-818c-8df8d710c5ea'}
  - id: 5270ad02-a029-4aab-a42a-b0b38988d36d
    title: ''
    size: {w: 17, h: 15}
    position: {x: 31, y: 0}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: 1591a01e-b61e-4f3a-88d5-f825e39e60b6
    title: Item Usages over time [1Password]
    size: {w: 24, h: 11}
    position: {x: 0, y: 15}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      id: 629f4f74-7f0a-5ab5-f057-470b4e466205
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        y_left_axis:
          title: Count
          extent: {mode: data_bounds}
      mode: stacked
  - id: 91a1db37-775f-4e70-b8ce-ad7c78680c87
    title: Item Usages hot users [1Password]
    size: {w: 24, h: 11}
    position: {x: 24, y: 15}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: fb95d8b9-196d-0781-3e8e-690650344102
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 6f07e67c-e270-6bb6-1ac6-8cff766e9df0, type: values, size: 10, field: \n\
          user.id}
      - {id: 542b05be-ab2d-11ca-9cb7-74e8a5562fa4, type: values, size: 10, field: \n\
          user.full_name}
      - {id: 2b90eb88-cd3a-1cc2-01f7-158e7a7be000, type: values, size: 10, field: \n\
          user.email}
  - id: d7f0be27-d6ed-4ef6-a217-3ee1837a7988
    title: Item Usages hot vaults [1Password]
    size: {w: 24, h: 12}
    position: {x: 0, y: 26}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 53290129-1530-3eb4-b9bf-abd4918efe18
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      - id: 1f034ff8-a034-7920-fe34-ab2b9b71e10e
        label: Top Item UUID
        filter: {kql: 'onepassword.item_uuid: *'}
        aggregation: last_value
        field: onepassword.item_uuid
      breakdowns:
      - {id: eb44fd4d-08b0-fd5b-7ed6-a737a53174db, type: values, size: 5, field: \n\
          onepassword.vault_uuid}
  - id: a7ed689a-7272-4e35-90d0-1d7724005aef
    title: Item Usages hot items [1Password]
    size: {w: 24, h: 12}
    position: {x: 24, y: 26}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 1e0f351d-1ef3-7afd-7783-3b8fabc2ddcb
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      - {id: d3252b5a-c12a-4d8e-cd1f-6b2854a0262f, label: Last Usage, \n\
          aggregation: max, field: '@timestamp'}
      breakdowns:
      - {id: 69a5e511-8a42-baee-70c3-9bb2dc0e0f1f, type: values, size: 10, field: \n\
          onepassword.item_uuid}
""")
