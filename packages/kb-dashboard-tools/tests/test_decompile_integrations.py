"""Opt-in integrations-backed decompiler tests."""

import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from inline_snapshot import snapshot
from ruamel.yaml import YAML

from kb_dashboard_tools.decompile import decompile_dashboard

from .integrations_targets import INTEGRATIONS_DASHBOARD_TARGETS, INTEGRATIONS_PINNED_SHA


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
    # Snapshot canonical YAML content only (strip ruamel comments/TODO JSON blobs).
    canonical = json.loads(json.dumps(decompile_dashboard(dashboard)))
    yaml = YAML(typ='safe')
    yaml_any = cast('Any', yaml)
    yaml_any.sort_base_mapping_type_on_output = False
    stream = io.StringIO()
    yaml.dump(canonical, stream)
    return stream.getvalue()


@pytest.fixture(scope='session')
def integrations_target_files(integrations_repo_path: Path, integrations_pinned_sha: str) -> list[tuple[str, Path]]:
    """Resolve hardcoded dashboard files to test from integrations fixture clone."""
    if integrations_pinned_sha != INTEGRATIONS_PINNED_SHA:
        message_template = 'inline snapshots are pinned to {pinned}; got {got}. Use --integrations-sha {pinned}.'
        message = message_template.format(pinned=INTEGRATIONS_PINNED_SHA, got=integrations_pinned_sha)
        pytest.skip(message)
    resolved = [(rel, integrations_repo_path / rel) for rel in INTEGRATIONS_DASHBOARD_TARGETS]
    missing = [path for _, path in resolved if not path.exists()]
    if missing:
        pytest.fail(f'missing hardcoded integrations dashboards: {missing}')
    return resolved


@pytest.mark.integrations
def test_integrations_decompile_yaml_inline_snapshots(integrations_target_files: list[tuple[str, Path]]) -> None:
    """Inline-snapshot generated YAML for selected integrations dashboards."""
    actual_outputs: list[dict[str, str]] = []
    for source_label, source_path in integrations_target_files:
        first_dashboard = next(_iter_dashboard_objects(source_path), None)
        if first_dashboard is None:
            continue
        actual_outputs.append(
            {
                'source': source_label,
                'yaml': _decompile_yaml_text(first_dashboard),
            }
        )
    assert actual_outputs == snapshot(
        [
            {
                'source': 'packages/apache/kibana/dashboard/apache-Logs-Apache-Dashboard.json',
                'yaml': """\
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
""",
            },
            {
                'source': 'packages/nginx/kibana/dashboard/nginx-023d2930-f1a5-11e7-a9ef-93c69af7b129.json',
                'yaml': """\
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
""",
            },
            {
                'source': 'packages/mysql/kibana/dashboard/mysql-Logs-MySQL-Dashboard.json',
                'yaml': """\
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
""",
            },
            {
                'source': 'packages/system/kibana/dashboard/system-Metrics-system-overview.json',
                'yaml': """\
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
""",
            },
            {
                'source': 'packages/system/kibana/dashboard/system-Logs-syslog-dashboard.json',
                'yaml': """\
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
""",
            },
            {
                'source': 'packages/kubernetes/kibana/dashboard/kubernetes-3d4d9290-bcb1-11ec-b64f-7dd6e8e82013.json',
                'yaml': """\
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
""",
            },
        ]
    )
