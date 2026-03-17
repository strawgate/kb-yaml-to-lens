"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/aws/kibana/dashboard/aws-07d67a60-d872-11eb-8220-c9141cc1b15c.json`."""
    assert integrations_yaml_for('packages/aws/kibana/dashboard/aws-07d67a60-d872-11eb-8220-c9141cc1b15c.json') == snapshot("""\
dashboards:
- name: '[Metrics AWS] Kinesis Overview'
  id: aws-07d67a60-d872-11eb-8220-c9141cc1b15c
  description: Overview of Amazon Kinesis Metrics
  settings: {margins: true, titles: true}
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: aws.kinesis}
  controls:
  - id: b8d6fa26-09b0-9d29-f62e-d4235ab4e386
    label: Account Names
    type: options
    field: cloud.account.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: a5336d45-fc13-e3f4-8239-c2f36cb35474
    label: Regions
    type: options
    field: cloud.region
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: d70ede1a-6e3d-ae95-9e98-9539e7d99bb5
    label: Availability Zones
    type: options
    field: cloud.availability_zone
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: bd25352f-1240-391d-008c-e39b4af370d2
    label: Stream Names
    type: options
    field: aws.dimensions.StreamName
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 84bfd8e4-fcfe-4985-8e80-f840c190787c
    title: Stream Count
    hide_title: true
    size: {w: 12, h: 6}
    position: {x: 0, y: 0}
    lens:
      id: ae725493-ad8d-a3a9-53f6-33e4b2bcce4b
      type: metric
      data_view: metrics-*
      primary: {id: bb074a6a-e029-66f8-5c5a-a387269e9b58, aggregation: count}
  - id: d2561e5f-82df-4c7e-940d-e443263a5761
    title: Incoming Bytes
    hide_title: true
    size: {w: 19, h: 6}
    position: {x: 12, y: 0}
    lens:
      id: ae725493-ad8d-a3a9-53f6-33e4b2bcce4b
      type: metric
      data_view: metrics-*
      primary: {id: bb074a6a-e029-66f8-5c5a-a387269e9b58, aggregation: count}
  - id: fe687607-118e-4b28-87d2-770bacc39c16
    title: Average Get Records Bytes
    hide_title: true
    size: {w: 17, h: 6}
    position: {x: 31, y: 0}
    lens:
      id: ae725493-ad8d-a3a9-53f6-33e4b2bcce4b
      type: metric
      data_view: metrics-*
      primary: {id: bb074a6a-e029-66f8-5c5a-a387269e9b58, aggregation: count}
  - id: bcb7cf5d-0f3e-42e4-a85b-fcf8aaf0272f
    title: Incoming Data Label
    hide_title: true
    size: {w: 4, h: 11}
    position: {x: 0, y: 6}
    markdown: {content: Incoming Data, font_size: 24, links_in_new_tab: false}
  - id: 35950b92-e435-4d8e-939f-729865b86d05
    title: Incoming Bytes per Stream
    size: {w: 22, h: 11}
    position: {x: 4, y: 6}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: ef1f9b18-05dd-4dad-aaf4-f0c93363b82a
    title: Incoming Records per Stream
    size: {w: 22, h: 11}
    position: {x: 26, y: 6}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: ca087394-b593-4315-96fc-91d001763436
    title: Outgoing Data Label
    hide_title: true
    size: {w: 4, h: 11}
    position: {x: 0, y: 17}
    markdown: {content: Outgoing Data, font_size: 24, links_in_new_tab: false}
  - id: cebc0c74-fbe5-4dd3-ab4e-a3957bc27b57
    title: Get Records Bytes per Stream
    size: {w: 22, h: 11}
    position: {x: 4, y: 17}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: 0de4ba03-7578-4e58-a11a-c9a3f189c737
    title: Get Records per Stream
    size: {w: 22, h: 11}
    position: {x: 26, y: 17}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: 31b1f250-ed1f-4f0f-a6c1-2b0c3b89f44e
    title: latency label
    hide_title: true
    size: {w: 4, h: 17}
    position: {x: 0, y: 28}
    markdown: {content: Latency, font_size: 24, links_in_new_tab: false}
  - id: 8b7a3327-5e7b-497e-81ad-44c4a79404c1
    title: Put Records Latency
    hide_title: true
    size: {w: 22, h: 6}
    position: {x: 4, y: 28}
    lens:
      id: ae725493-ad8d-a3a9-53f6-33e4b2bcce4b
      type: metric
      data_view: metrics-*
      primary: {id: bb074a6a-e029-66f8-5c5a-a387269e9b58, aggregation: count}
  - id: ba88b57d-1f5f-40f0-8c41-2c0f28840ba3
    title: Get Records Latency
    hide_title: true
    size: {w: 22, h: 6}
    position: {x: 26, y: 28}
    lens:
      id: ae725493-ad8d-a3a9-53f6-33e4b2bcce4b
      type: metric
      data_view: metrics-*
      primary: {id: bb074a6a-e029-66f8-5c5a-a387269e9b58, aggregation: count}
  - id: 0bc876e8-94df-413b-8297-a6059a876e2c
    title: Put Records Latency
    size: {w: 22, h: 11}
    position: {x: 4, y: 34}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: 45c140bc-8782-476c-8f2e-8713a1e39dfe
    title: Get Records Latency
    size: {w: 22, h: 11}
    position: {x: 26, y: 34}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: e4a85e33-bbc8-4476-a845-27b2ac3347ac
    title: Get Records Iterator Age (ms)
    size: {w: 44, h: 11}
    position: {x: 4, y: 45}
    lens:
      data_view: metrics-*
      metrics:
      - {id: cdceb520-d498-363b-8576-f1288ef35443, aggregation: count}
      id: b4d51e9f-25f4-63a7-db21-1152cb00b057
      legend: {visible: show}
      type: line
      appearance:
        x_axis: {title: timestamp}
        y_left_axis:
          title: false
          extent: {mode: data_bounds}
  - id: 360ef36d-2399-41e7-8f5a-b3c1406dedc7
    title: iterator age label
    hide_title: true
    size: {w: 4, h: 11}
    position: {x: 0, y: 45}
    markdown: {content: Iterator Age, font_size: 24, links_in_new_tab: false}
""")
