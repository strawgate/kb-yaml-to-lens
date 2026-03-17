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
        'breakdowns': [
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
                'appearance': {
                    'width': 200,
                    'alignment': 'right',
                    'summary_row': 'sum',
                    'summary_label': 'Total',
                },
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


def test_compile_datatable_chart_with_one_click_filter_enabled() -> None:
    """Test one_click_filter compiles to oneClickFilter when set to true."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': 'metric-col-id',
                'aggregation': 'count',
                'appearance': {'one_click_filter': True},
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')
    assert result['columns'][0]['oneClickFilter'] is True


def test_compile_datatable_chart_with_one_click_filter_default_omitted() -> None:
    """Test one_click_filter is omitted when not explicitly enabled."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'aerospike.namespace.name',
                'id': 'metric-col-id',
                'aggregation': 'count',
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')
    assert 'oneClickFilter' not in result['columns'][0]


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
        'breakdowns': [
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
        'breakdowns': [
            {
                'type': 'values',
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'metrics_split_by': [
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
                {'columnId': 'split-by-host', 'isTransposed': True, 'isMetric': False},
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
        'breakdowns': [
            {
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
            }
        ],
        'metrics_split_by': [
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
                {'columnId': 'split-by-host', 'isTransposed': True, 'isMetric': False},
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
        'breakdowns': [
            {
                'type': 'values',
                'field': 'agent.name',
                'id': '17fe5b4b-d36c-4fbd-ace9-58d143bb3172',
                'appearance': {
                    'width': 150,
                    'alignment': 'left',
                },
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
        'breakdowns': [
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
        'breakdowns': [],
    }

    with pytest.raises(ValidationError, match='at least one metric or one breakdown'):
        LensDatatableChart.model_validate(config)


def test_lens_datatable_validation_with_only_metrics_succeeds() -> None:
    """Test that Lens datatable with only metrics passes validation."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [{'field': 'test', 'id': 'test-id', 'aggregation': 'count'}],
        'breakdowns': [],
    }

    chart = LensDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 1
    assert len(chart.breakdowns) == 0


def test_lens_datatable_validation_with_only_breakdowns_succeeds() -> None:
    """Test that Lens datatable with only breakdowns passes validation."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [],
        'breakdowns': [{'field': 'test', 'id': 'test-id', 'type': 'values'}],
    }

    chart = LensDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 0
    assert len(chart.breakdowns) == 1


def test_esql_datatable_validation_requires_metrics_or_rows() -> None:
    """Test that ESQL datatable validation fails when both metrics and rows are empty."""
    config = {
        'type': 'datatable',
        'metrics': [],
        'breakdowns': [],
    }

    with pytest.raises(ValidationError, match='at least one metric or one breakdown'):
        ESQLDatatableChart.model_validate(config)


def test_esql_datatable_validation_with_only_metrics_succeeds() -> None:
    """Test that ESQL datatable with only metrics passes validation."""
    config = {
        'type': 'datatable',
        'metrics': [{'field': 'count(*)', 'id': 'test-id'}],
        'breakdowns': [],
    }

    chart = ESQLDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 1
    assert len(chart.breakdowns) == 0


def test_esql_datatable_validation_with_only_breakdowns_succeeds() -> None:
    """Test that ESQL datatable with only breakdowns passes validation."""
    config = {
        'type': 'datatable',
        'metrics': [],
        'breakdowns': [{'field': 'test', 'id': 'test-id'}],
    }

    chart = ESQLDatatableChart.model_validate(config)
    assert chart is not None
    assert len(chart.metrics) == 0
    assert len(chart.breakdowns) == 1


def test_compile_datatable_chart_with_range_colors_esql() -> None:
    """Test ESQL range colors preserve thresholds in both stops arrays."""
    config = {
        'type': 'datatable',
        'metrics': [
            {
                'field': 'avg(cpu_usage)',
                'id': 'cpu-metric',
                'color': {
                    'apply_to': 'cell',
                    'range_type': 'percent',
                    'range_min': 0,
                    'range_max': 100,
                    'thresholds': [
                        {'up_to': 50, 'color': '#00BF6F'},
                        {'up_to': 80, 'color': '#FFA500'},
                        {'up_to': 100, 'color': '#BD271E'},
                    ],
                },
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'esql')

    assert result == snapshot(
        {
            'columns': [
                {
                    'colorMode': 'cell',
                    'columnId': 'cpu-metric',
                    'isMetric': True,
                    'isTransposed': False,
                    'palette': {
                        'name': 'custom',
                        'params': {
                            'colorStops': [
                                {'color': '#00BF6F', 'stop': 0},
                                {'color': '#FFA500', 'stop': 50},
                                {'color': '#BD271E', 'stop': 80},
                            ],
                            'continuity': 'above',
                            'maxSteps': 3,
                            'name': 'custom',
                            'progression': 'fixed',
                            'rangeMax': 100,
                            'rangeMin': 0,
                            'rangeType': 'percent',
                            'reverse': False,
                            'steps': 3,
                            'stops': [
                                {'color': '#00BF6F', 'stop': 50},
                                {'color': '#FFA500', 'stop': 80},
                                {'color': '#BD271E', 'stop': 100.0},
                            ],
                        },
                        'type': 'palette',
                    },
                }
            ],
            'layerId': IsUUID,
            'layerType': 'data',
        }
    )


def test_compile_datatable_chart_with_range_colors_lens() -> None:
    """Test Lens datatable metric column with range color thresholds compiles correctly."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'system.cpu.total.pct',
                'id': 'cpu-metric',
                'aggregation': 'average',
                'color': {
                    'apply_to': 'text',
                    'range_type': 'number',
                    'range_min': 0,
                    'thresholds': [
                        {'up_to': 0.5, 'color': '#00BF6F'},
                        {'up_to': 0.8, 'color': '#FFA500'},
                        {'up_to': 1.0, 'color': '#BD271E'},
                    ],
                },
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    column = result['columns'][0]
    assert column == snapshot(
        {
            'columnId': 'cpu-metric',
            'isMetric': True,
            'isTransposed': False,
            'colorMode': 'text',
            'palette': {
                'type': 'palette',
                'name': 'custom',
                'params': {
                    'colorStops': [
                        {'stop': 0.0, 'color': '#00BF6F'},
                        {'stop': 0.5, 'color': '#FFA500'},
                        {'stop': 0.8, 'color': '#BD271E'},
                    ],
                    'name': 'custom',
                    'rangeType': 'number',
                    'rangeMin': 0.0,
                    'rangeMax': None,
                    'continuity': 'above',
                    'steps': 3,
                    'maxSteps': 3,
                    'progression': 'fixed',
                    'reverse': False,
                    'stops': [
                        {'stop': 0.5, 'color': '#00BF6F'},
                        {'stop': 0.8, 'color': '#FFA500'},
                        {'stop': 1.0, 'color': '#BD271E'},
                    ],
                },
            },
        }
    )


def test_lens_datatable_deprecated_keys_do_not_override_explicit_new_fields() -> None:
    """Legacy dimensions/dimensions_by keys are rejected in 0.4.0."""
    with pytest.raises(ValidationError, match='dimensions'):
        LensDatatableChart.model_validate(
            {
                'type': 'datatable',
                'data_view': 'logs-*',
                'breakdowns': [{'type': 'values', 'field': 'service.name', 'id': 'new-breakdown'}],
                'dimensions': [{'type': 'values', 'field': 'host.name', 'id': 'legacy-dimension'}],
                'metrics_split_by': [{'type': 'values', 'field': 'cloud.region', 'id': 'new-split-by'}],
                'dimensions_by': [{'type': 'values', 'field': 'host.os.name', 'id': 'legacy-split-by'}],
            }
        )


def test_esql_datatable_deprecated_keys_do_not_override_explicit_new_fields() -> None:
    """Legacy dimensions/dimensions_by keys are rejected for ES|QL datatables too."""
    with pytest.raises(ValidationError, match='dimensions'):
        ESQLDatatableChart.model_validate(
            {
                'type': 'datatable',
                'breakdowns': [{'field': 'service.name', 'id': 'new-breakdown'}],
                'dimensions': [{'field': 'host.name', 'id': 'legacy-dimension'}],
                'metrics_split_by': [{'field': 'cloud.region', 'id': 'new-split-by'}],
                'dimensions_by': [{'field': 'host.os.name', 'id': 'legacy-split-by'}],
            }
        )


@pytest.mark.parametrize(
    ('range_type', 'threshold_stops', 'expected_color_stops'),
    [
        ('number', [25.0, 50.0], [0.0, 25.0]),
        ('percent', [25.0, 100.0], [0.0, 25.0]),
    ],
)
def test_compile_datatable_chart_preserves_thresholds_in_color_stops(
    range_type: str, threshold_stops: list[float], expected_color_stops: list[float]
) -> None:
    """Test datatable colorStops encode lower bounds for each threshold band."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'system.cpu.total.pct',
                'id': 'cpu-metric',
                'aggregation': 'average',
                'color': {
                    'apply_to': 'text',
                    'range_type': range_type,
                    'thresholds': [
                        {'up_to': threshold_stops[0], 'color': '#000000'},
                        {'up_to': threshold_stops[1], 'color': '#ffffff'},
                    ],
                },
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')
    color_stops = result['columns'][0]['palette']['params']['colorStops']
    assert [entry['stop'] for entry in color_stops] == expected_color_stops
    assert [entry['stop'] for entry in result['columns'][0]['palette']['params']['stops']] == threshold_stops


def test_compile_datatable_chart_without_color_omits_palette() -> None:
    """Test that palette is omitted when no color config is provided."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'system.cpu.total.pct',
                'id': 'cpu-metric',
                'aggregation': 'average',
                'color': {'apply_to': 'cell'},
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')

    # Verify palette is not in the output when color is not configured
    column = result['columns'][0]
    assert column['colorMode'] == 'cell'
    assert 'palette' not in column


def test_datatable_metric_color_thresholds_empty_list_is_invalid() -> None:
    """Test that empty range color thresholds are rejected."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'id': 'cpu-metric',
                'field': 'system.cpu.total.pct',
                'aggregation': 'average',
                'color': {
                    'apply_to': 'text',
                    'thresholds': [],
                },
            }
        ],
    }

    with pytest.raises(ValidationError, match='at least 1 item'):
        LensDatatableChart.model_validate(config)


@pytest.mark.parametrize(
    'legacy_color_config',
    [
        {
            'apply_to': 'text',
            'stops': [
                {'stop': 50, 'color': '#00BF6F'},
            ],
        },
        {
            'apply_to': 'text',
            'thresholds': [
                {'stop': 50, 'color': '#00BF6F'},
            ],
        },
    ],
)
def test_datatable_metric_color_legacy_stops_keys_are_invalid(legacy_color_config: dict[str, object]) -> None:
    """Test that legacy stops/stop keys are rejected."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'id': 'cpu-metric',
                'field': 'system.cpu.total.pct',
                'aggregation': 'average',
                'color': legacy_color_config,
            }
        ],
    }

    with pytest.raises(ValidationError, match='Extra inputs are not permitted'):
        LensDatatableChart.model_validate(config)


def test_compile_datatable_chart_percent_thresholds_append_terminal_100() -> None:
    """Test that percent color stops keep the user threshold and append a terminal 100 stop."""
    config = {
        'type': 'datatable',
        'data_view': 'metrics-*',
        'metrics': [
            {
                'field': 'system.cpu.total.pct',
                'id': 'cpu-metric',
                'aggregation': 'average',
                'color': {
                    'apply_to': 'text',
                    'range_type': 'percent',
                    'thresholds': [
                        {'up_to': 50, 'color': '#00BF6F'},
                        {'up_to': 80, 'color': '#ffffff'},
                    ],
                },
            }
        ],
    }

    result = compile_datatable_chart_snapshot(config, 'lens')
    color_stops = result['columns'][0]['palette']['params']['colorStops']
    assert [entry['stop'] for entry in color_stops] == [0, 50, 80]
    assert [entry['stop'] for entry in result['columns'][0]['palette']['params']['stops']] == [50, 80, 100]


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
                    'breakdowns': [{'type': 'values', 'field': 'host.name', 'id': 'host-dim'}],
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
