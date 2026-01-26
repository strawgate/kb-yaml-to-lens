"""Test the compilation of Lens datatable charts from config models to view models using inline snapshots."""

from typing import TYPE_CHECKING, Any

import pytest
from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot
from pydantic import ValidationError

from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.dashboard_compiler import render
from kb_dashboard_core.panels.charts.datatable.compile import (
    compile_esql_datatable_chart,
    compile_lens_datatable_chart,
)
from kb_dashboard_core.panels.charts.datatable.config import ESQLDatatableChart, LensDatatableChart

if TYPE_CHECKING:
    from kb_dashboard_core.dashboard.view import KbnDashboard


def compile_datatable_chart_snapshot(config: dict[str, Any], chart_type: str = 'lens') -> dict[str, Any]:
    """Compile datatable chart config and return dict for snapshot testing."""
    if chart_type == 'lens':
        lens_chart = LensDatatableChart.model_validate(config)
        _layer_id, _kbn_columns_by_id, kbn_state_visualization = compile_lens_datatable_chart(lens_datatable_chart=lens_chart)
    else:  # esql
        esql_chart = ESQLDatatableChart.model_validate(config)
        _layer_id, _kbn_columns, kbn_state_visualization = compile_esql_datatable_chart(esql_datatable_chart=esql_chart)

    assert kbn_state_visualization is not None
    return kbn_state_visualization.model_dump()


def test_compile_datatable_chart_basic_lens() -> None:
    """Test the compilation of a basic datatable chart with metrics only (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [{'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True}],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_rows_lens() -> None:
    """Test the compilation of a datatable chart with metrics and rows (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
        'dimensions': [
            {
                'type': 'values',
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [
                {'columnId': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172', 'isTransposed': False, 'isMetric': False},
                {'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True},
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_metric_column_config_lens() -> None:
    """Test the compilation of a datatable chart with custom metric column configurations (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
        'metric_columns': [
            {
                'column_id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'width': 200,
                'alignment': 'right',
                'summary_row': 'sum',
                'summary_label': 'Total',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [
                {
                    'alignment': 'right',
                    'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                    'isTransposed': False,
                    'isMetric': True,
                    'summaryLabel': 'Total',
                    'summaryRow': 'sum',
                    'width': 200,
                }
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_sorting_and_paging_lens() -> None:
    """Test the compilation of a datatable chart with sorting and pagination (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
        'sorting': {'column_id': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'direction': 'desc'},
        'paging': {'enabled': True, 'page_size': 25},
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [{'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True}],
            'layerId': IsUUID,
            'layerType': 'data',
            'paging': {'enabled': True, 'size': 25},
            'sorting': {'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'direction': 'desc'},
        }
    )


def test_compile_datatable_chart_with_appearance_lens() -> None:
    """Test the compilation of a datatable chart with appearance settings (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
        'appearance': {
            'row_height': 'custom',
            'row_height_lines': 3,
            'density': 'compact',
        },
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [{'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True}],
            'density': 'compact',
            'layerId': IsUUID,
            'layerType': 'data',
            'rowHeight': 'custom',
            'rowHeightLines': 3,
        }
    )


def test_compile_datatable_chart_basic_esql() -> None:
    """Test the compilation of a basic datatable chart with metrics only (ESQL)."""
    config = {
        'type': 'datatable',
        'metrics': [
            {
                'field': 'count(aerospike.namespace)',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [{'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True}],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_rows_esql() -> None:
    """Test the compilation of a datatable chart with metrics and rows (ESQL)."""
    config = {
        'type': 'datatable',
        'metrics': [
            {
                'field': 'count(aerospike.namespace)',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            }
        ],
        'dimensions': [
            {
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'esql')

    # Verify the result matches the expected snapshot
    assert result == snapshot(
        {
            'columns': [
                {'columnId': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172', 'isTransposed': False, 'isMetric': False},
                {'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True},
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_rows_by_lens() -> None:
    """Test the compilation of a datatable chart with rows_by (split metrics by) (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
        'dimensions': [
            {
                'type': 'values',
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'dimensions_by': [
            {
                'type': 'values',
                'field': 'host.name',
                'id': 'split-by-host',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'columns': [
                {'columnId': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172', 'isTransposed': False, 'isMetric': False},
                {'columnId': 'split-by-host', 'isTransposed': False, 'isMetric': False},
                {'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True},
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_rows_by_esql() -> None:
    """Test the compilation of a datatable chart with rows_by (split metrics by) (ESQL)."""
    config = {
        'type': 'datatable',
        'metrics': [
            {
                'field': 'count(aerospike.namespace)',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
            }
        ],
        'dimensions': [
            {
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'dimensions_by': [
            {
                'field': 'host.name',
                'id': 'split-by-host',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'columns': [
                {'columnId': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172', 'isTransposed': False, 'isMetric': False},
                {'columnId': 'split-by-host', 'isTransposed': False, 'isMetric': False},
                {'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True},
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_row_column_config_lens() -> None:
    """Test the compilation of a datatable chart with row column configurations (Lens)."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': '156e3e91-7bb6-406f-8ae5-cb409747953b',
                'aggregation': 'count',
            }
        ],
        'dimensions': [
            {
                'type': 'values',
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'columns': [
            {
                'column_id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
                'width': 150,
                'alignment': 'left',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    assert result == snapshot(
        {
            'columns': [
                {
                    'alignment': 'left',
                    'columnId': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
                    'isTransposed': False,
                    'isMetric': False,
                    'width': 150,
                },
                {'columnId': '156e3e91-7bb6-406f-8ae5-cb409747953b', 'isTransposed': False, 'isMetric': True},
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_formula_metrics_lens() -> None:
    """Test that datatable with formula metrics uses alphabetical ordering for rows.

    Formula columns are computed post-aggregation and cannot be used for
    Elasticsearch aggregation ordering. When a datatable has only formula
    metrics, the row dimension should use alphabetical ordering instead of
    trying to order by the formula column.
    """
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'formula': '1 - average(system.cpu.idle.pct)',
                'label': 'CPU %',
                'id': 'cpu-util',
            },
            {
                'formula': 'average(system.memory.used.pct)',
                'label': 'Memory %',
                'id': 'mem-util',
            },
        ],
        'dimensions': [
            {
                'type': 'values',
                'field': 'host.name',
                'id': 'hostname',
                'size': 100,
            }
        ],
    }

    lens_chart = LensDatatableChart.model_validate(config)
    _layer_id, kbn_columns_by_id, _kbn_state_visualization = compile_lens_datatable_chart(lens_datatable_chart=lens_chart)

    # Get the row dimension column
    hostname_column = kbn_columns_by_id['hostname']
    hostname_dict = hostname_column.model_dump()

    # Verify that the row dimension uses alphabetical ordering (not ordering by formula)
    assert hostname_dict['params']['orderBy'] == {'type': 'alphabetical', 'fallback': True}
    assert hostname_dict['params']['orderDirection'] == 'desc'


def test_lens_datatable_validation_requires_metrics_or_rows() -> None:
    """Test that Lens datatable validation fails when both metrics and rows are empty."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [],
        'dimensions': [],
    }

    with pytest.raises(ValidationError, match='at least one metric or one dimension'):
        LensDatatableChart.model_validate(config)


def test_lens_datatable_validation_with_only_metrics_succeeds() -> None:
    """Test that Lens datatable with only metrics passes validation."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [{'field': 'test', 'id': 'test-id', 'aggregation': 'count'}],
        'dimensions': [],
    }

    chart = LensDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 1
    assert len(chart.dimensions) == 0


def test_lens_datatable_validation_with_only_dimensions_succeeds() -> None:
    """Test that Lens datatable with only dimensions passes validation."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [],
        'dimensions': [{'field': 'test', 'id': 'test-id', 'type': 'values'}],
    }

    chart = LensDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 0
    assert len(chart.dimensions) == 1


def test_esql_datatable_allows_empty_metrics_and_dimensions() -> None:
    """Test that ESQL datatable allows empty metrics and dimensions (columns inferred from query)."""
    config = {
        'type': 'datatable',
        'metrics': [],
        'dimensions': [],
    }

    chart = ESQLDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 0
    assert len(chart.dimensions) == 0


def test_esql_datatable_validation_with_only_metrics_succeeds() -> None:
    """Test that ESQL datatable with only metrics passes validation."""
    config = {
        'type': 'datatable',
        'metrics': [{'field': 'count(*)', 'id': 'test-id'}],
        'dimensions': [],
    }

    chart = ESQLDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 1
    assert len(chart.dimensions) == 0


def test_esql_datatable_validation_with_only_dimensions_succeeds() -> None:
    """Test that ESQL datatable with only dimensions passes validation."""
    config = {
        'type': 'datatable',
        'metrics': [],
        'dimensions': [{'field': 'test', 'id': 'test-id'}],
    }

    chart = ESQLDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 0
    assert len(chart.dimensions) == 1


def test_datatable_chart_dashboard_references_bubble_up() -> None:
    """Test that datatable chart data view references bubble up to dashboard level correctly.

    Datatable charts reference a data view (index-pattern), so this reference should appear
    at the dashboard's top-level references array with proper panel namespacing.
    """
    dashboard = Dashboard(
        name='Test Datatable Chart Dashboard',
        panels=[
            {
                'title': 'Datatable',
                'id': 'datatable-panel-1',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'lens': {
                    'type': 'datatable',
                    'data_view': 'logs-*',
                    'metrics': [{'aggregation': 'count', 'id': 'count-metric'}],
                    'dimensions': [{'type': 'values', 'field': 'host.name', 'id': 'host-dim'}],
                },
            }
        ],
    )

    kbn_dashboard: KbnDashboard = render(dashboard=dashboard)
    references = [ref.model_dump() for ref in kbn_dashboard.references]

    assert references == snapshot(
        [
            {
                'id': 'logs-*',
                'name': IsStr(regex=r'datatable-panel-1:indexpattern-datasource-layer-[a-f0-9-]+'),
                'type': 'index-pattern',
            }
        ]
    )
