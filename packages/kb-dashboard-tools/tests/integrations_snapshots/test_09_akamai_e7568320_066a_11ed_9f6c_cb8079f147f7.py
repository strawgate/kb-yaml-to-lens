"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/akamai/kibana/dashboard/akamai-e7568320-066a-11ed-9f6c-cb8079f147f7.json`."""
    assert integrations_yaml_for('packages/akamai/kibana/dashboard/akamai-e7568320-066a-11ed-9f6c-cb8079f147f7.json') == snapshot("""\
dashboards:
- name: '[Akamai SIEM] Akamai Overview'
  id: akamai-e7568320-066a-11ed-9f6c-cb8079f147f7
  description: Overview of Akamai SIEM events
  settings:
    margins: true
    sync: {tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: akamai.siem}
  controls:
  - id: 977a011f-3b78-a6c6-c54d-857423255ee1
    label: Akamai SIEM Rule Tags
    type: options
    field: akamai.siem.rules.ruleTags
    fill_width: false
    preselected: []
    data_view: logs-*
  - id: 98223a9a-4699-7a7c-1e78-b2e2fd36f060
    label: Akamai SIEM Rule Actions
    type: options
    field: akamai.siem.rules.ruleActions
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 256bd35d-3cea-4120-b3a4-27cd50f07aa3
    title: Rule Tags
    size: {w: 24, h: 8}
    position: {x: 0, y: 0}
    lens:
      id: f85727c9-7944-42c0-db4a-b7c8b7cdaca0
      type: treemap
      data_view: logs-*
      metric: {id: 3c2bc97d-1a0d-764c-e652-addeb8aaff00, aggregation: count}
      breakdowns:
      - {id: 5a2cbf5d-a23a-9792-32fd-606113538be3, type: values, field: \n\
          TODO_field}
  - id: bc61d3aa-5fd7-4d05-83a5-a362df834d27
    title: Rule Actions
    size: {w: 24, h: 8}
    position: {x: 24, y: 0}
    lens:
      id: f85727c9-7944-42c0-db4a-b7c8b7cdaca0
      type: treemap
      data_view: logs-*
      metric: {id: 3c2bc97d-1a0d-764c-e652-addeb8aaff00, aggregation: count}
      breakdowns:
      - {id: 5a2cbf5d-a23a-9792-32fd-606113538be3, type: values, field: \n\
          TODO_field}
  - id: 2a92ba28-401c-445d-bd11-b824a0645742
    title: Requests Over Time
    size: {w: 48, h: 8}
    position: {x: 0, y: 8}
    lens:
      data_view: logs-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: 9f4271c9-8f3e-c9b0-34f6-bff29ab2d624
      legend: {visible: show}
      type: line
  - id: fc9bec32-2478-4e5f-bb13-aaf06398adf8
    title: Response Bytes Over Time
    size: {w: 48, h: 8}
    position: {x: 0, y: 16}
    lens:
      data_view: logs-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: 9f4271c9-8f3e-c9b0-34f6-bff29ab2d624
      legend: {visible: show}
      type: line
  - id: f1d059ce-7994-41a3-a720-ba39c3ff96d0
    title: Akamai Bot Score Over Time
    size: {w: 48, h: 8}
    position: {x: 0, y: 24}
    lens:
      data_view: logs-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: 9f4271c9-8f3e-c9b0-34f6-bff29ab2d624
      legend: {visible: show}
      type: line
  - id: f709b8b5-2287-4685-8534-36b839a2d698
    title: User Risk Score
    size: {w: 24, h: 12}
    position: {x: 0, y: 32}
    lens:
      data_view: logs-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: 3e2662df-beb9-b4f7-abbb-710f4699c043
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: b9638e51-f009-4475-b1aa-4f10bbdea9e7
    title: User Risk Status
    size: {w: 24, h: 12}
    position: {x: 24, y: 32}
    lens:
      data_view: logs-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: 3e2662df-beb9-b4f7-abbb-710f4699c043
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: a0c366c4-a72a-4621-b6e5-b7f588459d66
    title: Source Country
    size: {w: 24, h: 30}
    position: {x: 0, y: 44}
    lens:
      id: 05254931-9ef7-c314-b169-0ab5eab4c6ed
      type: metric
      data_view: logs-*
      primary: {id: bb074a6a-e029-66f8-5c5a-a387269e9b58, aggregation: count}
  - id: c9103a68-33ca-40a7-8a39-1e8f81c4a26c
    title: Top 10 URL Domains
    size: {w: 24, h: 15}
    position: {x: 24, y: 44}
    lens:
      id: f85727c9-7944-42c0-db4a-b7c8b7cdaca0
      type: treemap
      data_view: logs-*
      metric: {id: 3c2bc97d-1a0d-764c-e652-addeb8aaff00, aggregation: count}
      breakdowns:
      - {id: 5a2cbf5d-a23a-9792-32fd-606113538be3, type: values, field: \n\
          TODO_field}
  - id: c0e48432-edd2-4ac8-a6af-013796656aa4
    title: Top 10 Source County Codes
    size: {w: 24, h: 15}
    position: {x: 24, y: 59}
    lens:
      id: f85727c9-7944-42c0-db4a-b7c8b7cdaca0
      type: treemap
      data_view: logs-*
      metric: {id: 3c2bc97d-1a0d-764c-e652-addeb8aaff00, aggregation: count}
      breakdowns:
      - {id: 5a2cbf5d-a23a-9792-32fd-606113538be3, type: values, field: \n\
          TODO_field}
""")
