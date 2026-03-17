"""Tests for schema upgrade command."""

from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from click.testing import CliRunner

from dashboard_compiler.cli import cli


def _read_yaml(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    assert isinstance(data, dict)
    return data


class TestUpgradeCommand:
    """Tests for upgrade command registration and migration behavior."""

    def test_upgrade_command_is_registered(self) -> None:
        """Upgrade command is available from the top-level CLI."""
        command_names = list(cli.commands)
        assert 'upgrade' in command_names

    def test_upgrade_check_mode_does_not_write(self, tmp_path: Path) -> None:
        """Check mode reports pending upgrades without mutating files."""
        input_file = tmp_path / 'legacy.yaml'
        input_file.write_text(
            """
dashboards:
  - id: demo
    name: Demo
    panels:
      - lens:
          type: pie
          data_view: logs-*
          metrics:
            - aggregation: count
          dimensions:
            - type: values
              field: service.name
              other_bucket: true
""".strip()
            + '\n',
            encoding='utf-8',
        )

        before = input_file.read_text(encoding='utf-8')
        runner = CliRunner()
        result = runner.invoke(cli, ['upgrade', '--input-file', str(input_file), '--fail-on-change'])

        assert result.exit_code == 1
        assert 'Upgrade needed:' in result.output
        assert 'would be applied' in result.output
        assert input_file.read_text(encoding='utf-8') == before

    def test_upgrade_write_migrates_legacy_fields(self, tmp_path: Path) -> None:
        """Write mode rewrites representative 0.2.7 legacy fields to canonical 0.4.0 schema."""
        input_file = tmp_path / 'legacy.yaml'
        input_file.write_text(
            """
dashboards:
  - id: demo
    name: Demo
    panels:
      - lens:
          type: datatable
          data_view: logs-*
          dimensions:
            - id: dim-1
              type: values
              field: service.name
              other_bucket: true
          dimensions_by:
            - id: split-1
              type: values
              field: host.name
          metrics:
            - id: metric-1
              aggregation: count
          columns:
            - column_id: dim-1
              width: 180
            - column_id: metric-1
              color_mode: text
          metric_columns:
            - column_id: metric-1
              summary_row: sum
      - lens:
          type: metric
          data_view: logs-*
          apply_to: cell
          color:
            range_type: percent
            continuity: all
            thresholds:
              - up_to: 80
                color: '#00BF6F'
          primary:
            aggregation: count
""".strip()
            + '\n',
            encoding='utf-8',
        )

        runner = CliRunner()
        result = runner.invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0
        assert 'Upgraded' in result.output

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        panel_datatable = cast('dict[str, Any]', panels[0]['lens'])
        panel_metric = cast('dict[str, Any]', panels[1]['lens'])

        assert 'breakdowns' in panel_datatable
        assert 'dimensions' not in panel_datatable
        assert 'metrics_split_by' in panel_datatable
        assert 'dimensions_by' not in panel_datatable
        assert 'columns' not in panel_datatable
        assert 'metric_columns' not in panel_datatable
        assert panel_datatable['breakdowns'][0]['show_other_bucket'] is True
        assert panel_datatable['metrics'][0]['color']['apply_to'] == 'text'
        assert panel_datatable['metrics'][0]['appearance']['summary_row'] == 'sum'

        assert 'color' not in panel_metric
        assert 'apply_to' not in panel_metric
        assert panel_metric['primary']['color']['apply_to'] == 'cell'
        assert 'continuity' not in panel_metric['primary']['color']

    def test_upgrade_handles_elastic_integrations_nginx_fixture_patterns(self, tmp_path: Path) -> None:
        """Upgrades deprecated pie/datatable dimensions from nginx_otel-style dashboard YAML."""
        input_file = tmp_path / 'nginx-fixture.yaml'
        input_file.write_text(
            """
dashboards:
  - id: nginx-fixture
    name: Nginx Fixture
    panels:
      - lens:
          type: pie
          data_view: logs-*
          dimensions:
            - field: attributes.http.response.status_code
              type: values
          metrics:
            - aggregation: count
      - lens:
          type: datatable
          data_view: logs-*
          dimensions:
            - field: attributes.url.original
              type: values
          metrics:
            - aggregation: count
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        pie_chart = cast('dict[str, Any]', panels[0]['lens'])
        table_chart = cast('dict[str, Any]', panels[1]['lens'])

        assert 'dimensions' not in pie_chart
        assert 'breakdowns' in pie_chart
        assert 'dimensions' not in table_chart
        assert 'breakdowns' in table_chart

    def test_upgrade_handles_elastic_integrations_iis_esql_datatable_patterns(self, tmp_path: Path) -> None:
        """Upgrades ES|QL datatable dimensions to breakdowns from iis_otel-style YAML."""
        input_file = tmp_path / 'iis-fixture.yaml'
        input_file.write_text(
            """
dashboards:
  - id: iis-fixture
    name: IIS Fixture
    panels:
      - esql:
          type: datatable
          query:
            - FROM metrics-iisreceiver.otel-*
            - STATS total_requests = SUM(`iis.request.count`) BY iis.site
          dimensions:
            - field: iis.site
              label: Site
          metrics:
            - field: total_requests
              label: Total Requests
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        chart = cast('dict[str, Any]', panels[0]['esql'])

        assert 'dimensions' not in chart
        assert 'breakdowns' in chart

    def test_upgrade_migrates_pie_titles_and_legend_visible_bool(self, tmp_path: Path) -> None:
        """Migrates pie titles_and_text and bool legend visibility to canonical fields."""
        input_file = tmp_path / 'pie-legacy.yaml'
        input_file.write_text(
            """
dashboards:
  - id: pie-legacy
    name: Pie Legacy
    panels:
      - lens:
          type: pie
          data_view: logs-*
          dimensions:
            - field: service.name
              type: values
          metrics:
            - aggregation: count
          titles_and_text:
            slice_labels: inside
            slice_values: percent
            value_decimal_places: 1
          legend:
            visible: true
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        chart = cast('dict[str, Any]', panels[0]['lens'])

        assert 'titles_and_text' not in chart
        assert chart['appearance']['categories']['position'] == 'inside'
        assert chart['appearance']['values']['format'] == 'percent'
        assert chart['appearance']['values']['decimal_places'] == 1
        assert chart['legend']['visible'] == 'show'

    def test_upgrade_preserves_legacy_key_when_target_key_already_exists(self, tmp_path: Path) -> None:
        """When target key already exists, skip rename without dropping legacy key data."""
        input_file = tmp_path / 'conflict.yaml'
        input_file.write_text(
            """
dashboards:
  - id: conflict
    name: Conflict
    panels:
      - lens:
          type: datatable
          data_view: logs-*
          breakdowns:
            - id: new-breakdown
              type: values
              field: service.name
          dimensions:
            - id: legacy-dimension
              type: values
              field: host.name
          metrics:
            - aggregation: count
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        chart = cast('dict[str, Any]', panels[0]['lens'])
        assert chart['breakdowns'][0]['id'] == 'new-breakdown'
        assert chart['dimensions'][0]['id'] == 'legacy-dimension'

    def test_upgrade_migrates_esql_gauge_static_bounds(self, tmp_path: Path) -> None:
        """Numeric minimum/maximum/goal on ESQL gauge are converted to EVAL expressions."""
        input_file = tmp_path / 'esql-gauge.yaml'
        input_file.write_text(
            """
dashboards:
  - id: esql-gauge
    name: ESQL Gauge
    panels:
      - esql:
          type: gauge
          query: "FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)"
          metric:
            field: avg_cpu
          minimum: 0
          maximum: 100
          goal: 95
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0
        assert 'Upgraded' in result.output

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        chart = cast('dict[str, Any]', panels[0]['esql'])

        assert '| EVAL _gauge_min = 0, _gauge_max = 100, _gauge_goal = 95' in chart['query']
        assert chart['minimum'] == {'field': '_gauge_min'}
        assert chart['maximum'] == {'field': '_gauge_max'}
        assert chart['goal'] == {'field': '_gauge_goal'}

    def test_upgrade_migrates_esql_gauge_static_bounds_list_query(self, tmp_path: Path) -> None:
        """Numeric bounds migration works when the ESQL query is a list of strings."""
        input_file = tmp_path / 'esql-gauge-list.yaml'
        input_file.write_text(
            """
dashboards:
  - id: esql-gauge-list
    name: ESQL Gauge List
    panels:
      - esql:
          type: gauge
          query:
            - FROM metrics-*
            - STATS avg_cpu = AVG(system.cpu.total.pct)
          metric:
            field: avg_cpu
          minimum: 0
          maximum: 1.0
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        chart = cast('dict[str, Any]', panels[0]['esql'])

        query_parts = chart['query']
        assert isinstance(query_parts, list)
        last_part = query_parts[-1]
        assert '_gauge_min = 0' in last_part
        assert '_gauge_max = 1.0' in last_part
        assert chart['minimum'] == {'field': '_gauge_min'}
        assert chart['maximum'] == {'field': '_gauge_max'}
        assert chart.get('goal') is None

    def test_upgrade_skips_esql_gauge_when_bounds_are_already_fields(self, tmp_path: Path) -> None:
        """No migration when minimum/maximum/goal are already field references."""
        input_file = tmp_path / 'esql-gauge-fields.yaml'
        input_file.write_text(
            """
dashboards:
  - id: esql-gauge-fields
    name: ESQL Gauge Fields
    panels:
      - esql:
          type: gauge
          query: "FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct), min_cpu = MIN(system.cpu.total.pct)"
          metric:
            field: avg_cpu
          minimum:
            field: min_cpu
""".strip()
            + '\n',
            encoding='utf-8',
        )

        before = input_file.read_text(encoding='utf-8')
        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--fail-on-change'])
        assert result.exit_code == 0
        assert 'No upgrades needed' in result.output
        assert input_file.read_text(encoding='utf-8') == before

    def test_upgrade_renames_heatmap_value_to_metric(self, tmp_path: Path) -> None:
        """Heatmap `value:` field is renamed to `metric:`."""
        input_file = tmp_path / 'heatmap.yaml'
        input_file.write_text(
            """
dashboards:
  - id: heatmap-test
    name: Heatmap Test
    panels:
      - lens:
          type: heatmap
          data_view: logs-*
          x_axis:
            field: host.name
            type: values
          value:
            aggregation: count
""".strip()
            + '\n',
            encoding='utf-8',
        )

        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 0
        assert 'Upgraded' in result.output

        upgraded = _read_yaml(input_file)
        dashboards = cast('list[dict[str, Any]]', upgraded['dashboards'])
        panels = cast('list[dict[str, Any]]', dashboards[0]['panels'])
        chart = cast('dict[str, Any]', panels[0]['lens'])

        assert 'value' not in chart
        assert chart['metric'] == {'aggregation': 'count'}

    def test_upgrade_wraps_write_errors_in_click_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Write failures should be surfaced as friendly click errors."""
        input_file = tmp_path / 'legacy.yaml'
        input_file.write_text(
            """
dashboards:
  - id: demo
    name: Demo
    panels:
      - lens:
          type: pie
          data_view: logs-*
          dimensions:
            - type: values
              field: service.name
          metrics:
            - aggregation: count
""".strip()
            + '\n',
            encoding='utf-8',
        )

        def _raise_write_error(_document: object, _path: str) -> None:
            msg = 'disk full'
            raise OSError(msg)

        monkeypatch.setattr('dashboard_compiler.cli_upgrade.dump_roundtrip', _raise_write_error)
        result = CliRunner().invoke(cli, ['upgrade', '--input-file', str(input_file), '--write'])
        assert result.exit_code == 1
        assert 'Error upgrading' in result.output
