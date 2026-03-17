"""Opt-in integrations-backed decompiler tests."""

# ruff: noqa: E501

import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from inline_snapshot import snapshot
from ruamel.yaml import YAML

from kb_dashboard_tools.decompile import decompile_dashboard

from .integrations_targets import INTEGRATIONS_PINNED_SHA


def _iter_dashboard_objects(path: Path) -> Iterator[dict[str, Any]]:
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.ndjson':
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if len(stripped) == 0:
                continue
            obj = json.loads(stripped)
            if isinstance(obj, dict) and obj.get('type') == 'dashboard':
                yield cast('dict[str, Any]', obj)
        return

    parsed = json.loads(text)
    if isinstance(parsed, dict):
        if parsed.get('type') == 'dashboard':
            yield cast('dict[str, Any]', parsed)
            return
        objects = parsed.get('objects')
        if isinstance(objects, list):
            for obj in objects:
                if isinstance(obj, dict) and obj.get('type') == 'dashboard':
                    yield cast('dict[str, Any]', obj)
            return
    if isinstance(parsed, list):
        for obj in parsed:
            if isinstance(obj, dict) and obj.get('type') == 'dashboard':
                yield cast('dict[str, Any]', obj)


def _decompile_yaml_text(dashboard: dict[str, Any]) -> str:
    canonical = json.loads(json.dumps(decompile_dashboard(dashboard)))
    yaml = YAML(typ='safe')
    yaml_any = cast('Any', yaml)
    yaml_any.sort_base_mapping_type_on_output = False
    stream = io.StringIO()
    yaml.dump(canonical, stream)
    return stream.getvalue()


@pytest.fixture(scope='session')
def integrations_target_files(integrations_repo_path: Path, integrations_pinned_sha: str) -> dict[str, Path]:
    """Resolve hardcoded dashboard files to test from integrations fixture clone."""
    if integrations_pinned_sha != INTEGRATIONS_PINNED_SHA:
        message_template = 'inline snapshots are pinned to {pinned}; got {got}. Use --integrations-sha {pinned}.'
        message = message_template.format(pinned=INTEGRATIONS_PINNED_SHA, got=integrations_pinned_sha)
        pytest.skip(message)

    targets = [
        'packages/1password/kibana/dashboard/1password-audit-events-full-dashboard.json',
        'packages/1password/kibana/dashboard/1password-item-usages-full-dashboard.json',
        'packages/1password/kibana/dashboard/1password-signin-attempts-full-dashboard.json',
        'packages/abnormal_security/kibana/dashboard/abnormal_security-37ed5d19-c753-43a0-b0a2-f8e6437ddfe5.json',
        'packages/abnormal_security/kibana/dashboard/abnormal_security-f6562262-e429-470d-af45-4c80afdcf664.json',
        'packages/activemq/kibana/dashboard/activemq-8a0cbc90-f916-11ec-9736-016ee09668f5.json',
        'packages/activemq/kibana/dashboard/activemq-f98d0c50-f916-11ec-9736-016ee09668f5.json',
        'packages/airflow/kibana/dashboard/airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b.json',
        'packages/akamai/kibana/dashboard/akamai-e7568320-066a-11ed-9f6c-cb8079f147f7.json',
        'packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1.json',
        'packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3.json',
        'packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json',
        'packages/apache/kibana/dashboard/apache-Metrics-Apache-HTTPD-server-status.json',
        'packages/apache_otel/kibana/dashboard/apache_otel-overview.json',
        'packages/apache_spark/kibana/dashboard/apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156.json',
        'packages/apache_tomcat/kibana/dashboard/apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969.json',
        'packages/arista_ngfw/kibana/dashboard/arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798.json',
        'packages/armis/kibana/dashboard/armis-68592f5a-9c7b-4398-a723-510d5e48a8b1.json',
        'packages/auditd/kibana/dashboard/auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb.json',
        'packages/auth0/kibana/dashboard/auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf.json',
        'packages/aws/kibana/dashboard/aws-07d67a60-d872-11eb-8220-c9141cc1b15c.json',
        'packages/aws/kibana/dashboard/aws-383d4630-63df-11ed-be08-4b4db5223139.json',
        'packages/aws_billing/kibana/dashboard/aws_billing-01aace34-9219-4c6c-80a9-b903af48950f.json',
        'packages/azure/kibana/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5.json',
        'packages/azure_openai/kibana/dashboard/azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3.json',
        'packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json',
        'packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json',
        'packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json',
        'packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json',
        'packages/system/kibana/dashboard/system-Metrics-system-overview.json',
    ]
    resolved = {rel: integrations_repo_path / rel for rel in targets}
    missing = [path for path in resolved.values() if not path.exists()]
    if missing:
        pytest.fail(f'missing hardcoded integrations dashboards: {missing}')
    return resolved


def _yaml_for_target(source_rel: str, integrations_target_files: dict[str, Path]) -> str:
    source_path = integrations_target_files[source_rel]
    first_dashboard = next(_iter_dashboard_objects(source_path), None)
    if first_dashboard is None:
        pytest.fail(f'no dashboard object found in {source_rel}')
    return _decompile_yaml_text(first_dashboard)


@pytest.mark.integrations
def test_integrations_snapshot_01_1password_audit_events_full_dashboard(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/1password/kibana/dashboard/1password-audit-events-full-dashboard.json`."""
    assert _yaml_for_target(
        'packages/1password/kibana/dashboard/1password-audit-events-full-dashboard.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: Audit Events [1Password]
  id: 1password-audit-events-full-dashboard
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: a9a9a507-ae79-422c-ac05-2f4d9a2bb5e6
    title: ''
    size: {w: 31, h: 15}
    position: {x: 0, y: 0}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_a9a9a507-ae79-422c-ac05-2f4d9a2bb5e6'}
  - id: 5191f658-f717-49ec-9d3c-7c881c07a502
    title: ''
    size: {w: 17, h: 15}
    position: {x: 31, y: 0}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: 7521b1b8-37a6-4890-a450-631bf653fb93
    title: Audit Events over time [1Password]
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
  - id: c76ab1dd-2177-4b19-8d0f-a44cd7280a79
    title: ''
    size: {w: 24, h: 11}
    position: {x: 24, y: 15}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: e1868285-62c1-b8c0-a668-0883f6013da8
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 1815f4d9-4f4d-5e1a-6d48-db1a08531383, type: values, size: 5, field: \n\
          user.id}
  - id: 6785d29f-971b-445d-8997-dd97f302814d
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 26}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 06d37e60-cf62-1329-cbe0-97ca8d3e11ed
      data_view: logs-*
      metrics:
      - {id: a27df444-1804-d42c-480f-4a2e1e2bcd2f, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 104c363e-2b3a-4497-1bc0-00d896626b28, type: values, size: 5, field: \n\
          event.action}
  - id: 60da356b-c843-4d41-8bf4-04e04ef77734
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 26}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 28a3257e-2b4f-f978-707b-247bbfa4fb47
      data_view: logs-*
      metrics:
      - {id: a27df444-1804-d42c-480f-4a2e1e2bcd2f, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 0f607a96-502a-16a1-cf06-275a8d952efd, type: values, size: 5, field: \n\
          onepassword.object_type}
""")


@pytest.mark.integrations
def test_integrations_snapshot_02_1password_item_usages_full_dashboard(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/1password/kibana/dashboard/1password-item-usages-full-dashboard.json`."""
    assert _yaml_for_target(
        'packages/1password/kibana/dashboard/1password-item-usages-full-dashboard.json',
        integrations_target_files,
    ) == snapshot("""\
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


@pytest.mark.integrations
def test_integrations_snapshot_03_1password_signin_attempts_full_dashboard(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/1password/kibana/dashboard/1password-signin-attempts-full-dashboard.json`."""
    assert _yaml_for_target(
        'packages/1password/kibana/dashboard/1password-signin-attempts-full-dashboard.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: Sign-in Attempts [1Password]
  id: 1password-signin-attempts-full-dashboard
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 944e346e-36df-430b-9734-5d91da79bdc1
    title: ''
    size: {w: 31, h: 15}
    position: {x: 0, y: 0}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_944e346e-36df-430b-9734-5d91da79bdc1'}
  - id: 5a635dbb-4cb6-46f8-9d4c-dd12078b184f
    title: ''
    size: {w: 17, h: 15}
    position: {x: 31, y: 0}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: b778af01-c0b6-4b57-a675-d39d1c6db832
    title: Sign-in Attempts unsuccessful [1Password]
    size: {w: 11, h: 9}
    position: {x: 0, y: 15}
    lens:
      id: 7fe11da5-5ad7-9c76-e9f0-66cf6fbb22d7
      type: metric
      data_view: logs-*
      primary: {id: 5880480d-6ce5-b13e-4a11-0bf4d6444efc, label: Failed Signin \n\
          Attempts, aggregation: count, field: ___records___}
  - id: 51433376-546a-492a-906e-9ca7f5d34f68
    title: Sign-in Attempts over time [1Password]
    size: {w: 20, h: 9}
    position: {x: 11, y: 15}
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
  - id: 8f8ae43c-e8d4-4425-b418-224a7db57e86
    title: Sign-in Attempts categories over time [1Password]
    size: {w: 17, h: 9}
    position: {x: 31, y: 15}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 208bfe09-9d04-9a3c-f6f5-80128d02dbe2, type: values, size: \n\
          10, field: event.action}
      id: e32d4517-ebb2-fe33-a04a-291e3c4c31ff
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        y_left_axis:
          title: Count
          extent: {mode: data_bounds}
      mode: stacked
  - id: 63f0a044-8a96-4664-9a05-cb8f4503b133
    title: Sign-in Attempts hot users [1Password]
    size: {w: 48, h: 9}
    position: {x: 0, y: 24}
    lens:
      type: datatable
      id: 2bc68fca-a9aa-86c0-039b-1b4c7eadef8c
      data_view: logs-*
      metrics:
      - {id: a27df444-1804-d42c-480f-4a2e1e2bcd2f, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 6f07e67c-e270-6bb6-1ac6-8cff766e9df0, type: values, size: 10, field: \n\
          user.id}
      - {id: 542b05be-ab2d-11ca-9cb7-74e8a5562fa4, type: values, size: 10, field: \n\
          user.full_name}
      - {id: 2b90eb88-cd3a-1cc2-01f7-158e7a7be000, type: values, size: 10, field: \n\
          user.email}
""")


@pytest.mark.integrations
def test_integrations_snapshot_04_abnormal_security_37ed5d19_c753_43a0_b0a2_f8e6437ddfe5(
    integrations_target_files: dict[str, Path],
) -> None:
    """Snapshot decompile YAML for `packages/abnormal_security/kibana/dashboard/abnormal_security-37ed5d19-c753-43a0-b0a2-f8e6437ddfe5.json`."""
    assert _yaml_for_target(
        'packages/abnormal_security/kibana/dashboard/abnormal_security-37ed5d19-c753-43a0-b0a2-f8e6437ddfe5.json',
        integrations_target_files,
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


@pytest.mark.integrations
def test_integrations_snapshot_05_abnormal_security_f6562262_e429_470d_af45_4c80afdcf664(
    integrations_target_files: dict[str, Path],
) -> None:
    """Snapshot decompile YAML for `packages/abnormal_security/kibana/dashboard/abnormal_security-f6562262-e429-470d-af45-4c80afdcf664.json`."""
    assert _yaml_for_target(
        'packages/abnormal_security/kibana/dashboard/abnormal_security-f6562262-e429-470d-af45-4c80afdcf664.json',
        integrations_target_files,
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


@pytest.mark.integrations
def test_integrations_snapshot_06_activemq_8a0cbc90_f916_11ec_9736_016ee09668f5(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/activemq/kibana/dashboard/activemq-8a0cbc90-f916-11ec-9736-016ee09668f5.json`."""
    assert _yaml_for_target(
        'packages/activemq/kibana/dashboard/activemq-8a0cbc90-f916-11ec-9736-016ee09668f5.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics ActiveMQ] Broker'
  id: activemq-8a0cbc90-f916-11ec-9736-016ee09668f5
  description: The dashboard presents metric data describing ActiveMQ broker. \n\
    Metrics show statistics of enqueued and dequeued messages, consumers, \n\
    producers and memory usage (broker, store, temp).
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: activemq.broker}
  panels:
  - id: 0bb4a077-65fc-4d3a-a6e6-39a7ec01e01f
    title: Broker Messages [Metrics ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 90aa54b0-7456-147a-4dcb-fe7cd36a851e, label: Maximum of \n\
          activemq.broker.messages.dequeue.count, aggregation: max, field: \n\
          activemq.broker.messages.dequeue.count}
      - {id: 046be75c-f3bd-4433-04c2-e1bd4eed63cc, label: Maximum of \n\
          activemq.broker.messages.enqueue.count, aggregation: max, field: \n\
          activemq.broker.messages.enqueue.count}
      - {id: 046be75c-f3bd-4433-04c2-e1bd4eed63cc, label: Maximum of \n\
          activemq.broker.messages.enqueue.count, aggregation: max, field: \n\
          activemq.broker.messages.enqueue.count}
      id: ecb853cd-4d39-fc01-5c43-9aaf3bdb4937
      legend: {visible: show, position: bottom, show_single_series: true}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 9719ed38-5a0d-4132-b504-1bae29b20369
    title: Broker Consumers/Producers [Metrics ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 24, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: f1d58744-ac02-7dba-68a5-0f6765f114ff, label: Producers, aggregation: \n\
          max, field: activemq.broker.producers.count}
      - {id: a8028813-78d9-64ea-0d5a-379279dd848a, label: Consumers, aggregation: \n\
          max, field: activemq.broker.consumers.count}
      id: 9abc42af-3ca4-38d7-26ae-bd591af09e3e
      legend: {visible: show, position: bottom, show_single_series: true}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 7f00478e-0bf9-409c-89b7-2fc3f4ee50a9
    title: Broker Connections [Metrics ActiveMQ]
    size: {w: 24, h: 18}
    position: {x: 0, y: 15}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 3bb3c5bc-7544-c831-a70a-2fecd9b30ed4, label: Maximum of \n\
          activemq.broker.connections.count, aggregation: max, field: \n\
          activemq.broker.connections.count}
      id: 811e751b-38c8-82e9-71da-09fcd7fe9a23
      legend: {visible: show, position: bottom, show_single_series: true}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: b82bc348-18ce-4a6c-8d6d-4e90340f1690
    title: Broker Memory Usage [Metrics ActiveMQ]
    size: {w: 24, h: 6}
    position: {x: 24, y: 15}
    lens:
      type: gauge
      appearance: {ticks_position: bands}
      id: 2d75fa88-b0bc-f268-5ee4-a552cc075ceb
      data_view: metrics-*
      metric:
        id: ab2845d5-f80c-59b3-000f-4656370799ac
        label: Broker Memory
        format: {type: percent, decimals: 2}
        aggregation: max
        field: activemq.broker.memory.broker.pct
  - id: 3716faab-9aeb-4431-8fab-0fed419689f5
    title: Broker Store Memory Usage [Metrics ActiveMQ]
    size: {w: 24, h: 6}
    position: {x: 24, y: 21}
    lens:
      type: gauge
      appearance: {ticks_position: bands}
      id: f0f726b7-192e-0080-2160-4163ca54b745
      data_view: metrics-*
      metric:
        id: d3546dfc-b2ce-b4fb-6924-3f69aff8a86f
        label: Store Memory
        format: {type: percent, decimals: 2}
        aggregation: max
        field: activemq.broker.memory.store.pct
  - id: c20b98fb-92f8-4933-ac32-18119552b57a
    title: Broker Temp Memory Usage [Metrics ActiveMQ]
    size: {w: 24, h: 6}
    position: {x: 24, y: 27}
    lens:
      type: gauge
      appearance: {ticks_position: bands}
      id: a8027a65-d8e4-752a-fe95-6d6c17521bcc
      data_view: metrics-*
      metric:
        id: d2a399b3-0d58-d676-8293-98d5e27d90f5
        label: Temp Memory
        format: {type: percent, decimals: 2}
        aggregation: max
        field: activemq.broker.memory.temp.pct
""")


@pytest.mark.integrations
def test_integrations_snapshot_07_activemq_f98d0c50_f916_11ec_9736_016ee09668f5(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/activemq/kibana/dashboard/activemq-f98d0c50-f916-11ec-9736-016ee09668f5.json`."""
    assert _yaml_for_target(
        'packages/activemq/kibana/dashboard/activemq-f98d0c50-f916-11ec-9736-016ee09668f5.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Logs ActiveMQ] Log'
  id: activemq-f98d0c50-f916-11ec-9736-016ee09668f5
  description: This dashboard shows application logs collected by the ActiveMQ \n\
    logs integration.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: activemq.log}
  panels:
  - id: b6bdc4b4-745a-4fa2-9928-9f7cb783f5b9
    title: Application Event Results [Logs ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 0, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 9a67312b-1682-a72c-7a73-945c2481482a, type: values, size: \n\
          15, field: log.level}
      id: 28d90856-3822-15b3-584e-59b6b991ecc6
      legend: {visible: show, show_single_series: true}
      type: bar
      appearance:
        y_left_axis: {title: Count}
      mode: stacked
  - id: 843b2c29-7386-41ac-acdd-286021471008
    title: Top Error Callers [Logs ActiveMQ]
    size: {w: 24, h: 15}
    position: {x: 24, y: 0}
    lens:
      type: datatable
      id: a9e2d24a-a220-24e2-4728-b3270adf7626
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: c5578263-cddd-0537-786f-ce84c050ac4e, type: values, size: 10, field: \n\
          activemq.log.caller}
  - id: 58c5e9cf-4342-4a2c-a893-98de182dc283
    title: Application Events [Logs ActiveMQ]
    size: {w: 48, h: 22}
    position: {x: 0, y: 15}
    search: {saved_search_id: TODO_saved_search_id}
""")


@pytest.mark.integrations
def test_integrations_snapshot_08_airflow_1ea4b491_e7a0_42ad_a0f3_7a4b02e1f22b(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/airflow/kibana/dashboard/airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b.json`."""
    assert _yaml_for_target(
        'packages/airflow/kibana/dashboard/airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics Airflow] Overview'
  id: airflow-1ea4b491-e7a0-42ad-a0f3-7a4b02e1f22b
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: airflow.statsd}
  controls:
  - id: e077536e-412b-783d-f0ce-528c5cb595f9
    label: host.hostname
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: f3313a2c-2e29-490e-b586-8d281a96faa4
    title: ''
    hide_title: true
    size: {w: 16, h: 11}
    position: {x: 0, y: 0}
    markdown: {content: "## Apache Airflow\\n\\nThis dashboard provides an overview
        of Apache Airflow performance and health, including Directed Acyclic Graph
        (DAG) run statuses, task execution times, and scheduling delays. Use it to
        monitor workflows, identify bottlenecks, and ensure smooth orchestration of
        data pipelines.", font_size: 12, links_in_new_tab: false}
  - id: 48c3b9c1-81aa-42ff-9572-669c9cf73728
    title: Scheduler heartbeat
    size: {w: 16, h: 11}
    position: {x: 16, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: dfa3d71f-88cc-eb74-70f7-5957db290514
        label: Hearbeats reported
        filter: {kql: '"airflow.scheduler_heartbeat.count": *'}
        aggregation: last_value
        field: airflow.scheduler_heartbeat.count
      id: fc08e1bf-4349-1da5-c007-fb108c7c56c1
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 45fc2d9e-d648-4ac4-b339-c013caad550b
    title: Scheduler tasks
    size: {w: 16, h: 11}
    position: {x: 32, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 3ba057ff-541f-46d4-b0a4-55823631880b
        label: Executable
        filter: {kql: '"airflow.task_executable.value": *'}
        aggregation: last_value
        field: airflow.task_executable.value
      - id: 0fb96067-0caf-95ee-3232-88fc0034b682
        label: Starving
        filter: {kql: '"airflow.task_starving.value": *'}
        aggregation: last_value
        field: airflow.task_starving.value
      id: da66f719-5d83-60bf-833d-ca97e5b6ee37
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Tasks}
      mode: stacked
  - id: ad7f08e5-4141-4c17-a619-8f7b370d1b78
    title: Mean DAG run schedule delay
    size: {w: 24, h: 15}
    position: {x: 0, y: 11}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 0e3e717a-5db2-f6ec-0268-4c905461ae63
        label: Mean delay
        format: {type: duration, decimals: 0, compact: true}
        filter: {kql: '"airflow.dag_schedule_delay.mean": *'}
        aggregation: last_value
        field: airflow.dag_schedule_delay.mean
      breakdown: {id: ed2ff3f5-ca41-eb1b-c4ff-c871637bb3a4, type: values, size: \n\
          5, field: airflow.dag_id}
      id: 041d8875-b01e-f64f-dbc0-58218093ae9d
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      mode: stacked
  - id: 4c9299a4-d135-4340-81f2-69da0e6602c8
    title: DAG bag size
    size: {w: 24, h: 15}
    position: {x: 24, y: 11}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 02519b17-0141-dfbb-3f09-034009a85593
        label: DAGs
        filter: {kql: '"airflow.dag_bag_size.value": *'}
        aggregation: last_value
        field: airflow.dag_bag_size.value
      id: 97dd1732-a6d4-caaf-ba38-ae1c95e71a1c
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 3eea737e-6f17-49f0-9c07-624055b9f41b
    title: Mean Successful DAG duration
    size: {w: 24, h: 15}
    position: {x: 0, y: 26}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 65204d5c-b2ce-904f-f943-0d2ca74b50d3
        label: Duration
        format: {type: duration, decimals: 1, compact: true}
        filter: {kql: '"airflow.success_dag_duration.mean": *'}
        aggregation: last_value
        field: airflow.success_dag_duration.mean
      breakdown: {id: ed2ff3f5-ca41-eb1b-c4ff-c871637bb3a4, type: values, size: \n\
          5, field: airflow.dag_id}
      id: edc5cd15-6de8-ad0c-da69-6ecae321c1cb
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      mode: stacked
  - id: 13a49310-419c-4666-9348-db529b9ed17b
    title: Mean Failed DAG duration
    size: {w: 24, h: 15}
    position: {x: 24, y: 26}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 4072bc17-aca6-7d26-8790-096c2f6ee837
        label: Duration
        format: {type: duration, decimals: 1, compact: true}
        filter: {kql: '"airflow.failed_dag_duration.mean": *'}
        aggregation: last_value
        field: airflow.failed_dag_duration.mean
      breakdown: {id: ed2ff3f5-ca41-eb1b-c4ff-c871637bb3a4, type: values, size: \n\
          5, field: airflow.dag_id}
      id: 5e6f85ee-9b0b-9585-de83-a2ebd34b4d9b
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      mode: stacked
  - id: e6c5b713-d20c-4ec1-9193-68caded2fc98
    title: DAG total parse time
    size: {w: 24, h: 15}
    position: {x: 0, y: 41}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 9276a7c0-89dc-ba0c-2ad1-a652d6d8a850
        label: DAG Total parse time
        format: {type: duration, decimals: 1, compact: true}
        filter: {kql: '"airflow.dag_total_parse_time.value": *'}
        aggregation: last_value
        field: airflow.dag_total_parse_time.value
      id: 5e0af697-9925-6231-ddfb-485ecc2e47cf
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Duration}
      mode: stacked
  - id: b65e9e91-49ee-4559-981c-c1cff459bb54
    title: DAG import errors
    size: {w: 24, h: 15}
    position: {x: 24, y: 41}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 63287037-d549-41e9-c231-edc99a541e8b
        label: Errors
        filter: {kql: '"airflow.dag_import_errors.value": *'}
        aggregation: last_value
        field: airflow.dag_import_errors.value
      id: cb895526-0e91-12ae-d91a-acb581cf8b0d
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: c18206fd-60a2-40be-bbb7-e0210b9be725
    title: Executor tasks
    size: {w: 24, h: 15}
    position: {x: 0, y: 56}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 4e589d4d-8809-4947-c5b4-f7c1a45d4d64
        label: Running
        filter: {kql: '"airflow.executor_running_tasks.value": *'}
        aggregation: last_value
        field: airflow.executor_running_tasks.value
      - id: b003343b-b68b-7f77-2e66-b4264ac8197f
        label: Queued
        filter: {kql: '"airflow.executor_queued_tasks.value": *'}
        aggregation: last_value
        field: airflow.executor_queued_tasks.value
      - id: 77310ce6-9cb1-436b-9a58-6cb3fff97956
        label: Open Slots
        filter: {kql: '"airflow.executor_open_slots.value": *'}
        aggregation: last_value
        field: airflow.executor_open_slots.value
      id: 969152c4-3545-9831-d783-55fb7ce185b3
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Tasks}
      mode: stacked
  - id: 04bbf1c9-724e-4f4b-a671-c0540e552d8d
    title: Pool task slots
    size: {w: 24, h: 15}
    position: {x: 24, y: 56}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 4cabc59c-f0a1-233b-0249-0d74642887cd
        label: Open
        filter: {kql: '"airflow.pool_open_slots.value": *'}
        aggregation: last_value
        field: airflow.pool_open_slots.value
      - id: de7b4d68-9eb0-04c5-1a64-b32d6a4106ee
        label: Queued
        filter: {kql: '"airflow.pool_queued_slots.value": *'}
        aggregation: last_value
        field: airflow.pool_queued_slots.value
      - id: b8b51524-4716-341c-4a05-23f5d8404b39
        label: Running
        filter: {kql: '"airflow.pool_running_slots.value": *'}
        aggregation: last_value
        field: airflow.pool_running_slots.value
      - id: 778dd06a-9137-4719-9b60-b8711db86e85
        label: Starving
        filter: {kql: '"airflow.pool_starving_tasks.value": *'}
        aggregation: last_value
        field: airflow.pool_starving_tasks.value
      breakdown: {id: e792cd4a-4e21-9df1-3726-8e09283027fe, type: values, size: \n\
          3, field: airflow.pool_name}
      id: 846c670c-6d7a-b4cc-d62c-a81aa6ff7ceb
      legend: {visible: show, width: extra_large, truncate_labels: 2}
      type: bar
      appearance:
        y_left_axis: {title: Slots}
      mode: stacked
""")


@pytest.mark.integrations
def test_integrations_snapshot_09_akamai_e7568320_066a_11ed_9f6c_cb8079f147f7(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/akamai/kibana/dashboard/akamai-e7568320-066a-11ed-9f6c-cb8079f147f7.json`."""
    assert _yaml_for_target(
        'packages/akamai/kibana/dashboard/akamai-e7568320-066a-11ed-9f6c-cb8079f147f7.json',
        integrations_target_files,
    ) == snapshot("""\
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


@pytest.mark.integrations
def test_integrations_snapshot_10_amazon_security_lake_0d2d7a60_2472_11ee_8d80_89e82659e0f1(
    integrations_target_files: dict[str, Path],
) -> None:
    """Snapshot decompile YAML for `packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1.json`."""
    assert _yaml_for_target(
        'packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-0d2d7a60-2472-11ee-8d80-89e82659e0f1.json',
        integrations_target_files,
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


@pytest.mark.integrations
def test_integrations_snapshot_11_amazon_security_lake_f21df8e0_249d_11ee_aa05_4dd9349682f3(
    integrations_target_files: dict[str, Path],
) -> None:
    """Snapshot decompile YAML for `packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3.json`."""
    assert _yaml_for_target(
        'packages/amazon_security_lake/kibana/dashboard/amazon_security_lake-f21df8e0-249d-11ee-aa05-4dd9349682f3.json',
        integrations_target_files,
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
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: 11b25773-8889-98ee-ba2b-8b103e85e28e, type: values, size: \n\
          10, field: ocsf.metadata.product.vendor_name}
      id: 6bfabc37-32a1-db52-c092-0d3f3bd2a50f
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
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: fe67ce39-c0f6-4c1f-9511-b76dc7bb3081, type: values, size: \n\
          33, field: ocsf.class_name}
      id: f4230840-8d48-571a-fbcf-83bf5701cb1d
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
      metrics:
      - id: ae00e989-841b-abeb-050c-df11b6f60c56
        label: Count
        format: {type: number, decimals: 0}
        aggregation: count
        field: ___records___
      breakdown: {id: f2917d00-6238-bec3-75a4-0158e156fdb6, type: values, size: \n\
          10, field: ocsf.metadata.product.name}
      id: 1b86d335-7363-8010-e9d9-51b85306818f
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


@pytest.mark.integrations
def test_integrations_snapshot_12_apache_logs_apache_dashboard(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json`."""
    assert _yaml_for_target(
        'packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Logs Apache] Access and error logs'
  id: apache-Logs-Apache-Dashboard
  description: Logs Apache integration dashboard
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [apache.access, apache.error]
  controls:
  - id: 7acd8a6f-d64f-22c6-b1ed-4fa6a18fd97c
    label: Hostname
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 665ee316-bf0f-4182-ab1b-2763a7fffc06
    title: Response codes over time [Logs Apache]
    size: {w: 32, h: 12}
    position: {x: 0, y: 45}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 1eed8a07-2b0b-c18b-dbb4-56b960301da2, type: values, size: \n\
          5, field: http.response.status_code}
      id: 36a3f3e1-ec27-a4c8-1cfa-d568ed431b2d
      legend: {visible: show, show_single_series: true}
      type: bar
      mode: stacked
  - id: 3f8742ea-3414-4259-99d3-83f02bedf868
    title: Operating systems breakdown [Logs Apache]
    size: {w: 16, h: 12}
    position: {x: 32, y: 45}
    lens:
      id: c1c94846-a23f-a236-968a-c21352aa2c11
      type: pie
      appearance: {donut: medium}
      legend: {visible: show}
      data_view: logs-*
      metrics:
      - {id: a2ec6baa-deb0-ed51-ea49-ecda62f4d18d, label: Unique count of \n\
          source.address, aggregation: unique_count, field: source.address}
      breakdowns:
      - {id: 9b452332-016c-bcaa-da7d-3a64576877e8, type: values, size: 5, field: \n\
          user_agent.os.name}
      - {id: d79d6a24-a93f-82d0-e626-686a13d42cfc, type: values, size: 5, field: \n\
          user_agent.os.version}
  - id: b95f2642-7f5e-4cfa-8c1a-ecccf384e840
    title: Top URLs by response code [Logs Apache]
    size: {w: 32, h: 12}
    position: {x: 0, y: 57}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: f180759b-b457-10f9-04cb-f0ee57f419c2
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 8b6266d7-9c02-52e0-f729-9b06c65b3530, type: values, size: 5, field: \n\
          http.response.status_code}
      - {id: 5e69f278-138f-664d-e8bb-1135746e09d1, type: values, size: 5, field: \n\
          url.original}
  - id: 1df4688c-8f4c-455f-a260-bb57e3445861
    title: Browsers breakdown [Logs Apache]
    size: {w: 16, h: 12}
    position: {x: 32, y: 57}
    lens:
      id: 45d02f70-2869-1c3a-cbc6-a21f6608f721
      type: pie
      appearance: {donut: medium}
      legend: {visible: show}
      data_view: logs-*
      metrics:
      - {id: a2ec6baa-deb0-ed51-ea49-ecda62f4d18d, label: Unique count of \n\
          source.address, aggregation: unique_count, field: source.address}
      breakdowns:
      - {id: d4851aa4-86e3-f23c-2c38-2eed2a74a815, type: values, size: 5, field: \n\
          user_agent.name}
      - {id: 9a18218e-26be-a284-a001-d72ea3c56daf, type: values, size: 5, field: \n\
          user_agent.version}
  - id: 4c8d6353-2787-475f-bd46-5b21239aa072
    title: Error logs over time [Logs Apache]
    size: {w: 48, h: 9}
    position: {x: 0, y: 69}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: cce5efe2-b956-597b-69f9-9a771b3a0b2a, type: values, size: \n\
          5, field: log.level}
      id: 0872f3f6-ec5d-4754-5a29-2a9231686cdc
      legend: {visible: show, show_single_series: true}
      type: bar
      mode: stacked
  - id: d9771ad7-cec0-4e4b-a51e-bbc880a8af0d
    title: Unique IPs map [Logs Apache]
    size: {w: 48, h: 15}
    position: {x: 0, y: 30}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
  - id: a39e73b9-4e6c-422e-a7bb-3dbbb53c7274
    title: Apache errors log [Logs Apache]
    size: {w: 48, h: 15}
    position: {x: 0, y: 93}
    search: {saved_search_id: TODO_saved_search_id}
""")


@pytest.mark.integrations
def test_integrations_snapshot_13_apache_metrics_apache_httpd_server_status(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/apache/kibana/dashboard/apache-Metrics-Apache-HTTPD-server-status.json`."""
    assert _yaml_for_target(
        'packages/apache/kibana/dashboard/apache-Metrics-Apache-HTTPD-server-status.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics Apache] Overview'
  id: apache-Metrics-Apache-HTTPD-server-status
  description: Overview of Apache server status
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: apache.status}
  controls:
  - id: 2bb288fa-d4b0-8b0e-caea-8bb16f92be0a
    label: Hostname
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 7b7a1f18-e274-4f4e-a3b3-3760e7896897
    title: Uptime [Metrics Apache]
    size: {w: 16, h: 7}
    position: {x: 0, y: 0}
    lens:
      id: 7fe7c15b-3101-5368-71fb-0b2b787af31d
      type: metric
      data_view: TODO_data_view
      primary:
        id: 6a0b603f-2e53-3418-1d5e-e2eef541f20b
        label: Uptime
        format: {type: duration, decimals: 2}
        aggregation: max
        field: apache.status.uptime.uptime
  - id: bcaad3c3-d62c-44bd-8e76-f00cb8a7f0eb
    title: Total accesses [Metrics Apache]
    size: {w: 16, h: 7}
    position: {x: 16, y: 0}
    lens:
      id: b59cab30-64cf-587e-28d4-0c88937c3670
      type: metric
      data_view: metrics-*
      primary: {id: 683329d5-9fbc-5fd2-c839-6a8b018a9b6c, label: ' Total accesses',
        aggregation: max, field: apache.status.total_accesses}
  - id: ea52006e-efe5-499a-88e7-2843258d6905
    title: Total egress [Metrics Apache]
    size: {w: 16, h: 7}
    position: {x: 32, y: 0}
    lens:
      id: 7ef8a433-10a5-2185-453e-f4788d8e5c99
      type: metric
      data_view: metrics-*
      primary:
        id: edd4edb6-368e-9953-054b-ad2eeac4293f
        label: Total egress
        format: {type: bytes, decimals: 1}
        aggregation: max
        field: apache.status.total_bytes
  - id: 9386f867-d876-448b-b5fb-cc39eefb09cd
    title: Requests per sec [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 22}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 64c7d943-72f7-fe95-19eb-7f57ef3f64b3, label: Requests per sec, \n\
          aggregation: average, field: apache.status.requests_per_sec}
      id: cfab55f1-a9b0-0f14-313c-54b4668ae2a3
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Requests per sec}
        missing_values: linear
  - id: fb9f73a9-022d-4f08-a176-a4af0618cfc6
    title: Scoreboard [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 7}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: e55fe8b6-966c-7df0-71c4-7b83c4b61410, label: Closing connection, \n\
          aggregation: average, field: \n\
          apache.status.scoreboard.closing_connection}
      - {id: 9884ef4b-21ec-ea11-1e78-5acee20fe6a5, label: DNS lookup, \n\
          aggregation: average, field: apache.status.scoreboard.dns_lookup}
      - {id: ee5696fa-79af-5ba5-6ba2-2bd7208f1197, label: Gracefully finishing, \n\
          aggregation: average, field: \n\
          apache.status.scoreboard.gracefully_finishing}
      - {id: c2c72109-59ae-ec6c-046f-b083b158ba99, label: Idle cleanup, \n\
          aggregation: average, field: apache.status.scoreboard.idle_cleanup}
      - {id: 50173818-3646-6cdd-eb6b-fcc95e22f035, label: Keepalive, aggregation: \n\
          average, field: apache.status.scoreboard.keepalive}
      - {id: 46ae596e-bf2b-c988-48e6-61d98b06d271, label: Logging, aggregation: \n\
          average, field: apache.status.scoreboard.logging}
      - {id: 3698d8fc-3697-f767-ef90-d5ba4347fae9, label: Open slot, aggregation: \n\
          average, field: apache.status.scoreboard.open_slot}
      - {id: f1ef9469-ae70-066e-d71f-7bcb2009cd50, label: Reading request, \n\
          aggregation: average, field: apache.status.scoreboard.reading_request}
      - {id: 48f7e06c-a65d-618d-8876-a6a530d8e964, label: Sending reply, \n\
          aggregation: average, field: apache.status.scoreboard.sending_reply}
      - {id: 739f03ed-239c-3552-f94e-ffcaed2292b1, label: Starting up, \n\
          aggregation: average, field: apache.status.scoreboard.starting_up}
      - {id: f5945c27-6f19-5e58-6004-a5204aadba74, label: Total, aggregation: \n\
          average, field: apache.status.scoreboard.total}
      - {id: f5e6c708-9039-a605-74d7-21c2f79f30e2, label: Waiting for connection,
        aggregation: average, field: \n\
          apache.status.scoreboard.waiting_for_connection}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: 89879482-c9df-afd0-f2e4-0f6e95414cb5
      legend: {visible: show, width: extra_large, show_single_series: true, \n\
          truncate_labels: 0}
      type: line
      appearance:
        y_left_axis: {title: Count}
        missing_values: linear
        show_as_dotted: true
  - id: 44d1c271-bc9a-41a8-b30c-ca8b04f04277
    title: Total connections [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 37}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: ca70564f-f304-1d14-d521-cf5e8d4bfef0, label: Total, aggregation: \n\
          max, field: apache.status.connections.total}
      id: fc5ebf77-4bca-ba59-5d27-ba44c107ba11
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Connections}
        missing_values: linear
  - id: 7f45f1dc-cc1c-42a6-a691-a1a602ace63c
    title: Bytes per sec [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 22}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: f5a8af46-8adf-6c21-7a2a-3b5e99601572, label: Bytes per sec, \n\
          aggregation: average, field: apache.status.bytes_per_sec}
      id: a9ee0679-bf85-6bd2-1361-22071c6c3dd1
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Bytes per sec}
        missing_values: linear
  - id: 58f100e1-c5f9-4843-9bdf-a7ae9061ca20
    title: Workers [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 7}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 56fb37bf-ba98-9f61-fd55-abd62d91abf3, label: Busy workers, \n\
          aggregation: average, field: apache.status.workers.busy}
      - {id: cd81b842-c71b-fc3d-8a05-ccb62b1a508e, label: Idle workers, \n\
          aggregation: average, field: apache.status.workers.idle}
      id: 3da7285a-6c18-ef55-995b-7f237a879e0f
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Workers}
        missing_values: linear
  - id: de79f71b-cc47-40e7-b958-63d87a14fa97
    title: Connections [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 37}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: cb9b1a8a-369d-fb4d-b164-cf494238f345, label: Writing, aggregation: \n\
          max, field: apache.status.connections.async.writing}
      - {id: fe37b92a-9203-5cc5-b4a4-108e4c532052, label: Keep alive, \n\
          aggregation: max, field: apache.status.connections.async.keep_alive}
      - {id: d2302f47-c20e-948f-d1a4-45b4e2d710ce, label: Closing, aggregation: \n\
          max, field: apache.status.connections.async.closing}
      id: dcfa4cb9-1f71-c16d-df50-d85d22b1c293
      legend: {visible: show, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Connections}
        missing_values: linear
  - id: a855f0c8-cac9-4ebe-bce1-91fff3c18668
    title: Average server load [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 0, y: 52}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 2d8eb50a-79c8-d7a8-59f2-7f5c73037dfb, label: Load per 1 min, \n\
          aggregation: average, field: apache.status.load.1}
      - {id: e06f3139-c859-d085-81a9-ccf153227a45, label: Load per 5 min, \n\
          aggregation: average, field: apache.status.load.5}
      - {id: fc05a8f0-f16c-30ca-5d96-d82976b2b2e4, label: Load per 15 min, \n\
          aggregation: average, field: apache.status.load.15}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: 4d99c97f-86e9-a09b-38ee-ff495b513af9
      legend: {visible: show, width: extra_large, truncate_labels: 0}
      type: line
      appearance:
        y_left_axis: {title: Count}
        missing_values: linear
        show_as_dotted: true
  - id: 908bb0f9-4d98-469d-9351-424a5196803f
    title: CPU usage [Metrics Apache]
    size: {w: 24, h: 15}
    position: {x: 24, y: 52}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 79753695-025e-6514-8d80-24b0694d7a1c, label: CPU load, aggregation: \n\
          average, field: apache.status.cpu.load}
      - {id: f825ed16-57aa-f482-41f4-4b7c09c1329e, label: CPU user, aggregation: \n\
          average, field: apache.status.cpu.user}
      - {id: 37d9b62d-6b15-512d-df3e-10826ce5346a, label: CPU system, \n\
          aggregation: average, field: apache.status.cpu.system}
      - {id: 25f43d03-76bd-bbda-737a-5e6738142f4e, label: CPU children user, \n\
          aggregation: average, field: apache.status.cpu.children_user}
      - {id: b155ec09-757f-9488-f529-f3ee676ca507, label: CPU children system, \n\
          aggregation: average, field: apache.status.cpu.children_system}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: cc954e7d-56b9-8bb8-c86d-0de3ca47033e
      legend: {visible: show, width: extra_large, truncate_labels: 0}
      type: line
      appearance:
        y_left_axis: {title: Count}
        missing_values: linear
        show_as_dotted: true
""")


@pytest.mark.integrations
def test_integrations_snapshot_14_apache_otel_overview(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/apache_otel/kibana/dashboard/apache_otel-overview.json`."""
    assert _yaml_for_target(
        'packages/apache_otel/kibana/dashboard/apache_otel-overview.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Apache OTel] Overview'
  id: apache_otel-overview
  description: Overview of Apache HTTP Server health and performance from \n\
    OpenTelemetry metrics.
  time_range: {from: now-1h, to: now}
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: apachereceiver.otel}
  controls:
  - id: 9ee7a268-5cc6-b546-db6e-96929c9a955b
    label: Server name
    type: options
    field: resource.attributes.apache.server.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: a18657f3-9386-7419-0c1e-db380f1b3b06
    label: Host
    type: options
    field: resource.attributes.host.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 887981e6-1ee5-4087-096b-af81cff49944
    title: ''
    hide_title: true
    size: {w: 16, h: 12}
    position: {x: 0, y: 0}
    markdown: {content: "## [Apache OTel] Overview\\n\\nThis dashboard provides an overview
        of Apache HTTP Server health and performance via OpenTelemetry metrics:\\n\\
        - Request rate and traffic throughput\\n- Worker pool utilization (busy vs
        idle)\\n- Active and asynchronous connection counts\\n- Server load averages
        (1m, 5m, 15m)\\n- CPU load and CPU time breakdown by mode\\n", font_size: \n\
        12, links_in_new_tab: false}
  - id: f1e0d86e-84d4-93fe-5f7b-bef3ab9bdfa0
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 16, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.uptime IS NOT NULL\\n\\
        | STATS uptime_sec = MAX(LAST_OVER_TIME(apache.uptime))"
      time_field: '@timestamp'
      id: 90b82132-fb95-b61d-b25b-6b3a956ce5eb
      type: metric
      primary: {id: 44133068-323b-27ee-8a35-ea6eebf2ccb7, field: uptime_sec, \n\
          label: Uptime}
  - id: e520f2f7-162a-8ae2-3c9d-4fe5cd5508d9
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 24, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.requests IS NOT NULL\\n\\
        | STATS request_rate = SUM(RATE(apache.requests))"
      time_field: '@timestamp'
      id: db068471-9f05-5d3f-b158-d86dcc864f46
      type: metric
      primary: {id: f691e6c3-1940-ecdf-ae31-22236c2ed15c, field: request_rate, \n\
          label: Request Rate}
  - id: 81c12fbb-84e1-8af8-787e-7f8943490b9c
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 32, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.traffic IS NOT NULL\\n\\
        | STATS traffic_rate = SUM(RATE(apache.traffic))"
      time_field: '@timestamp'
      id: 7aeafe3b-f369-eda5-460e-e5e53785bd91
      type: metric
      primary: {id: 7fdc8059-0203-19b4-0ccf-4ca2acae8937, field: traffic_rate, \n\
          label: Traffic Rate}
  - id: ac7d975a-8037-c750-c277-27b39069530a
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 40, y: 0}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.cpu.load IS NOT NULL\\n\\
        | STATS cpu_load = MAX(AVG_OVER_TIME(apache.cpu.load))"
      time_field: '@timestamp'
      id: 24978926-fa37-f2b2-dacf-9db16feb3b04
      type: metric
      primary: {id: f785719f-38a0-74e3-8cb4-644a0cfeb76e, field: cpu_load, label: \n\
          CPU Load}
  - id: 2e15537b-ed9c-bf4c-8f36-c383700afb65
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 16, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.current_connections
        IS NOT NULL\\n| STATS connections = MAX(LAST_OVER_TIME(apache.current_connections))"
      time_field: '@timestamp'
      id: 471e31b4-4a2a-3aeb-c11d-1a753aae5a0a
      type: metric
      primary: {id: a6d083cf-a04d-f4c1-17f9-781c30adb518, field: connections, \n\
          label: Active Connections}
  - id: 8c951b8b-02a8-fc7d-6960-273855fb0feb
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 24, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.workers IS NOT NULL
        AND attributes.state == \\"busy\\"\\n| STATS busy = MAX(LAST_OVER_TIME(apache.workers))"
      time_field: '@timestamp'
      id: 2d6dc306-bba4-3998-0e48-22e604615f9b
      type: metric
      primary: {id: ea066e13-d6ca-622e-8415-661dd57f65af, field: busy, label: \n\
          Busy Workers}
  - id: efdc2bf8-ae2d-b2e2-164c-cbff0bca4550
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 32, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.workers IS NOT NULL
        AND attributes.state == \\"idle\\"\\n| STATS idle = MAX(LAST_OVER_TIME(apache.workers))"
      time_field: '@timestamp'
      id: 158b44d3-5497-dd45-78bc-9094f10cc1d9
      type: metric
      primary: {id: fcedf5a1-dde1-e721-a0b1-dc298ae48674, field: idle, label: \n\
          Idle Workers}
  - id: cb8ead79-d8c5-13fa-1f94-520e63c21f06
    title: ''
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 40, y: 6}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE `apache.load.1` IS NOT NULL\\n\\
        | STATS load_1m = MAX(AVG_OVER_TIME(`apache.load.1`))"
      time_field: '@timestamp'
      id: 115d9abc-72ea-3071-4ffe-243954e8f55a
      type: metric
      primary: {id: b0862e2f-b189-d0bb-fffc-38901971f703, field: load_1m, label: \n\
          Server Load (1m)}
  - id: efc3c390-5ded-e443-91d9-88410c2a103b
    title: ''
    hide_title: true
    size: {w: 48, h: 3}
    position: {x: 0, y: 12}
    markdown: {content: '## Traffic & Performance', font_size: 12, \n\
        links_in_new_tab: false}
  - id: 8359485a-f93f-f780-cc8b-d2316ce56e05
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 15}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.requests IS NOT NULL\\n\\
        | STATS request_rate = SUM(RATE(apache.requests)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend)\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: 20a5f645-16df-2295-5f8c-a639f8a0b834, field: request_rate, label: \n\
          Requests/sec}
      id: 34a18afa-b0ee-1117-a900-1668525d48b4
      type: line
  - id: 399a4d4b-22a8-537f-9a47-f9e6e51582e0
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 15}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.traffic IS NOT NULL\\n\\
        | STATS traffic_rate = SUM(RATE(apache.traffic)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend)\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: 1cffc5ee-5721-36ea-20a4-f375da433660, field: traffic_rate, label: \n\
          Bytes/sec}
      id: 1d2ecf37-e43a-fff0-d4b9-cf8320451f99
      type: line
  - id: f63c8a06-4917-e9eb-d460-342789708dbe
    title: ''
    hide_title: true
    size: {w: 48, h: 3}
    position: {x: 0, y: 27}
    markdown: {content: '## Workers & Connections', font_size: 12, \n\
        links_in_new_tab: false}
  - id: d4db9150-8807-90e5-632d-679e4b1129fe
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 30}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.workers IS NOT NULL\\n\\
        | STATS workers = MAX(LAST_OVER_TIME(apache.workers)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend), attributes.state\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: d792695a-ae0d-bfc2-f5fd-84f1919c72e4, field: workers, label: \n\
          Workers}
      breakdown: {id: 425bd375-1fdb-eef3-859e-fe6500560791, field: \n\
          attributes.state}
      id: 4345524e-523e-6c06-ab0d-bd1544843bd7
      type: area
      mode: stacked
  - id: 80006d9a-5de5-4b99-12ce-486e55a7d0ce
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 30}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.current_connections
        IS NOT NULL\\n| STATS connections = MAX(LAST_OVER_TIME(apache.current_connections))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend)\\n| SORT time_bucket
        ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: b4602782-87fb-a673-4fca-7574bd6340b5, field: connections, label: \n\
          Active Connections}
      id: 767699aa-7077-3ca1-7cd0-5b649ae5ecfc
      type: line
  - id: ff32905c-4ec6-d1bd-0bee-be75d4bca877
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 42}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.scoreboard IS NOT NULL\\n\\
        | STATS count = MAX(LAST_OVER_TIME(apache.scoreboard)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend), attributes.state\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: b07c5df4-6511-8380-b79d-e8622dd87569, field: count, label: Workers}
      breakdown: {id: 425bd375-1fdb-eef3-859e-fe6500560791, field: \n\
          attributes.state}
      id: 5a64a6d7-9074-a7c6-dc32-591c29c0e1f2
      type: bar
      mode: stacked
  - id: f04ea16d-49bf-689f-3dcf-43d35ccf3ca6
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 42}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.connections.async IS
        NOT NULL\\n| STATS connections = MAX(LAST_OVER_TIME(apache.connections.async))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend), attributes.connection_state\\n\\
        | SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: bf4dc9e5-57d7-18cb-47a1-9ec9265607d2, field: connections, label: \n\
          Connections}
      breakdown: {id: 154b1775-0ddc-a99c-002e-399606d8644b, field: \n\
          attributes.connection_state}
      id: e9b984cc-aa1d-8753-2abd-8a9776bea5c1
      type: area
      mode: stacked
  - id: 3613a751-e533-3134-cccd-cdb572c26b67
    title: ''
    hide_title: true
    size: {w: 48, h: 3}
    position: {x: 0, y: 54}
    markdown: {content: '## System Resources', font_size: 12, links_in_new_tab: \n\
        false}
  - id: f9e49625-213d-5db0-c983-de18f7dc82d9
    title: ''
    size: {w: 24, h: 12}
    position: {x: 0, y: 57}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| FORK ( WHERE `apache.load.1` IS
        NOT NULL | STATS load = MAX(AVG_OVER_TIME(`apache.load.1`)) BY time_bucket
        = BUCKET(@timestamp, 20, ?_tstart, ?_tend) | EVAL period = \\"1 minute\\" )
        ( WHERE `apache.load.5` IS NOT NULL | STATS load = MAX(AVG_OVER_TIME(`apache.load.5`))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend) | EVAL period =
        \\"5 minutes\\" ) ( WHERE `apache.load.15` IS NOT NULL | STATS load = MAX(AVG_OVER_TIME(`apache.load.15`))
        BY time_bucket = BUCKET(@timestamp, 20, ?_tstart, ?_tend) | EVAL period =
        \\"15 minutes\\" )\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: d0850dfa-7c38-ae70-cde6-58bd8bb16418, field: load, label: Load}
      breakdown: {id: 88724d8b-0208-c6bc-f465-65feba363b95, field: period}
      id: 76e16332-23ef-62ec-dfe4-1e5d5dbb3e25
      type: line
  - id: a9a36696-a097-1cd0-83af-34af4ad26fda
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 57}
    esql:
      query: "TS metrics-apachereceiver.otel-*\\n| WHERE apache.cpu.time IS NOT NULL\\n\\
        | STATS cpu_time_rate = SUM(RATE(apache.cpu.time)) BY time_bucket = BUCKET(@timestamp,
        20, ?_tstart, ?_tend), attributes.mode\\n| SORT time_bucket ASC"
      time_field: '@timestamp'
      dimension: {id: 3b250a7d-a8d7-8c9f-3842-5d1f4e3fa04c, field: time_bucket}
      metrics:
      - {id: 87218855-948b-e42e-fc25-e1cd715ebca9, field: cpu_time_rate, label: \n\
          CPU jiffs/sec}
      breakdown: {id: d054a2a0-63c2-f3a0-6bd3-0f6d670141a3, field: \n\
          attributes.mode}
      id: dd4b99d3-4bce-f113-ad76-a143a555d682
      type: area
      mode: stacked
""")


@pytest.mark.integrations
def test_integrations_snapshot_15_apache_spark_b22dc960_a06c_11ec_8d4f_4fe3367a4156(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/apache_spark/kibana/dashboard/apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156.json`."""
    assert _yaml_for_target(
        'packages/apache_spark/kibana/dashboard/apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics Apache Spark] Overview'
  id: apache_spark-b22dc960-a06c-11ec-8d4f-4fe3367a4156
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [apache_spark.driver, apache_spark.executor, apache_spark.node, \n\
        apache_spark.application]
  panels:
  - id: a3339a86-6f2b-4f1a-85b8-4619c417a110
    title: Memory usage over time [Metrics Apache Spark]
    size: {w: 24, h: 17}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 1a54dd5d-a969-d5ce-4213-892431969123, label: Memory, aggregation: \n\
          last_value, field: apache_spark.driver.memory.used}
      id: 1ac511bc-4ed9-6cae-500a-13ce5dfafa55
      legend: {visible: show, position: top, show_single_series: true}
      type: bar
      appearance:
        x_axis: {title: Timestamp}
        y_left_axis: {title: Memory}
      mode: stacked
  - id: 2943002d-504e-4a30-a581-cd92fd621fe1
    title: Number of stages completed [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 24, y: 0}
    lens:
      id: f1623b37-00ca-b828-895d-1b01da0678ef
      type: metric
      data_view: metrics-*
      primary: {id: 12ae267e-6f3b-468f-347a-fff2c1606c72, label: Number of \n\
          Stages Completed, aggregation: last_value, field: \n\
          apache_spark.driver.stages.completed_count}
  - id: 784e4a18-20e7-48ef-8737-3a8a4643c4fe
    title: Number of stages skipped [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 32, y: 0}
    lens:
      id: ee79c08d-28ba-5a87-dee3-2c63e508d783
      type: metric
      data_view: metrics-*
      primary: {id: c3f30df0-0d28-fe44-37ef-5d436370fa08, label: Number of \n\
          Stages Skipped, aggregation: last_value, field: \n\
          apache_spark.driver.stages.skipped_count}
  - id: 19bd059b-ca79-4fb0-b450-f8adeb8acc8f
    title: Number of failed stages [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 40, y: 0}
    lens:
      id: 728b902b-3e3e-e9e1-c4ca-b9a79fd13b40
      type: metric
      data_view: metrics-*
      primary: {id: f80df669-bb9f-53c9-1132-fb4842037f5f, label: Number of \n\
          Stages Failed, aggregation: last_value, field: \n\
          apache_spark.driver.stages.failed_count}
  - id: f84a1cd9-1b4b-484e-87f7-953c2f645570
    title: Number of Tasks over time [Metrics Apache Spark]
    size: {w: 24, h: 17}
    position: {x: 24, y: 6}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 18444f3d-68cc-046a-a78e-aeb4e36ff26a, label: Failed, aggregation: \n\
          max, field: apache_spark.driver.tasks.failed}
      - {id: c3df3636-9c49-71e1-da25-323692093d22, label: Skipped, aggregation: \n\
          max, field: apache_spark.driver.tasks.skipped}
      - {id: 81c00cab-5bda-dcdf-b198-696a99109d5c, label: Completed, aggregation: \n\
          max, field: apache_spark.driver.tasks.completed}
      id: b61fab9a-ecd0-48a6-5590-53552d48eb07
      legend: {visible: show, position: top, show_single_series: true}
      type: area
      appearance:
        x_axis: {title: Timestamp}
        y_left_axis: {title: Tasks}
        missing_values: linear
      mode: stacked
  - id: 64cbf207-795a-4818-915c-137eaebc6198
    title: Maximum amount of memory available for storage [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 0, y: 17}
    lens:
      id: 3fa4fe7e-45f4-3d86-0d75-1d2b42531415
      type: metric
      data_view: metrics-*
      primary: {id: 42ffb9f2-13de-6a37-672c-bfdb788d7282, label: Max Memory (MB),
        aggregation: last_value, field: apache_spark.driver.memory.max_mem}
  - id: 62c6f93e-b6c1-4004-b780-535ed730ebaa
    title: Number of jobs failed [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 8, y: 17}
    lens:
      id: 506f906a-5a47-089b-ce48-d53fc518f8f7
      type: metric
      data_view: metrics-*
      primary: {id: 72bd30ea-2107-93a4-a18c-0965b1914815, label: Failed Jobs, \n\
          aggregation: last_value, field: apache_spark.driver.jobs.failed}
  - id: bb9eb57d-fbf2-41a4-8187-5cead0c80faa
    title: Number of Succeeded jobs [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 16, y: 17}
    lens:
      id: 92cbd651-6968-11da-15c0-2db61b29ef72
      type: metric
      data_view: metrics-*
      primary: {id: 35193231-73bb-3639-25ca-b579f8f2e905, label: Succeeded Jobs, \n\
          aggregation: last_value, field: apache_spark.driver.jobs.succeeded}
  - id: b5caa5d1-221e-400d-a11a-ea539f1f4546
    title: Number of Threadpool tasks over time [Metrics Apache Spark]
    size: {w: 26, h: 13}
    position: {x: 0, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 5a731654-572a-2926-1618-5e23b60af9c8, label: Completed, aggregation: \n\
          max, field: apache_spark.executor.threadpool.complete_tasks}
      - {id: feda6127-29d3-28e6-5e66-1fef23285e53, label: Active, aggregation: \n\
          max, field: apache_spark.executor.threadpool.active_tasks}
      - {id: 6382d955-3cd5-6a7a-c570-508dc2a93726, label: Started, aggregation: \n\
          max, field: apache_spark.executor.threadpool.started_tasks}
      id: 669d64ce-5a60-b85a-0817-ad3bfdd7c512
      legend: {visible: show, position: top, show_single_series: true}
      type: area
      appearance:
        x_axis: {title: Timestamp}
        y_left_axis: {title: Threadpool Tasks}
        missing_values: linear
      mode: stacked
  - id: 7a729bca-db45-4ffe-b1bf-51fdc30e3b18
    title: ''
    hide_title: true
    size: {w: 8, h: 5}
    position: {x: 26, y: 23}
    lens:
      id: c10ae0f8-1336-018c-6b37-003f77f2f0dc
      type: metric
      data_view: metrics-*
      primary:
        id: b8eac41f-d6ff-24a2-bfa5-f03aa63881da
        label: Bytes Read
        format: {type: bytes, decimals: 2}
        aggregation: last_value
        field: apache_spark.executor.bytes.read
  - id: 0595e44f-e6b0-4d93-868f-040f2eb0de31
    title: ''
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 34, y: 23}
    lens:
      id: cdf509ba-1fdf-cb28-b153-f6f8bb5acd78
      type: metric
      data_view: metrics-*
      primary:
        id: f2f2cdbe-3bba-a953-5190-9632763d5fbe
        label: Bytes Written
        format: {type: bytes, decimals: 2}
        aggregation: last_value
        field: apache_spark.executor.bytes.written
  - id: ab8c87f3-ec56-4ddc-b0b0-7bb8a21366c2
    title: Number of Applications waiting [Metrics Apache Spark]
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 41, y: 23}
    lens:
      id: f72b49e1-d6ad-b7af-af5a-2d0151f7ee29
      type: metric
      data_view: metrics-*
      primary: {id: c991b463-7f1f-f067-36b3-e1e1c1eafc6e, label: Waiting \n\
          Applications, aggregation: last_value, field: \n\
          apache_spark.node.main.applications.waiting}
  - id: 75c23769-a2bd-4825-b20a-d140aeb36175
    title: Number of Records Read [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 5}
    position: {x: 26, y: 28}
    lens:
      id: 95f31d30-ef5a-366c-ba03-c5fb8592b7cb
      type: metric
      data_view: metrics-*
      primary: {id: 9147aade-65b8-d845-b936-ccf0480a2118, label: Records Read, \n\
          aggregation: last_value, field: apache_spark.executor.records.read}
  - id: ab9316b5-5728-4b03-aadb-a93e22da9257
    title: Number of Records Written [Metrics Apache Spark]
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 34, y: 28}
    lens:
      id: f67d6ae9-9836-c3b0-ae66-2402e1afba51
      type: metric
      data_view: metrics-*
      primary: {id: e3096189-d04a-c527-7bff-a46de39bdb59, label: Records Written,
        aggregation: last_value, field: apache_spark.executor.records.written}
  - id: ab2aa190-2b49-4ec6-9479-ad4a4ade95ad
    title: Total number of Applications [Metrics Apache Spark]
    hide_title: true
    size: {w: 7, h: 5}
    position: {x: 41, y: 28}
    lens:
      id: fe53dcfd-cff1-04f2-a713-98ea7ea6a073
      type: metric
      data_view: metrics-*
      primary: {id: 81aa9980-5075-3ae2-fbd8-171b8ae9ba11, label: Total \n\
          Applications, aggregation: last_value, field: \n\
          apache_spark.node.main.applications.count}
  - id: cfbdf185-1437-478f-a856-eedbe62d1de2
    title: Number of Workers Alive [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 26, y: 33}
    lens:
      id: 3555b769-c9f2-dbef-778a-41b2c910cbf0
      type: metric
      data_view: metrics-*
      primary: {id: 34a76bc2-bcb5-e506-80d2-c745f7c9a313, label: Workers Alive, \n\
          aggregation: last_value, field: apache_spark.node.main.workers.alive}
  - id: 78e81e12-c659-4d89-a80d-14ec4e49368a
    title: Application Source Status [Metrics Apache Spark]
    size: {w: 14, h: 12}
    position: {x: 34, y: 33}
    lens:
      id: ade884fd-bcbc-b85c-f327-ea048e60555e
      type: pie
      appearance:
        donut: medium
        values: {format: hide}
      legend: {visible: show}
      data_view: metrics-*
      metrics:
      - {id: 8419b0f5-d93e-229b-78df-1ba30cdd0a05, label: Application Name, \n\
          aggregation: unique_count, field: apache_spark.application.name}
      breakdowns:
      - {id: 6a815d04-365d-75d8-a2bf-9810bf0f3f56, type: values, size: 5, field: \n\
          apache_spark.application.status}
  - id: fa3bca1d-df9c-4e2b-8785-cfe9211a7843
    title: Number of Cores used [Metrics Apache Spark]
    hide_title: true
    size: {w: 13, h: 9}
    position: {x: 0, y: 36}
    lens:
      id: 515fffaf-9d04-caad-75aa-f91b14489999
      type: metric
      data_view: metrics-*
      primary: {id: 7f527134-c934-5889-e48d-d344f8ee4050, label: Number of Cores
          Used, aggregation: last_value, field: \n\
          apache_spark.node.worker.cores.used}
  - id: 18c0d3d3-912f-42e4-a322-a5fcaa9002b0
    title: Memory Used [Metrics Apache Spark]
    hide_title: true
    size: {w: 13, h: 9}
    position: {x: 13, y: 36}
    lens:
      id: 9df1121d-0f58-d173-8ada-204a85982939
      type: metric
      data_view: metrics-*
      primary: {id: a7d99814-449a-c718-7a61-d57c7430a625, label: Memory Used \n\
          (MB), aggregation: last_value, field: \n\
          apache_spark.node.worker.memory.used}
  - id: 54e6714e-c9b2-4e0b-85f4-500ca898eb4d
    title: Total Workers [Metrics Apache Spark]
    hide_title: true
    size: {w: 8, h: 6}
    position: {x: 26, y: 39}
    lens:
      id: 46f73568-3fc3-3449-c826-38fa3d5eb033
      type: metric
      data_view: metrics-*
      primary: {id: b368cd2d-f33a-43a7-f042-616d1d4bd993, label: Total Workers, \n\
          aggregation: last_value, field: apache_spark.node.main.workers.count}
""")


@pytest.mark.integrations
def test_integrations_snapshot_16_apache_tomcat_2a331270_b8cd_11ed_a099_3791d000f969(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/apache_tomcat/kibana/dashboard/apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969.json`."""
    assert _yaml_for_target(
        'packages/apache_tomcat/kibana/dashboard/apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics Apache Tomcat] Session'
  id: apache_tomcat-2a331270-b8cd-11ed-a099-3791d000f969
  description: This Apache Tomcat dashboard visualizes session data stream \n\
    metrics.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: apache_tomcat.session}
  controls:
  - id: 04c6559b-711b-5cd4-22e9-91f2c26da973
    label: Host Name
    type: options
    field: service.address
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: 482ce94f-ef28-d3f2-dec0-a672173c6f01
    label: Application Name
    type: options
    field: apache_tomcat.session.application_name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: a39adf70-8e40-4d80-a127-a1747a75be1f
    title: Created sessions over time [Metrics Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: cef84950-71d9-e11e-6aad-928834e010f2
        label: Created
        format: {type: number, decimals: 0}
        filter: {kql: 'apache_tomcat.session.create.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.create.total
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: 96abbff7-e5ce-37d1-f982-d6495ce96460
      legend: {visible: show, width: large}
      type: line
      appearance:
        y_left_axis: {title: Sessions}
  - id: 91d26f64-351f-420e-a37b-88a882ecba0e
    title: Expired sessions per application [Metrics Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 24, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 2b38d0cb-f503-a865-39a8-3750631d2c7d
        label: Expired
        format: {type: number, decimals: 0}
        filter: {kql: 'apache_tomcat.session.expire.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.expire.total
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: 6abc7ea5-cd47-57b2-056b-d419084740ce
      legend: {visible: show, width: large, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Sessions}
        values: {visible: true}
  - id: 5922510e-e6a2-4f9c-aceb-83715cc3b539
    title: Current active sessions over time [Metrics Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 0, y: 14}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 8ca54818-6d8a-e9e5-4f6f-27325d3c050a
        label: Current active
        format: {type: number, decimals: 0}
        filter: {kql: 'apache_tomcat.session.active.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.active.total
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: 3d7208fd-3115-498f-41ec-5b7fcfecca93
      legend: {visible: show}
      type: line
      appearance:
        y_left_axis: {title: Sessions}
  - id: 2d408e1c-da52-4aed-b760-812f89f48184
    title: Session expiration processing time [Metric Apache Tomcat]
    size: {w: 24, h: 14}
    position: {x: 24, y: 14}
    lens:
      data_view: metrics-*
      metrics:
      - id: 2d84e1c1-8d7c-fa96-7ce2-9be39561172b
        label: Processing time(ms)
        filter: {kql: 'apache_tomcat.session.processing_time: *'}
        aggregation: last_value
        field: apache_tomcat.session.processing_time
      breakdown: {id: b360994e-7f94-67b2-1ef1-119bdfe47b0a, type: values, size: \n\
          10, field: apache_tomcat.session.application_name}
      id: b1908a67-8751-7dd1-296e-98b74257cd12
      legend: {visible: show}
      type: bar
      appearance:
        values: {visible: true}
      mode: stacked
  - id: 8ce83532-0623-4974-9280-b6c56c6b0c27
    title: Sessions overview [Metrics Apache Tomcat]
    size: {w: 48, h: 15}
    position: {x: 0, y: 28}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: 69c706e4-2afb-5494-e7a3-b7030c4ace22
      data_view: metrics-*
      metrics:
      - id: 23c60d24-dbab-15d5-f3fa-c7f0a1e27e75
        label: Created
        filter: {kql: 'apache_tomcat.session.create.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.create.total
      - id: 6126988d-5f3e-750b-f4e1-d37980e33279
        label: Current active
        filter: {kql: 'apache_tomcat.session.active.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.active.total
      - id: 3f6193ef-9ebf-6b72-4e7e-3d63221f85b1
        label: Expired
        filter: {kql: 'apache_tomcat.session.expire.total: *'}
        aggregation: last_value
        field: apache_tomcat.session.expire.total
      - id: 9feae62a-7de4-263b-e099-de8c4d8077b9
        label: Rejected
        filter: {kql: 'apache_tomcat.session.rejected.count: *'}
        aggregation: last_value
        field: apache_tomcat.session.rejected.count
      breakdowns:
      - {id: f5fb6326-26af-f495-421b-7b423475aa29, type: values, size: 10000, \n\
          field: apache_tomcat.session.application_name}
""")


@pytest.mark.integrations
def test_integrations_snapshot_17_arista_ngfw_090e6d40_1dc4_11ee_b346_5b9e0073e798(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/arista_ngfw/kibana/dashboard/arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798.json`."""
    assert _yaml_for_target(
        'packages/arista_ngfw/kibana/dashboard/arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: Arista NG Firewall Session Stats
  id: arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798
  description: ''
  settings:
    margins: false
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 20d48459-770b-4cde-8ede-72b084ea1772
    title: ''
    hide_title: true
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: 'TODO(decompile): unsupported panel type `metrics`'}
  - id: 13262519-30cf-49ea-a20e-e68cd2ed1a44
    title: ''
    size: {w: 48, h: 4}
    position: {x: 0, y: 4}
    links:
      layout: horizontal
      items:
      - {id: arista_ngfw-86b139ff-92ab-4aae-b0d8-c33e3be132f1, label: Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-86b139ff-92ab-4aae-b0d8-c33e3be132f1_dashboard}
      - {id: arista_ngfw-2b026f60-1cf1-11ee-b346-5b9e0073e798, label: Admin \n\
          Login, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-2b026f60-1cf1-11ee-b346-5b9e0073e798_dashboard}
      - {id: arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798, label: Session \n\
          Stats, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-090e6d40-1dc4-11ee-b346-5b9e0073e798_dashboard}
      - {id: arista_ngfw-c61b1eb0-1cf7-11ee-b346-5b9e0073e798, label: Web Filter,
        dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-c61b1eb0-1cf7-11ee-b346-5b9e0073e798_dashboard}
      - {id: arista_ngfw-0f3dafe6-c66a-4d1e-a9e9-fa3fb418bfaf, label: Intrusion \n\
          Prevention, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-0f3dafe6-c66a-4d1e-a9e9-fa3fb418bfaf_dashboard}
      - {id: arista_ngfw-93596b63-d808-4a2f-9cbf-d0e9c4003079, label: System \n\
          Stats, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-93596b63-d808-4a2f-9cbf-d0e9c4003079_dashboard}
      - {id: arista_ngfw-a4bb8521-b9d4-4d33-be52-b4ccefb2eee1, label: Interface \n\
          Stats, dashboard: \n\
          TODO_dashboard_id_for_link_arista_ngfw-a4bb8521-b9d4-4d33-be52-b4ccefb2eee1_dashboard}
  - id: 07dd66c3-cfbf-450e-835d-a2d1d15560b3
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 0, y: 8}
    lens:
      id: 38f6e595-d72c-afd6-7393-c4e0d5413bcf
      type: metric
      data_view: logs-*
      primary:
        id: 60f0e2e9-80aa-c60f-c9ac-4315f30ac797
        label: Total Network Bytes
        format: {type: bytes, decimals: 2}
        aggregation: sum
        field: network.bytes
  - id: ff518a08-7f9c-439b-92e1-488179e73e27
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 9, y: 8}
    lens:
      id: 788bab94-e278-d2bd-17b8-50faeed3c0ba
      type: metric
      data_view: logs-*
      primary:
        id: 553fc9d2-2640-b373-7038-7b43516fbb74
        label: Unique Source IP Addresses
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: source.ip
  - id: e13dda86-df4f-4f15-842c-dc5c757c36f5
    title: Bytes Transferred Over Time
    size: {w: 30, h: 16}
    position: {x: 18, y: 8}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: ff3cd2d8-387a-7746-c37c-28931d933d67
        label: Network Bytes
        format: {type: bytes, decimals: 2}
        filter: {kql: 'network.bytes: *'}
        aggregation: last_value
        field: network.bytes
      id: 764dcbe8-2e89-1b65-3985-fa51b2982520
      legend: {visible: hide, width: large, truncate_labels: 0}
      type: bar
      mode: stacked
  - id: 6d7ec786-8684-41e7-bee4-fcb34344e506
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 0, y: 16}
    lens:
      id: 611c5992-43c7-d115-9681-759f1b1fd3b4
      type: metric
      data_view: logs-*
      primary: {id: 9659d1ad-3346-6601-fd44-abb8ddca185e, label: Unique Sessions,
        aggregation: unique_count, field: event.id}
  - id: fc886fe0-c926-430c-b91d-2d5dde9f4ccf
    title: ''
    hide_title: true
    size: {w: 9, h: 8}
    position: {x: 9, y: 16}
    lens:
      id: f4fc2c85-f148-5a54-5a46-93f8a57f2f32
      type: metric
      data_view: logs-*
      primary:
        id: 828620bd-d524-ad12-485e-8b1d35276796
        label: Unique Destination IP Addresses
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: destination.ip
  - id: 86e18a08-a067-481c-a16c-af7ae7d17eec
    title: Top 500 Source IP's by Bytes Transferred
    size: {w: 11, h: 24}
    position: {x: 0, y: 24}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: 7373d679-ddbb-5f04-a077-69ca19958b06
      data_view: logs-*
      metrics:
      - id: ac60419e-296d-5ab4-1456-4d1264965548
        label: Total Source Bytes
        format: {type: bytes, decimals: 2}
        aggregation: sum
        field: source.bytes
      breakdowns:
      - {id: 5b9dbf18-3fa2-dc61-f776-d851d26efde1, type: values, size: 500, \n\
          field: source.ip}
  - id: 5b9db7a3-da2a-4bbf-b828-26c28337a81c
    title: Top 500 Destination IP's by Bytes Transferred
    size: {w: 11, h: 24}
    position: {x: 11, y: 24}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: e673ae2a-bcfd-1d8d-4681-2d5a8d5b11bd
      data_view: logs-*
      metrics:
      - id: 209245a0-3f5d-412d-a3ab-20d9f3ac7c7b
        label: Total Destination Bytes
        format: {type: bytes, decimals: 2}
        aggregation: sum
        field: destination.bytes
      breakdowns:
      - {id: 26d1ab6d-96a8-8f39-250b-87f07964d50f, type: values, size: 500, \n\
          field: destination.ip}
  - id: 7355a77d-85cd-41ed-b1da-f238a3ea84bd
    title: ''
    size: {w: 48, h: 40}
    position: {x: 0, y: 48}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_7355a77d-85cd-41ed-b1da-f238a3ea84bd'}
  - id: 6ae5c6ae-a667-49e2-aa53-2fe5a2d5b6d8
    title: Events by Source to Destination GeoLocation
    size: {w: 26, h: 24}
    position: {x: 22, y: 24}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
""")


@pytest.mark.integrations
def test_integrations_snapshot_18_armis_68592f5a_9c7b_4398_a723_510d5e48a8b1(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/armis/kibana/dashboard/armis-68592f5a-9c7b-4398-a723-510d5e48a8b1.json`."""
    assert _yaml_for_target(
        'packages/armis/kibana/dashboard/armis-68592f5a-9c7b-4398-a723-510d5e48a8b1.json',
        integrations_target_files,
    ) == snapshot("""\
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
      metrics:
      - id: 260bd7d4-c13d-6b77-5d3d-fb658dae7311
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdown: {id: 4ab783d8-08af-6325-0eb3-c5b0d3424ae3, type: values, size: \n\
          10, field: armis.vulnerability.user_interaction}
      id: 28026b69-d197-4962-df74-fb7caf5016ec
      legend: {visible: show, truncate_labels: 0}
      type: bar
      mode: stacked
  - id: f9abc45f-d604-4424-9ecd-430a01ad442e
    title: Vulnerabilities by Scope [Logs Armis]
    size: {w: 24, h: 15}
    position: {x: 0, y: 68}
    lens:
      data_view: logs-*
      metrics:
      - id: 260bd7d4-c13d-6b77-5d3d-fb658dae7311
        label: Count
        format: {type: number, decimals: 0}
        aggregation: unique_count
        field: vulnerability.id
      breakdown: {id: e12de2ae-6532-9e12-a0c7-a453f6f43f1a, type: values, size: \n\
          10, field: armis.vulnerability.scope}
      id: 88fe1705-da55-6c28-8d73-d6a2c7ddac4e
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
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_3d38e8cd-465c-4b53-a1a4-a4e040950c28'}
""")


@pytest.mark.integrations
def test_integrations_snapshot_19_auditd_dfbb49f0_0a0f_11e7_8a62_2d05eaaac5cb(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/auditd/kibana/dashboard/auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb.json`."""
    assert _yaml_for_target(
        'packages/auditd/kibana/dashboard/auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Logs Auditd] Audit Events'
  id: auditd-dfbb49f0-0a0f-11e7-8a62-2d05eaaac5cb
  description: Dashboard for the Auditd Logs integration
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: '1'
    title: Event types breakdown [Logs Auditd]
    size: {w: 16, h: 16}
    position: {x: 0, y: 0}
    lens:
      id: 903abd3b-90dc-73c8-d2c8-e515a7b6992e
      type: pie
      appearance:
        donut: medium
        values: {decimal_places: 2}
      legend: {visible: hide, truncate_labels: 1}
      data_view: logs-*
      metrics:
      - {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: ade70d6e-e7a0-ff05-784e-d503e3fa785d, type: values, size: 50, field: \n\
          event.action}
  - id: '2'
    title: Top Exec Commands [Logs Auditd]
    size: {w: 16, h: 16}
    position: {x: 32, y: 0}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 15d555ac-ffdc-1bb5-7840-593cc044986b
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 74d2078a-75aa-7938-5e47-4df6b852e788, type: values, size: 30, field: \n\
          auditd.log.a0}
  - id: '7'
    title: ''
    size: {w: 48, h: 20}
    position: {x: 0, y: 28}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_7'}
  - id: d84a9a87-e40f-465c-9114-4d343ffb6481
    title: Event Account Tag Cloud [Logs Auditd]
    size: {w: 16, h: 16}
    position: {x: 16, y: 0}
    lens:
      type: datatable
      paging: {enabled: true, page_size: 10}
      id: 904b21e5-b428-ebb8-f57d-ecfacf9618dc
      data_view: logs-*
      metrics:
      - {id: ff0c0d02-da78-c9e7-1a5f-ad5638cc3ecc, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: 005c89df-8ef9-fb6d-3700-75e21e4ed54d, type: values, size: 20, field: \n\
          user.name}
  - id: e1817f83-5b41-4dd8-8108-ffe725dc9cd2
    title: Event Results [Logs Auditd]
    size: {w: 24, h: 12}
    position: {x: 0, y: 16}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 2ee316f6-f221-ade4-14b6-c17eb4102f59
        label: Success
        filter: {kql: 'event.outcome : "success" '}
        aggregation: count
        field: ___records___
      - id: a877fdf6-7537-e4c5-a433-f7ba92760b34
        label: Failure
        filter: {kql: 'event.outcome : "failure"'}
        aggregation: count
        field: ___records___
      id: 25e76f0f-b803-ff74-b0bc-0f6c2ac6b2c8
      legend: {visible: show}
      type: line
      appearance:
        y_left_axis: {title: Count}
  - id: 09f4ba02-a62c-410f-8d43-31e9e5278826
    title: ''
    size: {w: 24, h: 12}
    position: {x: 24, y: 16}
    markdown: {content: 'TODO(decompile): unsupported panel type `map`'}
""")


@pytest.mark.integrations
def test_integrations_snapshot_20_auth0_29fb7200_4062_11ec_b18d_ef6bf98b26bf(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/auth0/kibana/dashboard/auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf.json`."""
    assert _yaml_for_target(
        'packages/auth0/kibana/dashboard/auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: Auth0
  id: auth0-29fb7200-4062-11ec-b18d-ef6bf98b26bf
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  panels:
  - id: 1a13814d-17bf-42cf-8ef9-2dc599fb6766
    title: Auth0 Log Stream Event Types
    size: {w: 15, h: 10}
    position: {x: 0, y: 0}
    lens:
      id: fddb976d-8c26-b8c6-135a-8821d498482d
      type: pie
      data_view: logs-*
      metrics:
      - {id: 45862133-3a58-d112-d754-dfbd3642a4e4, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 1fafb44f-baf9-8729-727f-25292d26b071, type: values, size: 5, field: \n\
          event.category}
  - id: 6089a77e-3c96-4414-9932-eda55ced3d07
    title: Rate of events
    size: {w: 14, h: 10}
    position: {x: 15, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 80593e81-2240-09ce-0ed4-72a28e5c7453, label: Unique count of \n\
          event.type, aggregation: unique_count, field: event.type}
      id: cb4380fc-2f0b-9732-4221-917b1eaad048
      legend: {visible: show}
      type: line
  - id: 5124c723-8890-477e-aad5-bc4fd529bd46
    title: ''
    size: {w: 9, h: 5}
    position: {x: 29, y: 0}
    lens:
      id: 21ea12b7-2d60-a974-def7-6b5d51f7274c
      type: metric
      data_view: logs-*
      primary: {id: 76ebcc27-9947-fb34-0237-d105829dbf47, label: Count of Failed
          Logins, aggregation: count, field: ___records___}
  - id: cb337534-d263-480b-b6a3-80cc4f14d73b
    title: Number of Successful Logins
    size: {w: 10, h: 5}
    position: {x: 38, y: 0}
    lens:
      id: 95ece390-67c3-5f41-ab17-78545af3fb48
      type: metric
      data_view: logs-*
      primary: {id: 90c68c7b-bef9-4068-3235-0b7c27368a11, label: Count of \n\
          Successful Logins, aggregation: count, field: ___records___}
  - id: f35d9f39-29b5-4ea3-b43a-36da7af3b2af
    title: Number of Failed Signups
    size: {w: 9, h: 5}
    position: {x: 29, y: 5}
    lens:
      id: 8afc7342-3c96-b073-5544-1cba9c548b25
      type: metric
      data_view: logs-*
      primary: {id: d7c62aa6-2fac-4195-2e9c-91d77d584800, label: Count of Failed
          Signups, aggregation: count, field: ___records___}
  - id: 27dafd73-8177-4243-b93c-426f70bc5fea
    title: Number of Successful Signups
    size: {w: 10, h: 5}
    position: {x: 38, y: 5}
    lens:
      id: 5db2d673-3b8d-c208-bd22-64e6f6bcdadf
      type: metric
      data_view: logs-*
      primary: {id: b0d33e81-cbb1-49db-8ffa-5c25d7a8af51, label: Count of \n\
          Successful Signups, aggregation: count, field: ___records___}
  - id: d00429d4-502f-41d8-8a2b-7300859930ea
    title: Rate of Successful Logins
    size: {w: 15, h: 12}
    position: {x: 0, y: 10}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 28ba3e0b-7a41-30d4-9377-96a097cfc685, label: Count of records, \n\
          aggregation: count, field: ___records___}
      id: 3c3713e4-cc81-1e3c-25fd-e6f3a6b28680
      legend: {visible: show}
      type: line
  - id: c1a1b718-c5f1-4029-9fda-0cd7ed38b3a8
    title: Rate of Failed Logins
    size: {w: 14, h: 12}
    position: {x: 15, y: 10}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 28ba3e0b-7a41-30d4-9377-96a097cfc685, label: Count of records, \n\
          aggregation: count, field: ___records___}
      id: 3c3713e4-cc81-1e3c-25fd-e6f3a6b28680
      legend: {visible: show}
      type: line
  - id: 7f0587d4-ef04-4913-9ccb-cd2c93f470df
    title: IP Addresses of failed logins
    size: {w: 19, h: 12}
    position: {x: 29, y: 10}
    lens:
      data_view: logs-*
      metrics:
      - {id: 28ba3e0b-7a41-30d4-9377-96a097cfc685, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdown: {id: 5cf7c1f2-7b4e-0e1d-3ea4-abc1e81517d4, type: values, size: \n\
          10, field: source.ip}
      id: 64059a2f-154b-7d5a-b768-bb856b96a0c5
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 253f1007-1537-4012-a663-48bccf233f4c
    title: ''
    size: {w: 48, h: 11}
    position: {x: 0, y: 22}
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_253f1007-1537-4012-a663-48bccf233f4c'}
""")


@pytest.mark.integrations
def test_integrations_snapshot_21_aws_07d67a60_d872_11eb_8220_c9141cc1b15c(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/aws/kibana/dashboard/aws-07d67a60-d872-11eb-8220-c9141cc1b15c.json`."""
    assert _yaml_for_target(
        'packages/aws/kibana/dashboard/aws-07d67a60-d872-11eb-8220-c9141cc1b15c.json',
        integrations_target_files,
    ) == snapshot("""\
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


@pytest.mark.integrations
def test_integrations_snapshot_22_aws_383d4630_63df_11ed_be08_4b4db5223139(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/aws/kibana/dashboard/aws-383d4630-63df-11ed-be08-4b4db5223139.json`."""
    assert _yaml_for_target(
        'packages/aws/kibana/dashboard/aws-383d4630-63df-11ed-be08-4b4db5223139.json',
        integrations_target_files,
    ) == snapshot("""\
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
    markdown: {content: 'TODO(decompile): unresolved panel reference: panel_1bd92e14-3902-4a5b-bc32-86952f9fdfb0'}
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


@pytest.mark.integrations
def test_integrations_snapshot_23_aws_billing_01aace34_9219_4c6c_80a9_b903af48950f(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/aws_billing/kibana/dashboard/aws_billing-01aace34-9219-4c6c-80a9-b903af48950f.json`."""
    assert _yaml_for_target(
        'packages/aws_billing/kibana/dashboard/aws_billing-01aace34-9219-4c6c-80a9-b903af48950f.json',
        integrations_target_files,
    ) == snapshot("""\
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


@pytest.mark.integrations
def test_integrations_snapshot_24_azure_0f559cc0_f0d5_11e9_90ec_112a988266d5(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/azure/kibana/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5.json`."""
    assert _yaml_for_target(
        'packages/azure/kibana/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Logs Azure] Alerts Overview'
  id: azure-0f559cc0-f0d5-11e9-90ec-112a988266d5
  description: This dashboard provides expanded alerts overview for Azure cloud.
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: azure.activitylogs}
  controls:
  - id: d617c958-32bc-5a3b-503e-1244328b809f
    label: Subscription
    type: options
    field: azure.subscription_id
    fill_width: false
    preselected: []
    data_view: logs-*
  panels:
  - id: 9d1a26e6-2ff0-4d3e-bab3-7bb3c50cd060
    title: Navigation Alerts
    size: {w: 21, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: "### Azure Monitoring\\n\\n[Overview](#/dashboard/azure-41e84340-ec20-11e9-90ec-112a988266d5)
        | [Users](#/dashboard/azure-87095750-f05a-11e9-90ec-112a988266d5) | [**Alerts**](#/dashboard/azure-0f559cc0-f0d5-11e9-90ec-112a988266d5) ",
      font_size: 10, links_in_new_tab: false}
  - id: e5e45365-c81a-4f7f-b58b-8d2d781329a5
    title: Alerts Overview
    size: {w: 27, h: 15}
    position: {x: 21, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 1bf73098-7576-cda2-b39e-c5aabbebd628
        label: Activated
        filter: {kql: 'azure.activitylogs.result_type: "Activated"'}
        aggregation: count
        field: '@timestamp'
      - id: 79be1122-26d2-ade8-c990-5f299529a7f9
        label: Resolved/Succeeded
        filter: {kql: 'azure.activitylogs.result_type: "Resolved" or azure.activitylogs.result_type:
            "Succeeded"'}
        aggregation: count
        field: '@timestamp'
      id: cedc252e-1aae-48fa-f5e7-b45876c77793
      legend: {visible: hide}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 36fb5c08-80d9-4a1c-8fde-9c063381fdd8
    title: Alerts Heatmap
    size: {w: 21, h: 20}
    position: {x: 0, y: 4}
    lens:
      type: heatmap
      id: d03e8dc1-a13b-fac2-3127-7c6a294dfef5
      data_view: logs-*
      x_axis: {id: 67e64ad9-cfc4-92b1-a192-87dafea58540, type: values, field: \n\
          TODO_field}
      y_axis: {id: cc39073e-b1ab-221c-1f1f-4150ee172e9b, type: values, size: 5, \n\
          field: azure.resource.provider}
      metric: {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, \n\
          aggregation: count, field: ___records___}
  - id: 162fb43e-fff3-4f50-aa9b-a713418bd651
    title: Alerts Count
    size: {w: 27, h: 9}
    position: {x: 21, y: 15}
    lens:
      id: bd676e9d-7a12-b074-4273-cf92c544a797
      type: metric
      data_view: logs-*
      primary: {id: 68928132-55cb-befc-37f2-9c98607e83b8, label: Alerts, \n\
          aggregation: count, field: ___records___}
      breakdown:
        id: e0b7c278-4422-8706-dfac-5d3bf3aeb931
        type: filters
        filters:
        - query: {kql: 'azure.activitylogs.result_type : "Activated"'}
          label: Activated
        - query: {kql: 'azure.activitylogs.result_type : "Resolved"'}
          label: Resolved
        - query: {kql: 'azure.activitylogs.result_type : "Succeeded"'}
          label: Succeeded
""")


@pytest.mark.integrations
def test_integrations_snapshot_25_azure_openai_21d9a0d0_e6a0_4b34_bc6d_ce6560a1dab3(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/azure_openai/kibana/dashboard/azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3.json`."""
    assert _yaml_for_target(
        'packages/azure_openai/kibana/dashboard/azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Azure OpenAI] Overview'
  id: azure_openai-21d9a0d0-e6a0-4b34-bc6d-ce6560a1dab3
  description: ''
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: cf955ef2-c987-f646-9cb4-cba112d00bb6
    label: Subscriptions
    type: options
    field: azure.subscription_id
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: ccc608e1-0d73-02a1-ba0f-3601e328f1ca
    label: Resource Group
    type: options
    field: azure.resource.group
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: 179ea6c2-9e55-343b-90dd-8a6712d5f346
    label: Resource Name
    type: options
    field: azure.resource.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: a742531f-2d61-4eca-b069-74ece964034a
    title: Azure OpenAI Link
    hide_title: true
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: 9dae4891-8878-42f2-b429-593d71aae2b1, label: Azure OpenAI Overview, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_9dae4891-8878-42f2-b429-593d71aae2b1_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: 68ffd5fb-7aa9-4ccd-acfd-14fcafb021c8, label: Azure OpenAI PTU \n\
          Deployments, dashboard: \n\
          TODO_dashboard_id_for_link_68ffd5fb-7aa9-4ccd-acfd-14fcafb021c8_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: 8a0a1521-1b26-43dd-81ff-2804312342bd, label: Azure OpenAI Billing, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_8a0a1521-1b26-43dd-81ff-2804312342bd_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: 06d115b9-c21d-4fb1-b643-499f33b9add2, label: Azure OpenAI Content \n\
          Filtering Overview, dashboard: \n\
          TODO_dashboard_id_for_link_06d115b9-c21d-4fb1-b643-499f33b9add2_dashboard,
        new_tab: false, with_time: true, with_filters: false}
  - id: 55ea58ac-730f-4301-80ff-27b30f98b268
    title: ''
    size: {w: 18, h: 12}
    position: {x: 0, y: 4}
    markdown: {content: "# Azure OpenAI\\n\\nPrimary metrics from Azure's OpenAI service.
        This dashboard contains: \\n\\n- Request rates\\n- Error rates\\n- Token usage\\n\\
        - Chat completion latency", font_size: 12, links_in_new_tab: false}
  - id: 6f9d228a-b56a-411c-9153-08f4f8f04037
    title: ''
    hide_title: true
    description: Number of calls made to the Azure OpenAI API over a period of \n\
      time. Applies to PTU, PTU-Managed and Pay-as-you-go deployments.
    size: {w: 7, h: 6}
    position: {x: 18, y: 4}
    lens:
      id: fa24f5ff-906f-54d2-8f49-0e4f5e84d0ea
      type: metric
      data_view: logs-*
      primary:
        id: 8de6ee90-1d28-5d3a-5c23-29db9ca081a8
        label: Total requests
        format: {type: number, decimals: 2, compact: true}
        formula: "count(kql='azure.open_ai.category : \\"RequestResponse\\" ')"
      secondary:
        id: 2ad4f1d2-3674-17a7-e66e-8541946e5d2b
        label: Part of Total requests
        filter: {kql: 'azure.open_ai.category : "RequestResponse" '}
        aggregation: count
        field: ___records___
  - id: e99d4e71-252b-45f7-a3e6-bf627347f683
    title: ''
    hide_title: true
    description: Total token usage(input+output).
    size: {w: 7, h: 6}
    position: {x: 25, y: 4}
    lens:
      id: cc26119b-65d4-c995-6699-9c49e40fbc45
      type: metric
      data_view: metrics-*
      primary:
        id: 86e10925-759e-8fa9-a94c-cdcd921ec6c8
        label: Total tokens
        format: {type: number, decimals: 2, compact: true}
        aggregation: sum
        field: azure.open_ai.token_transaction.total
  - id: 5a0e50a9-2768-47c0-81b7-0c33361f3dd5
    title: Model usage
    description: Top 10 model usage.
    size: {w: 16, h: 12}
    position: {x: 32, y: 4}
    lens:
      id: a9cd0a48-0e9c-c737-9c7b-138803a5d1a9
      type: pie
      appearance: {donut: medium}
      legend: {visible: show}
      data_view: logs-*
      metrics:
      - {id: 45862133-3a58-d112-d754-dfbd3642a4e4, label: Count of records, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 1c3524e7-bd5e-718e-2dbc-804526597c68, type: values, size: 10, field: \n\
          azure.open_ai.properties.model_deployment_name}
  - id: eb83f647-b149-4510-92f1-3a87ff664ee1
    title: ''
    hide_title: true
    description: Total number of calls with error response (HTTP response code \n\
      4xx or 5xx).
    size: {w: 7, h: 6}
    position: {x: 18, y: 10}
    lens:
      id: 2760e814-af85-4314-57e8-5d4be1dd3e97
      type: metric
      data_view: logs-*
      primary: {id: 4d28428b-5042-7353-430e-a25dafe9c296, label: Total errors, \n\
          formula: "count(kql='azure.open_ai.result_signature >= 400 and azure.open_ai.category
          : \\"RequestResponse\\" ')"}
      secondary:
        id: b7819522-e77f-9bb6-81ec-9025f7e651a8
        label: Part of Total errors
        filter: {kql: 'azure.open_ai.result_signature >= 400 and azure.open_ai.category
            : "RequestResponse" '}
        aggregation: count
        field: ___records___
  - id: 2091414b-fbae-451e-8e2a-c7d506f198db
    title: Overall request rate - by model deployment
    description: The overall requests count group by deployed model overtime.
    size: {w: 24, h: 16}
    position: {x: 0, y: 16}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: c46e93e3-382b-238f-67a7-d7b30f212ccf, label: Requests, aggregation: \n\
          sum, field: azure.open_ai.requests.total}
      breakdown: {id: cca1084f-576f-3a61-b364-e50d66b2a307, type: values, size: \n\
          20, field: azure.dimensions.model_deployment_name}
      id: c06ebe7d-847c-40f5-13aa-81738acf2878
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 6fe0e882-52a8-426f-ab07-3829bff17393
    title: Overall error rate - by response code
    description: The overall errors count group by error response code over \n\
      time.
    size: {w: 24, h: 16}
    position: {x: 24, y: 16}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 73002e1d-b7cd-0cf2-26c2-bfb812dcc4ca
        label: Errors
        filter: {kql: 'azure.open_ai.category : "RequestResponse" and azure.open_ai.result_signature
            >=400'}
        aggregation: count
        field: ___records___
      breakdown: {id: c77a3359-1595-2ef1-f076-c357d89b112d, type: values, size: \n\
          20, field: azure.open_ai.result_signature}
      id: 681af99c-5da9-ffe3-bebd-476fa3d29c28
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 980a4a83-bd69-4a1b-8264-3c5f865c545a
    title: Token usage
    description: Processed prompt token (input) and Generated completion token \n\
      (output).
    size: {w: 24, h: 16}
    position: {x: 0, y: 32}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 27f7c2ce-ac29-5c7e-320e-542d12e48387, label: Processed prompt \n\
          tokens, aggregation: sum, field: \n\
          azure.open_ai.processed_prompt_tokens.total}
      - {id: a282c43b-492a-b1b2-f744-e38d2a37e28c, label: Generated completion \n\
          tokens, aggregation: sum, field: azure.open_ai.generated_tokens.total}
      id: f3f655b4-818e-8b4a-d8de-f468e4b47089
      legend: {visible: show}
      type: bar
      appearance:
        y_left_axis: {title: Tokens}
      mode: stacked
  - id: df4e0f6a-2914-4fb7-b25a-4466a84b3b1a
    title: Chat completion latency - by model
    description: The chat completion latency in milliseconds group by model. \n\
      This includes only the chat completion latency and ignores the image model
      latency.
    size: {w: 24, h: 16}
    position: {x: 24, y: 32}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 8aa0536e-6e1c-4107-6bc8-2eef784a70b4, label: 'Response time / ms ', \n\
          formula: \n\
          (average(azure.open_ai.properties.response_time)-average(azure.open_ai.properties.request_time))/10000}
      - id: 81b6b5b7-07db-18d2-c00e-f3447831840a
        label: 'Part of Response time / ms '
        filter: {kql: 'azure.open_ai.operation_name : "ChatCompletions_Create" '}
        aggregation: average
        field: azure.open_ai.properties.response_time
      - id: 61d041c9-5e53-2b47-0caf-8054c5986305
        label: 'Part of Response time / ms '
        filter: {kql: 'azure.open_ai.operation_name : "ChatCompletions_Create" '}
        aggregation: average
        field: azure.open_ai.properties.request_time
      breakdown: {id: 6122303b-def1-30a9-069d-13cb68a0f6f4, type: values, size: \n\
          20, field: azure.open_ai.properties.model_deployment_name}
      id: aadb073e-0073-e13c-dfc8-f77479b886ff
      legend: {visible: show}
      type: bar
      mode: stacked
  - id: 7599e392-ef0a-4a12-85bd-627ad65d6322
    title: Logs
    description: The actual ingested document data for detailed analysis.
    size: {w: 48, h: 18}
    position: {x: 0, y: 48}
    search: {saved_search_id: TODO_saved_search_id}
""")


@pytest.mark.integrations
def test_integrations_snapshot_26_kubernetes_3d4d9290_bcb1_11ec_b64f_7dd6e8e82013(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json`."""
    assert _yaml_for_target(
        'packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics Kubernetes] Pods'
  id: kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013
  description: Metrics about Pods
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  controls:
  - id: f992c139-e52a-09be-55ae-0c599b288c7a
    label: Cluster Name
    type: options
    field: orchestrator.cluster.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: aa9b8e58-ee0f-cecb-5d96-5173d12d6d6a
    label: Namespace Name
    type: options
    field: kubernetes.namespace
    fill_width: false
    preselected: []
    data_view: metrics-*
  - id: e26f06c6-cfa3-00d2-d82d-7c25ee6e7d30
    label: Pod Name
    type: options
    field: kubernetes.pod.name
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: c0a8dc23-df25-4618-8603-15b76ee0ae86
    title: Kubernetes Dashboards [Metrics Kubernetes]
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    markdown: {content: '[Kubernetes Overview](#/view/kubernetes-f4dc26db-1b53-4ea2-a78b-1bfab8ea267c),
        [Kubernetes Nodes](#/view/kubernetes-b945b7b0-bcb1-11ec-b64f-7dd6e8e82013),
        [Kubernetes Pods](#/view/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013),  [Kubernetes
        Deployments](#/view/kubernetes-5be46210-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        StatefulSets](#/view/kubernetes-21694370-bcb2-11ec-b64f-7dd6e8e82013),  [Kubernetes
        DaemonSets](#/view/kubernetes-85879010-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        CronJobs](#/view/kubernetes-0a672d50-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        Jobs](#/view/kubernetes-9bf990a0-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        Volumes](#/view/kubernetes-3912d9a0-bcb2-11ec-b64f-7dd6e8e82013), [Kubernetes
        PV/PVC](#/view/kubernetes-dd081350-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        Services](#/view/kubernetes-ff1b3850-bcb1-11ec-b64f-7dd6e8e82013), [Kubernetes
        API Server](#/view/kubernetes-d3bd9650-0c14-11ed-b760-5d1bccb47f56)', \n\
        font_size: 10, links_in_new_tab: false}
  - id: c077515d-1668-487f-9942-2448a0c25e70
    title: Status per Pod [Metrics Kubernetes]
    size: {w: 48, h: 15}
    position: {x: 0, y: 4}
    lens:
      type: datatable
      appearance: {row_height: auto, header_row_height: single, \n\
          header_row_height_lines: 1, density: normal}
      paging: {enabled: true, page_size: 10}
      id: 9c9f9cf0-1bdf-ec1f-2b3b-d54df09c5848
      data_view: metrics-*
      metrics:
      - id: 0179ab06-e0af-bbe4-5b22-fe4dfbc1b209
        label: Phase
        filter: {kql: 'kubernetes.pod.status.phase: *'}
        aggregation: last_value
        field: kubernetes.pod.status.phase
      - id: 90ac78d9-ba09-1fd7-0312-1e73917829ed
        label: Ready
        filter: {kql: 'kubernetes.pod.status.ready: *'}
        aggregation: last_value
        field: kubernetes.pod.status.ready
      - id: 090e75fd-f7cc-a5d1-da29-a84b5c6efc1e
        label: Scheduled
        filter: {kql: 'kubernetes.pod.status.scheduled: *'}
        aggregation: last_value
        field: kubernetes.pod.status.scheduled
      breakdowns:
      - {id: b438d745-cf29-3a05-f104-ba7988a77c5a, type: values, size: 1000, \n\
          field: kubernetes.pod.name}
  - id: 23852bac-d857-4a32-95f3-8100d6abd976
    title: CPU Usage as Pct of the Total Node CPU [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 19}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 85ac8c09-a57a-b784-a69e-2e36358fc6be
        label: CPU Usage
        format: {type: percent, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: average
        field: kubernetes.pod.cpu.usage.node.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: d5f69190-d095-d772-3801-b916647eda20
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 9567b72e-6e79-479b-a5b1-1d9f81d258bd
    title: CPU Usage as Pct of the Defined Pod Limit [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 24, y: 19}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 7bd442e3-45cb-983e-b1e2-e4bc9cdaea4b
        label: CPU Usage
        format: {type: percent, decimals: 2}
        filter: {kql: ''}
        aggregation: average
        field: kubernetes.pod.cpu.usage.limit.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: 7cd11fb2-ce3e-cf35-6e63-e6ed165cad80
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 6b939075-346d-4aa1-b634-bf57b8cc1532
    title: Memory Usage as Pct of the Total Node Memory [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 34}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 95e57d73-0b62-bc82-0755-c9f1c4b3f0c6
        label: Memory Usage
        format: {type: percent, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: average
        field: kubernetes.pod.memory.usage.node.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: d6cc9df9-bea7-9c63-c6ff-27b458c2f8b4
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 54bfc973-09ca-4ebe-a777-c790087c3a91
    title: Memory Usage as Pct of the Defined Pod Limit [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 24, y: 34}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: db624464-333a-8a69-c301-d8974eb9575c
        label: Memory Usage
        format: {type: percent, decimals: 2}
        filter: {kql: ''}
        aggregation: average
        field: kubernetes.pod.memory.usage.limit.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: 8a3c00fe-7adb-2dbb-1889-f23d9864f762
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 6459a5c9-80c5-46d8-968f-5b0a40b2eee0
    title: Working Set Memory Usage as Pct of the Defined Pod Limit [Metrics \n\
      Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 49}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 2d3e959b-5943-c22d-3aaf-c057dcd45894
        label: Memory Usage
        format: {type: percent, decimals: 2}
        filter: {kql: ''}
        aggregation: average
        field: kubernetes.pod.memory.working_set.limit.pct
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: d6e96fcf-3f2a-44b8-d88f-a1157b288810
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 06ded777-f88c-40c8-93fa-1f0ed71ed43a
    title: Network Outgoing Bytes per Pod [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 24, y: 49}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: b942c2f5-1abc-49f5-025b-573c822206ff
        label: Network Usage
        format: {type: bytes, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: last_value
        field: kubernetes.pod.network.tx.bytes
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: fbe2d09f-eb69-ceeb-9493-f856e43fa055
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
  - id: 83f2689a-838b-4d73-8d92-8dd358c33329
    title: Network Incoming Bytes per Pod [Metrics Kubernetes]
    size: {w: 24, h: 15}
    position: {x: 0, y: 64}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: 6a8cd549-4911-a234-a683-af180bae572b
        label: Network Usage
        format: {type: bytes, decimals: 2}
        filter: {kql: 'kubernetes.pod.cpu.usage.node.pct: *'}
        aggregation: last_value
        field: kubernetes.pod.network.rx.bytes
      breakdown: {id: cb759e25-47d2-ad1c-3ca5-25e7b37b8f00, type: values, size: \n\
          10, field: kubernetes.pod.name}
      id: 669a7ae0-73ae-ad6a-39b9-0a89ed9ab15c
      legend: {visible: show, width: large}
      type: area
      appearance:
        y_left_axis: {title: false}
      mode: stacked
""")


@pytest.mark.integrations
def test_integrations_snapshot_27_mysql_logs_mysql_dashboard(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json`."""
    assert _yaml_for_target(
        'packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Logs MySQL] Overview'
  id: mysql-Logs-MySQL-Dashboard
  description: Overview dashboard for the Logs MySQL integration
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [mysql.error, mysql.slowlog]
  panels:
  - id: '1'
    title: Top slowest queries [Logs MySQL]
    size: {w: 24, h: 20}
    position: {x: 0, y: 28}
    lens:
      type: datatable
      appearance: {row_height: single, header_row_height: single, density: \n\
          normal}
      paging: {enabled: true, page_size: 10}
      id: 3f68aff4-efd0-853c-a305-f819a28c83ca
      data_view: logs-*
      metrics:
      - id: e2ad6534-dddb-8f6e-50c0-9335b78ab605
        label: Query time (ms)
        format: {type: number, decimals: 2}
        formula: max(event.duration)/1000000
      - {id: 9ce5a389-ce65-794f-f251-099e2eb8c699, label: Part of Query time, \n\
          aggregation: max, field: event.duration}
      breakdowns:
      - {id: 5d3c36e4-47ea-6d0c-56df-ae4db7870141, type: values, size: 5, field: \n\
          mysql.slowlog.query}
      - {id: 8796bbeb-09f2-cde1-db44-f3876594529f, type: values, size: 5, field: \n\
          user.name}
  - id: '2'
    title: Slow queries over time [Logs MySQL]
    size: {w: 24, h: 12}
    position: {x: 0, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 6b279897-7436-6186-81e5-53853d38f824, label: Slow queries, \n\
          aggregation: count, field: ___records___}
      id: 439152fd-f182-38ae-2ee0-6d95fa50ca8e
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        x_axis: {title: '@timestamp per 30 seconds'}
        y_left_axis: {title: Slow queries}
      mode: stacked
  - id: '3'
    title: Error logs over time [Logs MySQL]
    size: {w: 24, h: 12}
    position: {x: 24, y: 0}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 0bdd6627-4c9b-2fb2-eda7-ed6d4cc3d49a, label: Error logs, \n\
          aggregation: count, field: ___records___}
      id: 0bd158c8-0a10-108a-63f1-baf3267dd775
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      appearance:
        x_axis: {title: '@timestamp per 30 seconds'}
        y_left_axis: {title: Error logs}
      mode: stacked
  - id: '5'
    title: Error logs levels breakdown [Logs MySQL]
    size: {w: 24, h: 16}
    position: {x: 24, y: 12}
    lens:
      id: 79334a28-b3c6-076d-e9d8-4658fde81a01
      type: pie
      appearance:
        values: {decimal_places: 2}
      legend: {visible: show, position: bottom, truncate_labels: 1}
      data_view: logs-*
      metrics:
      - {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: cce5efe2-b956-597b-69f9-9a771b3a0b2a, type: values, size: 5, field: \n\
          log.level}
  - id: '6'
    title: Slow logs breakdown [Logs MySQL]
    size: {w: 24, h: 16}
    position: {x: 0, y: 12}
    lens:
      id: 68eeb524-7985-7df7-e4f2-eab0d00db9ca
      type: pie
      appearance:
        values: {decimal_places: 2}
      legend: {visible: show, position: bottom, truncate_labels: 1}
      data_view: logs-*
      metrics:
      - {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdowns:
      - {id: c3744947-3e00-020e-b25d-b3b051be5ead, type: values, size: 5, field: \n\
          mysql.slowlog.query}
  - id: 4d60bed6-79cf-4852-bf1b-224bd94635fe
    title: Error logs [Logs MySQL]
    size: {w: 24, h: 20}
    position: {x: 24, y: 28}
    search: {saved_search_id: TODO_saved_search_id}
""")


@pytest.mark.integrations
def test_integrations_snapshot_28_nginx_023d2930_f1a5_11e7_a9ef_93c69af7b129(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json`."""
    assert _yaml_for_target(
        'packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics Nginx] Overview'
  id: nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129
  description: Overview dashboard for the Nginx integration in Metrics
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: true}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: nginx.stubstatus}
  controls:
  - id: adc4ed90-888b-a0a5-f7bb-874592448bfa
    label: Nginx instance
    type: options
    field: host.hostname
    fill_width: false
    preselected: []
    data_view: metrics-*
  panels:
  - id: 634a8822-9fdf-4abd-a881-b22fa0a43883
    title: Total requests
    size: {w: 16, h: 10}
    position: {x: 0, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 815327a7-9499-b336-1de4-6e81839d589b, label: Total, aggregation: \n\
          max, field: nginx.stubstatus.requests}
      id: 15c2ccbd-b4ca-bcc0-3066-79cd638721aa
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Total}
        missing_values: linear
        show_as_dotted: true
  - id: 7feb4b0c-7f27-4f31-9745-e93376a773b5
    title: Processed requests
    size: {w: 16, h: 10}
    position: {x: 16, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 01ed5bb2-612f-f097-6988-29ecb3535f6d, label: Processed, aggregation: \n\
          max, field: nginx.stubstatus.handled}
      id: bbfe074b-7d12-2417-070c-d28d33e53c99
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance: {missing_values: linear, show_as_dotted: true}
  - id: 16841075-2904-4a7e-b305-988646a2e88a
    title: Heartbeat / Up
    size: {w: 16, h: 10}
    position: {x: 32, y: 0}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 0abfce95-8220-354b-6220-7f92ef4e5f83, label: Up, aggregation: \n\
          unique_count, field: host.hostname}
      id: 52c615bd-917d-8ede-ad90-119f999ab953
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance: {missing_values: linear, show_as_dotted: true}
  - id: 45dee013-0721-4e1f-8d06-b8fb5e6ec462
    title: Active connections
    size: {w: 23, h: 13}
    position: {x: 0, y: 10}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: aee3ce5e-608c-d03c-a2e7-899c43fea927
        label: Active
        format: {type: number, decimals: 0}
        aggregation: average
        field: nginx.stubstatus.active
      id: e7cd0234-3e6d-155c-07a3-0c665c753489
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Active}
  - id: 194effcd-61a9-4239-8b53-9d8793cefde1
    title: Reading / Writing / Waiting Rates
    size: {w: 25, h: 13}
    position: {x: 23, y: 10}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - id: bc872dd7-fa35-1d39-3ccb-581b326711f1
        label: Reading
        format: {type: number, decimals: 1}
        aggregation: average
        field: nginx.stubstatus.reading
      - id: c82a421f-1b8a-52bc-510e-10734c630b25
        label: Writing
        format: {type: number, decimals: 1}
        aggregation: average
        field: nginx.stubstatus.writing
      - id: 2582d3cf-9c2b-9305-3812-c53e99b22605
        label: Waiting
        format: {type: number, decimals: 1}
        aggregation: average
        field: nginx.stubstatus.waiting
      id: 6394953b-a86d-5046-73af-52dd258d7c67
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
  - id: ffa68274-1f0b-468e-9ff5-f486a1501307
    title: Request Rate
    size: {w: 16, h: 12}
    position: {x: 0, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 1dda1d54-5b38-9be6-0e41-c6bb7c04a040, label: Maximum of \n\
          nginx.stubstatus.requests, aggregation: max, field: \n\
          nginx.stubstatus.requests}
      id: 241c67fe-1287-6b49-6440-75874416033f
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
  - id: 1711ea62-d9f5-418c-b244-81dc1832b9ef
    title: Accepts and Handled Rate
    size: {w: 16, h: 12}
    position: {x: 16, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: b83e05a4-3e1a-b372-ff61-7cae32f570e3, label: Maximum of \n\
          nginx.stubstatus.accepts, aggregation: max, field: \n\
          nginx.stubstatus.accepts}
      - {id: 8f41cf89-53b1-3479-5838-c69bd211b0a1, label: Maximum of \n\
          nginx.stubstatus.handled, aggregation: max, field: \n\
          nginx.stubstatus.handled}
      id: b714cdd1-b31a-7158-c8bb-60f3cacc047b
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
  - id: 8fd75d58-0b72-47f4-b500-d0091e60bf3e
    title: Drops Rate
    size: {w: 16, h: 12}
    position: {x: 32, y: 23}
    lens:
      data_view: metrics-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: e8c4132d-a05a-6f5d-472b-7d1217283b12, label: Maximum of \n\
          nginx.stubstatus.dropped, aggregation: max, field: \n\
          nginx.stubstatus.dropped}
      id: 7d1d37fb-546c-347e-87c1-f85339ecc467
      legend: {visible: show, position: bottom, show_single_series: true}
      type: line
      appearance:
        y_left_axis: {title: Rate}
""")


@pytest.mark.integrations
def test_integrations_snapshot_29_system_logs_syslog_dashboard(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json`."""
    assert _yaml_for_target(
        'packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Logs System] Syslog dashboard'
  id: system-Logs-syslog-dashboard
  description: Syslog dashboard from the Logs System integration
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - {field: data_stream.dataset, equals: system.syslog}
  panels:
  - id: '4'
    title: Dashboards
    size: {w: 48, h: 4}
    position: {x: 0, y: 0}
    links:
      layout: horizontal
      items:
      - {id: system-Logs-syslog-dashboard, label: Syslog, dashboard: \n\
          TODO_dashboard_id_for_link_system-Logs-syslog-dashboard_dashboard, \n\
          new_tab: false, with_time: true, with_filters: false}
      - {id: system-277876d0-fa2c-11e6-bbd3-29c986c96e5a, label: Sudo commands, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_system-277876d0-fa2c-11e6-bbd3-29c986c96e5a_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: system-5517a150-f9ce-11e6-8115-a7c18106d86a, label: SSH logins, \n\
          dashboard: \n\
          TODO_dashboard_id_for_link_system-5517a150-f9ce-11e6-8115-a7c18106d86a_dashboard,
        new_tab: false, with_time: true, with_filters: false}
      - {id: system-0d3f2380-fa78-11e6-ae9b-81e5311e8cab, label: New users and \n\
          groups, dashboard: \n\
          TODO_dashboard_id_for_link_system-0d3f2380-fa78-11e6-ae9b-81e5311e8cab_dashboard,
        new_tab: false, with_time: true, with_filters: false}
  - id: 1c0a80d4-cd4d-488a-a06d-e9b816e733a8
    title: Syslog events by hostname
    size: {w: 32, h: 16}
    position: {x: 0, y: 4}
    lens:
      data_view: logs-*
      dimension: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram,
        field: '@timestamp'}
      metrics:
      - {id: 4b828384-df36-004a-b6da-37bcab7e5f18, label: Count, aggregation: \n\
          count, field: ___records___}
      breakdown: {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: \n\
          5, field: host.hostname}
      id: cacf4e9a-9fb7-5f22-4c5f-a37b28c41fc8
      legend: {visible: show, show_single_series: true, truncate_labels: 1}
      type: bar
      mode: stacked
  - id: 30ce1a8d-6460-45b6-be1a-841db5ca7c8b
    title: Syslog hostnames and processes
    size: {w: 16, h: 16}
    position: {x: 32, y: 4}
    lens:
      id: 9faf9364-addc-80f3-946a-5018ca596574
      type: treemap
      appearance:
        values: {decimal_places: 2}
      legend: {visible: hide, position: bottom, truncate_labels: 1}
      data_view: logs-*
      metric: {id: ed85e2e8-53f2-5576-18cb-a03460a48b3b, label: Count, \n\
          aggregation: count, field: ___records___}
      breakdowns:
      - {id: 0ab3bb62-cf29-0994-1271-aba22c914b98, type: values, size: 5, field: \n\
          host.hostname}
      - {id: cf40b962-6df3-09a0-9724-8adf72638e3e, type: values, size: 5, field: \n\
          process.name}
  - id: f08ec141-4b46-4e87-9b1c-3bb1bb502d3e
    title: Syslog logs
    size: {w: 48, h: 28}
    position: {x: 0, y: 20}
    search: {saved_search_id: TODO_saved_search_id}
""")


@pytest.mark.integrations
def test_integrations_snapshot_30_system_metrics_system_overview(integrations_target_files: dict[str, Path]) -> None:
    """Snapshot decompile YAML for `packages/system/kibana/dashboard/system-Metrics-system-overview.json`."""
    assert _yaml_for_target(
        'packages/system/kibana/dashboard/system-Metrics-system-overview.json',
        integrations_target_files,
    ) == snapshot("""\
dashboards:
- name: '[Metrics System] Overview'
  id: system-Metrics-system-overview
  description: Overview of system metrics
  settings:
    margins: true
    sync: {cursor: true, tooltips: false, colors: false}
    titles: true
  query: {kql: ''}
  filters:
  - field: data_stream.dataset
    in: [system.process, system.fsstat, system.cpu, system.memory, \n\
        system.network]
  panels:
  - id: 471f7546-e704-4a38-a041-d8b11869d7cc
    title: System Navigation
    hide_title: true
    size: {w: 48, h: 5}
    position: {x: 0, y: 0}
    markdown: {content: "# System overview\\n\\nTo view host details, select a host
        from the list below by clicking the respective label.", font_size: 12, \n\
        links_in_new_tab: false}
  - id: aa7fddcf-8146-4d85-b3d7-d37a99a5ff32
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 0, y: 5}
    lens:
      id: 1e5b399d-681f-0b61-85cb-826bc084e826
      type: metric
      data_view: metrics-*
      primary:
        id: 49948a83-0e0b-fc06-d408-6408223553ba
        label: Memory used
        format: {type: percent, compact: true}
        filter: {kql: 'system.memory.actual.used.pct: *'}
        aggregation: last_value
        field: system.memory.actual.used.pct
  - id: 9fc7a050-de1b-495b-8ca7-2a852ed5a28c
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 9, y: 5}
    lens:
      id: 03e69969-5962-dc34-36ce-0f5fe61debe1
      type: metric
      data_view: metrics-*
      primary:
        id: 74e34c2f-6c02-b4b8-624d-0de03644791a
        label: CPU used
        format: {type: percent, compact: true}
        filter: {kql: 'system.cpu.total.norm.pct: *'}
        aggregation: last_value
        field: system.cpu.total.norm.pct
  - id: 234c40f8-f787-49a9-b1d3-1d3340e0ebaa
    title: Top Hosts by CPU
    hide_title: true
    size: {w: 30, h: 21}
    position: {x: 18, y: 5}
    lens:
      type: datatable
      id: 35965e26-8165-1adc-1618-16907eefc1f6
      data_view: TODO_data_view
      metrics:
      - id: 9bf8fdfb-d02e-0662-e44e-4e36a552ae99
        label: CPU usage
        format: {type: percent}
        filter: {kql: '"system.cpu.total.norm.pct": *'}
        aggregation: last_value
        field: system.cpu.total.norm.pct
      - id: 601d050d-9c29-eb5e-a631-5ae5a082877b
        label: Memory usage
        format: {type: percent}
        filter: {kql: '"system.memory.actual.used.pct": *'}
        aggregation: last_value
        field: system.memory.actual.used.pct
      breakdowns:
      - {id: ce2d4ae7-0c85-a2d6-f606-b1cd016bc589, type: values, size: 1000, \n\
          field: host.name}
  - id: f95d2a8f-0ec2-4252-b3e8-8771b9165241
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 0, y: 12}
    lens:
      id: 70dd394c-840e-735a-1813-a834e4841a23
      type: metric
      data_view: metrics-*
      primary: {id: b7966ae2-9ab7-5a96-b3aa-c7cf6f859afc, label: Hosts, formula: \n\
          unique_count(host.name)}
      secondary: {id: 1b2e0a6b-24c9-a866-7559-702820af3e8c, label: Part of Hosts,
        aggregation: unique_count, field: host.name}
  - id: 4a59a56e-e5fd-4ff3-b2f0-8a1c07be572b
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 9, y: 12}
    lens:
      id: 4c3f868b-b07f-9934-f672-8d945f6842ec
      type: metric
      data_view: metrics-*
      primary:
        id: a50f00c3-90b7-f788-d613-5bb0e6ee222b
        label: Disk used
        format: {type: percent, compact: true}
        formula: 'last_value(system.fsstat.total_size.used)/last_value(system.fsstat.total_size.total) '
      secondary:
        id: d9761885-2890-9c8f-814a-1564b66a9fb9
        label: Part of Disk used
        filter: {kql: '"system.fsstat.total_size.used": *'}
        aggregation: last_value
        field: system.fsstat.total_size.used
  - id: 4fdb14ab-c349-489b-afc1-55603ddb52f3
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 0, y: 19}
    lens:
      id: c95f2503-75ca-90d5-b31a-231b19c9a359
      type: metric
      data_view: metrics-*
      primary:
        id: ef238bd0-3843-eb3c-dcc4-a4510f88792a
        label: Inbound traffic per second
        format: {type: bytes, decimals: 2}
        formula: (max(system.network.in.bytes, reducedTimeRange='30s') - \n\
          min(system.network.in.bytes, reducedTimeRange='30s')) / 30
      secondary: {id: 4d71a8ea-5063-0095-d2db-2435f5e6bf45, label: Part of \n\
          Inbound Traffic per second, aggregation: max, field: \n\
          system.network.in.bytes}
  - id: fe4dd8cc-1c8d-4b88-8db3-4a286b33984f
    title: ''
    hide_title: true
    size: {w: 9, h: 7}
    position: {x: 9, y: 19}
    lens:
      id: 035c6a75-3c54-f2b8-e68d-4be7de591263
      type: metric
      data_view: metrics-*
      primary:
        id: acd50f90-caee-9706-98de-e4253ed6eef0
        label: Outbound traffic per second
        format: {type: bytes, decimals: 2}
        formula: (max(system.network.out.bytes, reducedTimeRange='30s') - \n\
          min(system.network.out.bytes, reducedTimeRange='30s')) / 30
      secondary: {id: f63a1eb6-47fa-eff6-c4bd-107179e2c576, label: Part of \n\
          Outbound Traffic per second, aggregation: max, field: \n\
          system.network.out.bytes}
  - id: e6f8fdab-5f7e-42b1-9093-36c017e0d26d
    title: Top hosts by CPU usage over time
    size: {w: 48, h: 15}
    position: {x: 0, y: 26}
    lens:
      type: heatmap
      id: 74a4b7a9-af0c-9d2d-3323-9ebcc92ad871
      data_view: metrics-*
      x_axis: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram, \n\
          field: '@timestamp'}
      y_axis: {id: 9e654e1c-02e0-7f4b-b5c0-93958e779b8f, type: values, size: 20, \n\
          field: host.name}
      metric:
        id: c7e21c64-ad6c-5791-5b06-80703124f1e3
        label: CPU Usage
        format: {type: percent, decimals: 0}
        aggregation: average
        field: system.cpu.user.norm.pct
  - id: e6f6cabf-ecec-482f-b7b5-634e323e9a15
    title: Top hosts by memory usage over time
    size: {w: 48, h: 16}
    position: {x: 0, y: 41}
    lens:
      type: heatmap
      id: 45c80a3b-eb7c-7fb0-9e12-6d4025f79ebd
      data_view: metrics-*
      x_axis: {id: 8d8b7676-c4af-9ec1-d403-657f98d8eab3, type: date_histogram, \n\
          field: '@timestamp'}
      y_axis: {id: 9e654e1c-02e0-7f4b-b5c0-93958e779b8f, type: values, size: 20, \n\
          field: host.name}
      metric:
        id: d39c121c-1182-d4e8-cd09-89d74dc90d92
        label: Memory Usage
        format: {type: percent, decimals: 0}
        formula: average(system.memory.actual.used.pct)
""")
