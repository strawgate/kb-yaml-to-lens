"""Integration tests for uploading compiled dashboards to Kibana.

These tests verify that:
1. Dashboards compile correctly from YAML
2. Dashboards upload successfully to Kibana
3. Panels render without errors
4. Sample data displays correctly
"""

import json
from pathlib import Path
from typing import Any

import pytest
from elasticsearch import AsyncElasticsearch

from dashboard_compiler.dashboard_compiler import load, render
from dashboard_compiler.kibana_client import KibanaClient

from .conftest import get_dashboard_panel_errors


@pytest.fixture
def simple_dashboard_yaml() -> str:
    """Return a simple dashboard YAML for testing."""
    return """---
dashboards:
  - name: '[Integration Test] Simple Dashboard'
    description: Integration test dashboard with basic panels
    panels:
      - title: Document Count
        grid: {x: 0, y: 0, w: 24, h: 10}
        lens:
          type: metric
          data_view: logs-sample*
          primary:
            aggregation: count
      - title: Log Levels Distribution
        grid: {x: 24, y: 0, w: 24, h: 10}
        lens:
          type: pie
          data_view: logs-sample*
          dimensions:
            - field: log.level
              type: values
              size: 10
          metrics:
            - aggregation: count
      - title: Events Over Time
        grid: {x: 0, y: 10, w: 48, h: 15}
        lens:
          type: line
          data_view: logs-sample*
          dimension:
            type: date_histogram
            field: '@timestamp'
          metrics:
            - aggregation: count
"""


@pytest.fixture
def esql_dashboard_yaml() -> str:
    """Return an ES|QL dashboard YAML for testing."""
    return """---
dashboards:
  - name: '[Integration Test] ES|QL Dashboard'
    description: Integration test dashboard with ES|QL panels
    panels:
      - title: ES|QL Metric
        grid: {x: 0, y: 0, w: 24, h: 10}
        esql:
          type: metric
          query: "FROM logs-sample | STATS count()"
          metrics:
            - field: count()
      - title: ES|QL Line Chart
        grid: {x: 24, y: 0, w: 24, h: 15}
        esql:
          type: line
          query: "FROM logs-sample | STATS count() BY @timestamp"
          dimension:
            field: "@timestamp"
          metrics:
            - field: count()
"""


@pytest.fixture
def multi_panel_dashboard_yaml() -> str:
    """Return a multi-panel dashboard YAML for comprehensive testing."""
    return """---
dashboards:
  - name: '[Integration Test] Multi-Panel Dashboard'
    description: Comprehensive integration test with all panel types
    panels:
      - title: Welcome
        grid: {x: 0, y: 0, w: 48, h: 4}
        markdown:
          content: "# Integration Test Dashboard\\nThis dashboard tests all panel types."
      - title: Quick Links
        grid: {x: 0, y: 4, w: 48, h: 3}
        links:
          layout: horizontal
          items:
            - label: Elastic
              url: https://www.elastic.co
      - title: Metric Panel
        grid: {x: 0, y: 7, w: 12, h: 8}
        lens:
          type: metric
          data_view: logs-sample*
          primary:
            aggregation: count
      - title: Pie Chart
        grid: {x: 12, y: 7, w: 12, h: 8}
        lens:
          type: pie
          data_view: logs-sample*
          dimensions:
            - field: log.level
              type: values
          metrics:
            - aggregation: count
      - title: Bar Chart
        grid: {x: 24, y: 7, w: 24, h: 8}
        lens:
          type: bar
          data_view: logs-sample*
          dimension:
            type: values
            field: host.name
          metrics:
            - aggregation: count
      - title: Line Chart
        grid: {x: 0, y: 15, w: 24, h: 10}
        lens:
          type: line
          data_view: logs-sample*
          dimension:
            type: date_histogram
            field: '@timestamp'
          metrics:
            - aggregation: count
      - title: Area Chart
        grid: {x: 24, y: 15, w: 24, h: 10}
        lens:
          type: area
          mode: stacked
          data_view: logs-sample*
          dimension:
            type: date_histogram
            field: '@timestamp'
          metrics:
            - aggregation: count
          breakdown:
            type: values
            field: log.level
      - title: Tag Cloud
        grid: {x: 0, y: 25, w: 24, h: 10}
        lens:
          type: tagcloud
          data_view: logs-sample*
          dimension:
            type: values
            field: tags
          metric:
            aggregation: count
      - title: Data Table
        grid: {x: 24, y: 25, w: 24, h: 10}
        lens:
          type: datatable
          data_view: logs-sample*
          dimensions:
            - field: host.name
              type: values
          metrics:
            - aggregation: count
"""


class TestDashboardUpload:
    """Test suite for dashboard upload and panel error detection."""

    @pytest.mark.asyncio
    async def test_simple_dashboard_upload(
        self,
        kibana_client: KibanaClient,
        loaded_sample_data: str,  # noqa: ARG002 - fixture dependency
        data_view: str,  # noqa: ARG002 - fixture dependency
        simple_dashboard_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Test uploading a simple dashboard with basic Lens panels."""
        # Write YAML to temp file
        yaml_file = tmp_path / 'simple_dashboard.yaml'
        yaml_file.write_text(simple_dashboard_yaml)

        # Load and compile
        dashboards = load(str(yaml_file))
        assert len(dashboards) == 1

        # Render to Kibana format
        kbn_dashboard = render(dashboards[0])
        ndjson = kbn_dashboard.model_dump_json(by_alias=True)

        # Upload to Kibana
        result = await kibana_client.upload_ndjson(ndjson, overwrite=True)

        # Verify upload succeeded
        assert result.success, f'Upload failed: {result.errors}'
        assert result.success_count > 0

        # Get dashboard ID from result
        dashboard_result = next((r for r in result.success_results if r.type == 'dashboard'), None)
        assert dashboard_result is not None, 'Dashboard not found in upload results'

        dashboard_id = dashboard_result.destination_id or dashboard_result.id

        # Check for panel errors
        errors = await get_dashboard_panel_errors(kibana_client, dashboard_id)
        assert len(errors) == 0, f'Panel errors detected: {errors}'

    @pytest.mark.asyncio
    async def test_esql_dashboard_upload(
        self,
        kibana_client: KibanaClient,
        loaded_sample_data: str,  # noqa: ARG002 - fixture dependency
        esql_dashboard_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Test uploading a dashboard with ES|QL panels."""
        yaml_file = tmp_path / 'esql_dashboard.yaml'
        yaml_file.write_text(esql_dashboard_yaml)

        # Load and compile
        dashboards = load(str(yaml_file))
        assert len(dashboards) == 1

        # Render to Kibana format
        kbn_dashboard = render(dashboards[0])
        ndjson = kbn_dashboard.model_dump_json(by_alias=True)

        # Upload to Kibana
        result = await kibana_client.upload_ndjson(ndjson, overwrite=True)

        assert result.success, f'Upload failed: {result.errors}'

        # Get dashboard ID
        dashboard_result = next((r for r in result.success_results if r.type == 'dashboard'), None)
        assert dashboard_result is not None

        dashboard_id = dashboard_result.destination_id or dashboard_result.id

        # Check for panel errors
        errors = await get_dashboard_panel_errors(kibana_client, dashboard_id)
        assert len(errors) == 0, f'Panel errors detected: {errors}'

    @pytest.mark.asyncio
    async def test_multi_panel_dashboard_upload(
        self,
        kibana_client: KibanaClient,
        loaded_sample_data: str,  # noqa: ARG002 - fixture dependency
        data_view: str,  # noqa: ARG002 - fixture dependency
        multi_panel_dashboard_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Test uploading a comprehensive multi-panel dashboard."""
        yaml_file = tmp_path / 'multi_panel_dashboard.yaml'
        yaml_file.write_text(multi_panel_dashboard_yaml)

        # Load and compile
        dashboards = load(str(yaml_file))
        assert len(dashboards) == 1

        # Render to Kibana format
        kbn_dashboard = render(dashboards[0])
        ndjson = kbn_dashboard.model_dump_json(by_alias=True)

        # Upload to Kibana
        result = await kibana_client.upload_ndjson(ndjson, overwrite=True)

        assert result.success, f'Upload failed: {result.errors}'

        # Get dashboard ID
        dashboard_result = next((r for r in result.success_results if r.type == 'dashboard'), None)
        assert dashboard_result is not None

        dashboard_id = dashboard_result.destination_id or dashboard_result.id

        # Check for panel errors
        errors = await get_dashboard_panel_errors(kibana_client, dashboard_id)
        assert len(errors) == 0, f'Panel errors detected: {errors}'

    @pytest.mark.asyncio
    async def test_upload_and_export_roundtrip(
        self,
        kibana_client: KibanaClient,
        loaded_sample_data: str,  # noqa: ARG002 - fixture dependency
        data_view: str,  # noqa: ARG002 - fixture dependency
        simple_dashboard_yaml: str,
        tmp_path: Path,
    ) -> None:
        """Test that uploaded dashboard can be exported back."""
        yaml_file = tmp_path / 'roundtrip_dashboard.yaml'
        yaml_file.write_text(simple_dashboard_yaml)

        # Load and compile
        dashboards = load(str(yaml_file))
        kbn_dashboard = render(dashboards[0])
        ndjson = kbn_dashboard.model_dump_json(by_alias=True)

        # Upload
        result = await kibana_client.upload_ndjson(ndjson, overwrite=True)
        assert result.success

        # Get dashboard ID
        dashboard_result = next((r for r in result.success_results if r.type == 'dashboard'), None)
        assert dashboard_result is not None

        dashboard_id = dashboard_result.destination_id or dashboard_result.id

        # Export back
        exported_ndjson = await kibana_client.export_dashboard(dashboard_id)

        # Verify we got valid NDJSON back
        lines = [line for line in exported_ndjson.strip().split('\n') if line]
        assert len(lines) > 0, 'Export returned empty NDJSON'

        # Parse and verify structure
        for line in lines:
            obj = json.loads(line)
            assert 'type' in obj or 'exportedCount' in obj, f'Invalid object in export: {obj}'


class TestSampleDataIntegration:
    """Tests for sample data loading and visualization."""

    @pytest.mark.asyncio
    async def test_sample_data_indexed(
        self,
        es_client: AsyncElasticsearch,
        loaded_sample_data: str,
    ) -> None:
        """Verify sample data is correctly indexed."""
        # Check document count
        count_response = await es_client.count(index=loaded_sample_data)
        assert count_response['count'] == 100

        # Verify document structure
        search_response = await es_client.search(
            index=loaded_sample_data,
            body={'query': {'match_all': {}}, 'size': 1},
        )
        hits = search_response['hits']['hits']
        assert len(hits) == 1

        doc = hits[0]['_source']
        assert '@timestamp' in doc
        assert 'log' in doc
        assert 'host' in doc
        assert 'tags' in doc

    @pytest.mark.asyncio
    async def test_data_view_created(
        self,
        kibana_client: KibanaClient,
        data_view: str,
    ) -> None:
        """Verify data view is correctly created."""
        async with await kibana_client._get(f'/api/data_views/data_view/{data_view}') as response:
            assert response.status == 200
            data = await response.json()
            assert data['data_view']['id'] == data_view


class TestExampleDashboards:
    """Test actual example dashboards from the docs folder."""

    @pytest.mark.asyncio
    async def test_docs_examples_compile_and_upload(
        self,
        kibana_client: KibanaClient,
        loaded_sample_data: str,  # noqa: ARG002 - fixture dependency
        data_view: str,  # noqa: ARG002 - fixture dependency
    ) -> None:
        """Test that docs example dashboards compile and upload without errors."""
        examples_dir = Path(__file__).parent.parent.parent.parent / 'docs' / 'examples'

        if not examples_dir.exists():
            pytest.skip(f'Examples directory not found: {examples_dir}')

        # Find all YAML files
        yaml_files = list(examples_dir.glob('*.yaml'))

        # Skip if no examples found
        if not yaml_files:
            pytest.skip('No example YAML files found')

        errors: list[dict[str, Any]] = []

        for yaml_file in yaml_files:
            try:
                # Load and compile
                dashboards = load(str(yaml_file))

                for dashboard in dashboards:
                    kbn_dashboard = render(dashboard)
                    ndjson = kbn_dashboard.model_dump_json(by_alias=True)

                    # Upload to Kibana
                    result = await kibana_client.upload_ndjson(ndjson, overwrite=True)

                    if not result.success:
                        errors.append(
                            {
                                'file': yaml_file.name,
                                'dashboard': dashboard.name,
                                'type': 'upload_error',
                                'errors': [e.model_dump() for e in result.errors],
                            }
                        )
                        continue

                    # Get dashboard ID and check for panel errors
                    dashboard_result = next((r for r in result.success_results if r.type == 'dashboard'), None)
                    if dashboard_result:
                        dashboard_id = dashboard_result.destination_id or dashboard_result.id
                        panel_errors = await get_dashboard_panel_errors(kibana_client, dashboard_id)
                        if panel_errors:
                            errors.append(
                                {
                                    'file': yaml_file.name,
                                    'dashboard': dashboard.name,
                                    'type': 'panel_errors',
                                    'errors': panel_errors,
                                }
                            )

            except Exception as e:
                errors.append(
                    {
                        'file': yaml_file.name,
                        'type': 'compile_error',
                        'error': str(e),
                    }
                )

        if errors:
            # Format errors for readable output
            error_msg = json.dumps(errors, indent=2, default=str)
            pytest.fail(f'Dashboard compilation/upload errors:\n{error_msg}')
