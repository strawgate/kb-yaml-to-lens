"""Integrations decompile inline snapshot."""

from collections.abc import Callable

import pytest
from inline_snapshot import snapshot


@pytest.mark.integrations
def test_snapshot(integrations_yaml_for: Callable[[str], str]) -> None:
    """Snapshot decompile YAML for `packages/aws/kibana/dashboard/aws-383d4630-63df-11ed-be08-4b4db5223139.json`."""
    assert integrations_yaml_for('packages/aws/kibana/dashboard/aws-383d4630-63df-11ed-be08-4b4db5223139.json') == snapshot("""\
dashboards:
- name: '[Logs AWS] Inspector Vulnerabilities'
  id: aws-383d4630-63df-11ed-be08-4b4db5223139
  description: Overview of AWS Inspector Vulnerabilities.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: aws.inspector}
  controls:
  - id: c5f7dec9-e883-6c6a-c3b8-484f6f8407bc
    label: AWS Inspector Findings Severity
    type: options
    field: aws.inspector.severity
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: dd29b1be-2713-4758-bef1-9c310b4a8e1a
    title: Top 10 Vulnerability CVSS Source with Highest CVSS Score [Logs \n\
      Inspector]
    size: {w: 24, h: 15}
    position: {x: 0, y: 4}
    lens:
      type: datatable
      id: ff3db9f8-54a9-56de-533c-cf90d77778de
      data_view: logs-*
      metrics:
      - {id: a6b60d33-c9b1-1baa-c372-192adbc3b6c8, label: CVSS Score, \n\
          aggregation: max, field: vulnerability.score.base}
      breakdowns:
      - {id: 2a08b154-3aa2-37b1-46ac-cc038a8119a7, type: values, size: 10, field: \n\
          aws.inspector.package_vulnerability_details.cvss.source}
  - id: 896a3082-c44b-456c-a144-0ce096c0a213
    title: Vulnerabilities Package Name with Most Critical Findings [Logs \n\
      Inspector]
    size: {w: 24, h: 15}
    position: {x: 24, y: 4}
    lens:
      type: datatable
      id: c0b3baa0-2609-f5ab-770b-10d4877118f2
      data_view: logs-*
      metrics:
      - {id: 98812427-03b3-5ce3-bf7f-5dd34a15ecfd, label: Critical Severity, \n\
          aggregation: count, field: aws.inspector.severity}
      breakdowns:
      - {id: 4e6fabca-f827-69ea-1cd3-4606a2b3ef62, type: values, size: 10, field: \n\
          package.name}
      - {id: 9deeebda-6439-74f2-3505-d747d43458dd, type: values, size: 10, field: \n\
          cloud.account.id}
  - id: 1bd92e14-3902-4a5b-bc32-86952f9fdfb0
    title: Findings Package Vulnerability Essential Details [Logs Inspector]
    size: {w: 48, h: 15}
    position: {x: 0, y: 19}
    search: {saved_search_id: TODO_saved_search_id}
  - id: 858f6288-7c54-4d7a-be33-374a9d79d1e4
    title: Dashboards [Logs Inspector]
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: '[Inspector Findings Overview Dashboard](#/dashboard/aws-131a1550-5a0b-11ed-a807-bd2da8f2e79b)
        | [Inspector Severity Dashboard](#/dashboard/aws-60881ab0-63e0-11ed-be08-4b4db5223139)
        | **Inspector Vulnerabilities Dashboard** | [Inspector EC2 and ECR Overview
        Dashboard](#/dashboard/aws-63984b70-63e1-11ed-be08-4b4db5223139)  ', \n\
        font_size: 13, links_in_new_tab: true}
""")
