"""Test the compilation of Lens datatable charts from config models to view models using inline snapshots."""

from typing import Any

from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.datatable.compile import (
    compile_esql_datatable_chart,
    compile_lens_datatable_chart,
)
from dashboard_compiler.panels.charts.datatable.config import ESQLDatatableChart, LensDatatableChart


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
        'rows': [
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
        'rows': [
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
        'rows': [
            {
                'type': 'values',
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'rows_by': [
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
        'rows': [
            {
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'rows_by': [
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
        'rows': [
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
