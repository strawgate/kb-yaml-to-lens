"""Integrations decompile inline snapshot."""

# ruff: noqa: E501

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/aws_billing/kibana/dashboard/aws_billing-01aace34-9219-4c6c-80a9-b903af48950f.json`."""
    assert integrations_yaml_for('packages/aws_billing/kibana/dashboard/aws_billing-01aace34-9219-4c6c-80a9-b903af48950f.json') == snapshot("""\
dashboards:
- name: '[Metrics] AWS Cost and Usage Report - Current month'
  id: aws_billing-01aace34-9219-4c6c-80a9-b903af48950f
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: 1e14eb3b-c43e-64e3-f81b-882c19083e28
    label: Payer Account ID
    type: options
    field: aws_billing.cur.bill.payer_account_id
    fill_width: false
    preselected: []
    data_view: e65c8b0bfe6b4a0aebad76d709d8666b7812bb7a07da7ac7ce8d2af692bce544
  - id: 6c6827f3-8a50-a434-af84-7a185ff3108b
    label: Linked Account ID
    type: options
    field: aws_billing.cur.line_item.usage_account_id
    fill_width: false
    preselected: []
    data_view: e65c8b0bfe6b4a0aebad76d709d8666b7812bb7a07da7ac7ce8d2af692bce544
  panels:
  - id: 38eb0e3e-12bc-48e0-b594-eb03a117a639
    title: ''
    size: {w: 48, h: 2}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: b6533e72-35b4-4531-8e04-f104916537e1, label: Current month, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_b6533e72-35b4-4531-8e04-f104916537e1_dashboard}
      - {id: 2f0cba9f-b64b-417e-9819-fdff7bc1e7f2, label: Last month, dashboard: \n\
          TODO_dashboard_id_for_link_2f0cba9f-b64b-417e-9819-fdff7bc1e7f2_dashboard}
      - {id: edf2d69e-8788-4beb-bd2d-cd947d978bab, label: Last 3 months, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_edf2d69e-8788-4beb-bd2d-cd947d978bab_dashboard}
      - {id: 3ced28f4-a77d-47d0-a827-08d07823729e, label: Last 6 months, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_3ced28f4-a77d-47d0-a827-08d07823729e_dashboard}
      - {id: 9a656ba3-684f-4cad-8791-67ac0d2fcb07, label: All time, dashboard: \n\
          TODO_dashboard_id_for_link_9a656ba3-684f-4cad-8791-67ac0d2fcb07_dashboard}
  - id: 1c940294-1a0e-4884-95ed-a5678eb46af5
    title: Percentage of cost per product
    size: {w: 14, h: 16}
    position: {x: 20, y: 0}
    esql:
      query: "FROM aws_billing.cur_latest\\n| WHERE aws_billing.cur.line_item.type
        == \\"Usage\\" and aws_billing.cur.bill.billing_period_start_date == DATE_TRUNC(1
        month , NOW())\\n| STATS sum_line_item_unblended_cost = SUM(aws_billing.cur.line_item.unblended_cost)
        by aws_billing.cur.line_item.product_code \\n| WHERE sum_line_item_unblended_cost
        >= 0\\n| SORT sum_line_item_unblended_cost DESC\\n| rename sum_line_item_unblended_cost
        as `Unblended Cost`"
      time_field: '@timestamp'
      id: 144c7097-09f6-f953-a12d-e5c103f0183a
      type: pie
      metrics:
      - {id: 73d2d43d-1172-414b-ce57-8cd63af61e7f, field: TODO_metric_field}
      breakdowns:
      - {id: 206f9511-b1b2-16ad-8794-3fd4f90e1d31, field: TODO_dimension_field}
  - id: 3d2d4af9-d312-488f-83eb-b6af9625e5e6
    title: Percentage of cost per region
    size: {w: 14, h: 16}
    position: {x: 34, y: 0}
    esql:
      query: "FROM aws_billing.cur_latest\\n| WHERE aws_billing.cur.bill.billing_period_start_date
        == DATE_TRUNC(1 month , NOW()) AND aws_billing.cur.line_item.type == \\"Usage\\"\\
        \\n| STATS sum_line_item_unblended_cost = SUM(aws_billing.cur.line_item.unblended_cost)
        by aws_billing.cur.product.region_code\\n| WHERE sum_line_item_unblended_cost
        >= 0\\n| SORT sum_line_item_unblended_cost DESC\\n| rename sum_line_item_unblended_cost
        as `Unblended Cost`"
      time_field: '@timestamp'
      id: 74535a2b-1cb7-c05c-3a6c-f779d3fe4474
      type: pie
      metrics:
      - {id: 73d2d43d-1172-414b-ce57-8cd63af61e7f, field: TODO_metric_field}
      breakdowns:
      - {id: 206f9511-b1b2-16ad-8794-3fd4f90e1d31, field: TODO_dimension_field}
  - id: c0ccda82-6e9a-4bdb-86b7-139ed831946f
    title: ''
    size: {w: 10, h: 16}
    position: {x: 10, y: 0}
    esql:
      query: "FROM aws_billing.cur_latest\\n| WHERE aws_billing.cur.bill.billing_period_start_date
        == DATE_TRUNC(1 month , NOW()) AND aws_billing.cur.line_item.type == \\"Usage\\"\\
        \\n| STATS sum_line_item_unblended_cost = SUM(aws_billing.cur.line_item.unblended_cost)
        by aws_billing.cur.line_item.currency_code\\n| SORT sum_line_item_unblended_cost
        DESC\\n| rename sum_line_item_unblended_cost as `Total Unblended Cost`"
      time_field: '@timestamp'
      id: 26676c04-3800-e1e4-13ca-1fa48a3741f5
      type: metric
      primary: {id: 0e66d57e-a209-f46c-75c7-ef4bad6732f5, field: Total Unblended
          Cost}
  - id: 924aade6-e660-4bf5-8dc9-59093cee9fa0
    title: ''
    size: {w: 10, h: 16}
    position: {x: 0, y: 0}
    markdown: {content: "#### AWS Cost and Usage\\n\\nThis dashboard provides insights
        into the following:\\n\\n- Overview of cost distribution across all users\\n\\
        - Cost breakdown by AWS service and region\\n- Cost distribution across linked
        accounts\\n- Visual trends of usage over time\\n\\nYou can adjust the __time
        range__ using the filter options to view cost and usage for the current month,
        last 3 or 6 months, or all time.", font_size: 12, links_in_new_tab: \n\
        false}
  - id: 036fd20b-0bbf-482c-b41d-8cfea66aa6d3
    title: Cost per product
    size: {w: 16, h: 16}
    position: {x: 0, y: 16}
    esql:
      query: "FROM aws_billing.cur_latest\\n| WHERE aws_billing.cur.line_item.type
        == \\"Usage\\" and aws_billing.cur.bill.billing_period_start_date == DATE_TRUNC(1
        month , NOW())\\n| STATS sum_line_item_unblended_cost = SUM(aws_billing.cur.line_item.unblended_cost)
        by aws_billing.cur.line_item.product_code, aws_billing.cur.bill.billing_period_start_date\\
        \\  \\n| SORT sum_line_item_unblended_cost DESC\\n| rename sum_line_item_unblended_cost
        as `Unblended Cost`"
      time_field: '@timestamp'
      dimension: {id: 4a0385c5-c6f7-b30d-bb9d-548f862fd74c, field: \n\
          aws_billing.cur.bill.billing_period_start_date, label: Month}
      metrics:
      - {id: 67fac93e-eb3b-527e-8595-152adda99cfa, field: Unblended Cost}
      breakdown: {id: 7d1b4737-a2f3-c44a-8ba6-f07c086edeb8, field: \n\
          aws_billing.cur.line_item.product_code}
      id: 0b3ce621-4c93-260a-46c2-b81061461f3b
      legend: {visible: show, position: bottom}
      type: bar
      mode: stacked
  - id: e2194454-ab58-4c7a-9da1-15317e3882b7
    title: Cost per linked account
    size: {w: 16, h: 16}
    position: {x: 16, y: 16}
    esql:
      query: "FROM aws_billing.cur_latest\\n| WHERE aws_billing.cur.line_item.type
        == \\"Usage\\" and aws_billing.cur.bill.billing_period_start_date == DATE_TRUNC(1
        month , NOW())\\n| STATS sum_line_item_unblended_cost = SUM(aws_billing.cur.line_item.unblended_cost)
        by aws_billing.cur.line_item.usage_account_name, aws_billing.cur.bill.billing_period_start_date\\
        \\  \\n| SORT sum_line_item_unblended_cost DESC\\n| rename sum_line_item_unblended_cost
        as `Unblended Cost`"
      time_field: '@timestamp'
      dimension: {id: 4a0385c5-c6f7-b30d-bb9d-548f862fd74c, field: \n\
          aws_billing.cur.bill.billing_period_start_date, label: Month}
      metrics:
      - {id: 67fac93e-eb3b-527e-8595-152adda99cfa, field: Unblended Cost}
      breakdown: {id: 0af2df24-1bb0-1794-2577-1f25cf306379, field: \n\
          aws_billing.cur.line_item.usage_account_name}
      id: 9a87fea5-4a97-1f20-bfe1-7389d6a72cad
      legend: {visible: show, position: bottom}
      type: bar
      mode: stacked
  - id: fde337d5-a199-4d5f-91e2-bda3b43190fb
    title: Cost per user
    size: {w: 16, h: 16}
    position: {x: 32, y: 16}
    esql:
      query: "FROM aws_billing.cur_latest\\n| WHERE aws_billing.cur.line_item.type
        == \\"Usage\\" and aws_billing.cur.bill.billing_period_start_date == DATE_TRUNC(1
        month , NOW())\\n| STATS sum_line_item_unblended_cost = SUM(aws_billing.cur.line_item.unblended_cost)
        by aws_billing.cur.resource_tags.aws_created_by, aws_billing.cur.bill.billing_period_start_date\\
        \\  \\n| SORT sum_line_item_unblended_cost DESC\\n| rename sum_line_item_unblended_cost
        as `Unblended Cost`"
      time_field: '@timestamp'
      dimension: {id: 4a0385c5-c6f7-b30d-bb9d-548f862fd74c, field: \n\
          aws_billing.cur.bill.billing_period_start_date, label: Month}
      metrics:
      - {id: 67fac93e-eb3b-527e-8595-152adda99cfa, field: Unblended Cost}
      breakdown: {id: f0c6e749-91b9-9165-0cda-210f5ef506c6, field: \n\
          aws_billing.cur.resource_tags.aws_created_by, label: Created By}
      id: 43286847-236a-5273-ebb5-a8063e9d2274
      legend: {visible: show, position: bottom}
      type: bar
      mode: stacked
""")
