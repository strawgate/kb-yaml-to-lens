"""Tests for chart compilation utilities."""

from typing import Any

import pytest
from dirty_equals import IsStr, IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.compile import (
    chart_type_to_kbn_type_lens,
    compile_charts_panel_config,
    compile_esql_chart_state,
    compile_lens_chart_state,
)
from dashboard_compiler.panels.charts.datatable.config import ESQLDatatableChart, LensDatatableChart
from dashboard_compiler.panels.charts.gauge.config import ESQLGaugeChart, LensGaugeChart
from dashboard_compiler.panels.charts.heatmap.config import ESQLHeatmapChart, LensHeatmapChart
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.pie.config import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.charts.tagcloud.config import ESQLTagcloudChart, LensTagcloudChart
from dashboard_compiler.panels.charts.view import KbnVisualizationTypeEnum
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
)
from dashboard_compiler.panels.charts.xy.view import XYDataLayerConfig, XYReferenceLineLayerConfig


def _get_single_layer(state: Any) -> tuple[str, Any]:
    """Extract the single layer from a compiled chart state."""
    form_based = state.datasourceStates.formBased
    assert form_based is not None
    layers = form_based.layers.root
    assert len(layers) == 1
    layer_id, layer = next(iter(layers.items()))
    return layer_id, layer


class TestChartTypeToKbnTypeLens:
    """Tests for chart_type_to_kbn_type_lens function."""

    def test_identifies_lens_pie_chart(self) -> None:
        """Test that LensPieChart is identified correctly."""
        chart = LensPieChart.model_validate(
            {
                'type': 'pie',
                'data_view': 'metrics-*',
                'dimensions': [{'type': 'values', 'field': 'status', 'id': 'group1'}],
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.PIE

    def test_identifies_esql_pie_chart(self) -> None:
        """Test that ESQLPieChart is identified correctly."""
        chart = ESQLPieChart.model_validate(
            {
                'type': 'pie',
                'dimensions': [{'field': 'status', 'id': 'group1'}],
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.PIE

    def test_identifies_lens_line_chart(self) -> None:
        """Test that LensLineChart is identified as XY."""
        chart = LensLineChart.model_validate(
            {
                'type': 'line',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.XY

    def test_identifies_lens_bar_chart(self) -> None:
        """Test that LensBarChart is identified as XY."""
        chart = LensBarChart.model_validate(
            {
                'type': 'bar',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.XY

    def test_identifies_lens_area_chart(self) -> None:
        """Test that LensAreaChart is identified as XY."""
        chart = LensAreaChart.model_validate(
            {
                'type': 'area',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.XY

    def test_identifies_lens_reference_line_layer(self) -> None:
        """Test that LensReferenceLineLayer is identified as XY."""
        chart = LensReferenceLineLayer.model_validate(
            {
                'data_view': 'metrics-*',
                'reference_lines': [{'value': 100.0, 'id': 'ref1'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.XY

    def test_identifies_esql_xy_charts(self) -> None:
        """Test that ESQL XY charts are identified correctly."""
        area_chart = ESQLAreaChart.model_validate(
            {
                'type': 'area',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            }
        )
        assert chart_type_to_kbn_type_lens(area_chart) == KbnVisualizationTypeEnum.XY

        bar_chart = ESQLBarChart.model_validate(
            {
                'type': 'bar',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            }
        )
        assert chart_type_to_kbn_type_lens(bar_chart) == KbnVisualizationTypeEnum.XY

        line_chart = ESQLLineChart.model_validate(
            {
                'type': 'line',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            }
        )
        assert chart_type_to_kbn_type_lens(line_chart) == KbnVisualizationTypeEnum.XY

    def test_identifies_lens_metric_chart(self) -> None:
        """Test that LensMetricChart is identified correctly."""
        chart = LensMetricChart.model_validate(
            {
                'type': 'metric',
                'data_view': 'metrics-*',
                'primary': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.METRIC

    def test_identifies_esql_metric_chart(self) -> None:
        """Test that ESQLMetricChart is identified correctly."""
        chart = ESQLMetricChart.model_validate(
            {
                'type': 'metric',
                'primary': {'field': 'count(*)', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.METRIC

    def test_identifies_lens_datatable_chart(self) -> None:
        """Test that LensDatatableChart is identified correctly."""
        chart = LensDatatableChart.model_validate(
            {
                'type': 'datatable',
                'data_view': 'metrics-*',
                'metrics': [{'field': 'test', 'id': 'test-id', 'aggregation': 'count'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.DATATABLE

    def test_identifies_esql_datatable_chart(self) -> None:
        """Test that ESQLDatatableChart is identified correctly."""
        chart = ESQLDatatableChart.model_validate(
            {
                'type': 'datatable',
                'metrics': [{'field': 'count(*)', 'id': 'test-id'}],
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.DATATABLE

    def test_identifies_lens_gauge_chart(self) -> None:
        """Test that LensGaugeChart is identified correctly."""
        chart = LensGaugeChart.model_validate(
            {
                'type': 'gauge',
                'data_view': 'metrics-*',
                'metric': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.GAUGE

    def test_identifies_esql_gauge_chart(self) -> None:
        """Test that ESQLGaugeChart is identified correctly."""
        chart = ESQLGaugeChart.model_validate(
            {
                'type': 'gauge',
                'metric': {'field': 'count(*)', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.GAUGE

    def test_identifies_lens_heatmap_chart(self) -> None:
        """Test that LensHeatmapChart is identified correctly."""
        chart = LensHeatmapChart.model_validate(
            {
                'type': 'heatmap',
                'data_view': 'metrics-*',
                'x_axis': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'x1'},
                'value': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.HEATMAP

    def test_identifies_esql_heatmap_chart(self) -> None:
        """Test that ESQLHeatmapChart is identified correctly."""
        chart = ESQLHeatmapChart.model_validate(
            {
                'type': 'heatmap',
                'x_axis': {'field': '@timestamp', 'id': 'x1'},
                'value': {'field': 'count(*)', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.HEATMAP

    def test_identifies_lens_tagcloud_chart(self) -> None:
        """Test that LensTagcloudChart is identified correctly."""
        chart = LensTagcloudChart.model_validate(
            {
                'type': 'tagcloud',
                'data_view': 'metrics-*',
                'dimension': {'type': 'values', 'field': 'tag', 'id': 'tags1'},
                'metric': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.TAGCLOUD

    def test_identifies_esql_tagcloud_chart(self) -> None:
        """Test that ESQLTagcloudChart is identified correctly."""
        chart = ESQLTagcloudChart.model_validate(
            {
                'type': 'tagcloud',
                'dimension': {'field': 'tag', 'id': 'tags1'},
                'metric': {'field': 'count(*)', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.TAGCLOUD


class TestCompileLensChartState:
    """Tests for compile_lens_chart_state function."""

    def test_raises_error_when_no_charts_provided(self) -> None:
        """Test that compile_lens_chart_state raises ValueError when no charts are provided."""
        with pytest.raises(ValueError, match='At least one chart must be provided'):
            _ = compile_lens_chart_state(query=None, filters=None, charts=[])

    def test_compiles_metric_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a metric chart."""
        metric_chart = LensMetricChart.model_validate(
            {
                'type': 'metric',
                'data_view': 'metrics-*',
                'primary': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[metric_chart])
        _layer_id, layer = _get_single_layer(state)

        assert layer.model_dump() == snapshot(
            {
                'columnOrder': ['metric1'],
                'columns': {
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    }
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        assert state.visualization.model_dump() == snapshot(
            {
                'layerId': IsUUID,
                'layerType': 'data',
                'metricAccessor': 'metric1',
                'secondaryLabelPosition': 'before',
                'secondaryTrend': {'type': 'none'},
            }
        )

        assert len(references) == 1
        assert references[0].model_dump() == snapshot(
            {
                'id': 'metrics-*',
                'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'),
                'type': 'index-pattern',
            }
        )

    def test_compiles_datatable_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a datatable chart."""
        datatable_chart = LensDatatableChart.model_validate(
            {
                'type': 'datatable',
                'data_view': 'metrics-*',
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[datatable_chart])
        _layer_id, layer = _get_single_layer(state)

        assert layer.model_dump() == snapshot(
            {
                'columnOrder': ['metric1'],
                'columns': {
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    }
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        assert state.visualization.model_dump() == snapshot(
            {
                'columns': [
                    {
                        'columnId': 'metric1',
                        'isMetric': True,
                        'isTransposed': False,
                    }
                ],
                'layerId': IsUUID,
                'layerType': 'data',
            }
        )

        assert len(references) == 1
        assert references[0].model_dump() == snapshot(
            {'id': 'metrics-*', 'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'), 'type': 'index-pattern'}
        )

    def test_compiles_gauge_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a gauge chart."""
        gauge_chart = LensGaugeChart.model_validate(
            {
                'type': 'gauge',
                'data_view': 'metrics-*',
                'metric': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[gauge_chart])
        _layer_id, layer = _get_single_layer(state)

        assert layer.model_dump() == snapshot(
            {
                'columnOrder': ['metric1'],
                'columns': {
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    }
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        assert state.visualization.model_dump() == snapshot(
            {
                'labelMajorMode': 'auto',
                'layerId': IsUUID,
                'layerType': 'data',
                'metricAccessor': 'metric1',
                'shape': 'arc',
                'ticksPosition': 'auto',
            }
        )

        assert len(references) == 1
        assert references[0].model_dump() == snapshot(
            {'id': 'metrics-*', 'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'), 'type': 'index-pattern'}
        )

    def test_compiles_heatmap_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a heatmap chart."""
        heatmap_chart = LensHeatmapChart.model_validate(
            {
                'type': 'heatmap',
                'data_view': 'metrics-*',
                'x_axis': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'x1'},
                'value': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[heatmap_chart])
        _layer_id, layer = _get_single_layer(state)

        assert layer.model_dump() == snapshot(
            {
                'columnOrder': ['x1', 'metric1'],
                'columns': {
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    },
                    'x1': {
                        'dataType': 'date',
                        'isBucketed': True,
                        'label': '@timestamp',
                        'operationType': 'date_histogram',
                        'params': {'dropPartials': False, 'includeEmptyRows': True, 'interval': 'auto'},
                        'scale': 'interval',
                        'sourceField': '@timestamp',
                    },
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        assert state.visualization.model_dump() == snapshot(
            {
                'gridConfig': {
                    'isCellLabelVisible': False,
                    'isXAxisLabelVisible': False,
                    'isXAxisTitleVisible': False,
                    'isYAxisLabelVisible': False,
                    'isYAxisTitleVisible': False,
                    'type': 'heatmap_grid',
                },
                'layerId': IsUUID,
                'layerType': 'data',
                'legend': {'isVisible': True, 'position': 'right', 'type': 'heatmap_legend'},
                'shape': 'heatmap',
                'valueAccessor': 'metric1',
                'xAccessor': 'x1',
            }
        )

        assert len(references) == 1
        assert references[0].model_dump() == snapshot(
            {'id': 'metrics-*', 'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'), 'type': 'index-pattern'}
        )

    def test_compiles_tagcloud_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a tagcloud chart."""
        tagcloud_chart = LensTagcloudChart.model_validate(
            {
                'type': 'tagcloud',
                'data_view': 'metrics-*',
                'dimension': {'type': 'values', 'field': 'tag', 'id': 'tags1'},
                'metric': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[tagcloud_chart])
        _layer_id, layer = _get_single_layer(state)

        assert layer.model_dump() == snapshot(
            {
                'columnOrder': ['tags1', 'metric1'],
                'columns': {
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    },
                    'tags1': {
                        'dataType': 'string',
                        'isBucketed': True,
                        'label': 'Top 3 values of tag',
                        'operationType': 'terms',
                        'params': {
                            'size': 3,
                            'exclude': [],
                            'excludeIsRegex': False,
                            'include': [],
                            'includeIsRegex': False,
                            'missingBucket': False,
                            'orderBy': {'columnId': 'metric1', 'type': 'column'},
                            'orderDirection': 'desc',
                            'otherBucket': True,
                            'parentFormat': {'id': 'terms'},
                        },
                        'scale': 'ordinal',
                        'sourceField': 'tag',
                    },
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        assert state.visualization.model_dump() == snapshot(
            {
                'layerId': IsUUID,
                'maxFontSize': 72,
                'minFontSize': 12,
                'orientation': 'single',
                'showLabel': True,
                'tagAccessor': 'tags1',
                'valueAccessor': 'metric1',
            }
        )

        assert len(references) == 1
        assert references[0].model_dump() == snapshot(
            {'id': 'metrics-*', 'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'), 'type': 'index-pattern'}
        )

    def test_compiles_pie_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a pie chart."""
        pie_chart = LensPieChart.model_validate(
            {
                'type': 'pie',
                'data_view': 'metrics-*',
                'dimensions': [{'type': 'values', 'field': 'status', 'id': 'group1'}],
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[pie_chart])
        _layer_id, layer = _get_single_layer(state)

        assert layer.model_dump() == snapshot(
            {
                'columnOrder': ['group1', 'metric1'],
                'columns': {
                    'group1': {
                        'dataType': 'string',
                        'isBucketed': True,
                        'label': 'Top 3 values of status',
                        'operationType': 'terms',
                        'params': {
                            'size': 3,
                            'exclude': [],
                            'excludeIsRegex': False,
                            'include': [],
                            'includeIsRegex': False,
                            'missingBucket': False,
                            'orderBy': {'columnId': 'metric1', 'type': 'column'},
                            'orderDirection': 'desc',
                            'otherBucket': True,
                            'parentFormat': {'id': 'terms'},
                        },
                        'scale': 'ordinal',
                        'sourceField': 'status',
                    },
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    },
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        assert state.visualization.model_dump() == snapshot(
            {
                'layers': [
                    {
                        'categoryDisplay': 'default',
                        'colorMapping': {
                            'assignments': [],
                            'colorMode': {'type': 'categorical'},
                            'paletteId': 'eui_amsterdam_color_blind',
                            'specialAssignments': [{'color': {'type': 'loop'}, 'rule': {'type': 'other'}, 'touched': False}],
                        },
                        'layerId': IsUUID,
                        'layerType': 'data',
                        'legendDisplay': 'default',
                        'metrics': ['metric1'],
                        'nestedLegend': False,
                        'numberDisplay': 'percent',
                        'primaryGroups': ['group1'],
                    }
                ],
                'shape': 'pie',
            }
        )

        assert len(references) == 1
        assert references[0].model_dump() == snapshot(
            {'id': 'metrics-*', 'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'), 'type': 'index-pattern'}
        )

    def test_compiles_chart_with_reference_line_layer(self) -> None:
        """Test that compile_lens_chart_state merges reference line layers into XY visualization."""
        bar_chart = LensBarChart.model_validate(
            {
                'type': 'bar',
                'data_view': 'metrics-*',
                'dimension': {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        ref_line = LensReferenceLineLayer.model_validate(
            {
                'data_view': 'metrics-*',
                'reference_lines': [{'value': 100.0, 'id': 'ref1'}],
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[bar_chart, ref_line])

        # Verify references (two layers = two references)
        assert len(references) == 2
        for ref in references:
            assert ref.model_dump() == snapshot(
                {'id': 'metrics-*', 'name': IsStr(regex=r'indexpattern-datasource-layer-[a-f0-9-]+'), 'type': 'index-pattern'}
            )

        # Verify visualization layers
        vis = state.visualization
        assert vis is not None
        assert len(vis.layers) == 2

        # Verify data layer (bar chart) - find by type for stability
        data_layer = next(layer for layer in vis.layers if isinstance(layer, XYDataLayerConfig))
        assert data_layer.model_dump() == snapshot(
            {
                'accessors': ['metric1'],
                'colorMapping': {
                    'assignments': [],
                    'colorMode': {'type': 'categorical'},
                    'paletteId': 'eui_amsterdam_color_blind',
                    'specialAssignments': [{'color': {'type': 'loop'}, 'rule': {'type': 'other'}, 'touched': False}],
                },
                'layerId': IsUUID,
                'layerType': 'data',
                'position': 'top',
                'seriesType': 'bar_stacked',
                'showGridlines': False,
                'xAccessor': 'dim1',
            }
        )

        # Verify reference line layer - find by type for stability
        ref_layer = next(layer for layer in vis.layers if isinstance(layer, XYReferenceLineLayerConfig))
        assert ref_layer.model_dump() == snapshot(
            {
                'accessors': ['ref1'],
                'layerId': IsUUID,
                'layerType': 'referenceLine',
                'yConfig': [{'axisMode': 'left', 'forAccessor': 'ref1'}],
            }
        )

        # Verify datasource layers
        assert state.datasourceStates.formBased is not None
        form_based_layers = list(state.datasourceStates.formBased.layers.root.values())
        assert len(form_based_layers) == 2

        # Sort by columnOrder length to ensure consistent ordering
        sorted_layers = sorted(form_based_layers, key=lambda layer: len(layer.columnOrder), reverse=True)

        # Verify data layer datasource
        data_layer_ds = sorted_layers[0]
        assert data_layer_ds.model_dump() == snapshot(
            {
                'columnOrder': ['dim1', 'metric1'],
                'columns': {
                    'dim1': {
                        'dataType': 'date',
                        'isBucketed': True,
                        'label': '@timestamp',
                        'operationType': 'date_histogram',
                        'params': {'dropPartials': False, 'includeEmptyRows': True, 'interval': 'auto'},
                        'scale': 'interval',
                        'sourceField': '@timestamp',
                    },
                    'metric1': {
                        'dataType': 'number',
                        'isBucketed': False,
                        'label': 'Count of records',
                        'operationType': 'count',
                        'params': {'emptyAsNull': True},
                        'scale': 'ratio',
                        'sourceField': '___records___',
                    },
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )

        # Verify reference line layer datasource
        ref_layer_ds = sorted_layers[1]
        assert ref_layer_ds.model_dump() == snapshot(
            {
                'columnOrder': ['ref1'],
                'columns': {
                    'ref1': {
                        'customLabel': False,
                        'dataType': 'number',
                        'isBucketed': False,
                        'isStaticValue': True,
                        'label': 'Static value: 100.0',
                        'operationType': 'static_value',
                        'params': {'value': '100.0'},
                        'references': [],
                        'scale': 'ratio',
                    }
                },
                'incompleteColumns': {},
                'sampling': 1,
            }
        )


class TestCompileESQLChartState:
    """Tests for compile_esql_chart_state function."""

    def test_esql_metric_chart_default_time_field(self) -> None:
        """Test that ES|QL metric chart uses default time field (@timestamp) correctly."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | STATS count()',
                    'primary': {'field': 'count(*)', 'id': 'metric1'},
                },
            }
        )

        state, layer_id = compile_esql_chart_state(panel)

        # Get the layer
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        assert len(layers) == 1
        layer = next(iter(layers.values()))

        # Verify timeField is set to default
        assert layer.timeField == '@timestamp'

        # Verify layer_id is returned
        assert layer_id in layers

        # Verify adHocDataViews is empty
        assert state.adHocDataViews == {}

    def test_esql_metric_chart_custom_time_field(self) -> None:
        """Test that ES|QL metric chart uses custom time field when specified."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | STATS count()',
                    'time_field': 'event.created',
                    'primary': {'field': 'count(*)', 'id': 'metric1'},
                },
            }
        )

        state, layer_id = compile_esql_chart_state(panel)

        # Get the layer
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        # Verify timeField is set to custom value
        assert layer.timeField == 'event.created'

        # Verify layer_id is returned
        assert layer_id in layers

    def test_esql_pie_chart_custom_time_field(self) -> None:
        """Test that ES|QL pie chart correctly compiles with custom time field."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'pie',
                    'query': 'FROM logs-* | STATS count() BY status',
                    'time_field': 'timestamp',
                    'dimensions': [{'field': 'status', 'id': 'group1'}],
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        assert layer.timeField == 'timestamp'

    def test_esql_bar_chart_custom_time_field(self) -> None:
        """Test that ES|QL bar chart correctly compiles with custom time field."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'bar',
                    'query': 'FROM metrics-* | STATS count() BY @timestamp',
                    'time_field': 'event.timestamp',
                    'dimension': {'field': '@timestamp', 'id': 'dim1'},
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        assert layer.timeField == 'event.timestamp'

    def test_esql_all_chart_types_have_time_field(self) -> None:
        """Test that all ES|QL chart types correctly populate the timeField.

        This ensures consistency across metric, gauge, heatmap, pie, datatable, tagcloud, and XY charts.
        """
        from dashboard_compiler.panels.charts.config import ESQLPanel

        test_cases = [
            # Metric
            {
                'type': 'metric',
                'query': 'FROM logs-* | STATS count()',
                'primary': {'field': 'count(*)', 'id': 'metric1'},
            },
            # Gauge
            {
                'type': 'gauge',
                'query': 'FROM logs-* | STATS count()',
                'metric': {'field': 'count(*)', 'id': 'metric1'},
            },
            # Heatmap
            {
                'type': 'heatmap',
                'query': 'FROM logs-* | STATS count() BY @timestamp, status',
                'x_axis': {'field': '@timestamp', 'id': 'x1'},
                'value': {'field': 'count(*)', 'id': 'metric1'},
            },
            # Pie
            {
                'type': 'pie',
                'query': 'FROM logs-* | STATS count() BY status',
                'dimensions': [{'field': 'status', 'id': 'dim1'}],
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            },
            # Datatable
            {
                'type': 'datatable',
                'query': 'FROM logs-* | STATS count()',
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            },
            # Tagcloud
            {
                'type': 'tagcloud',
                'query': 'FROM logs-* | STATS count() BY tag',
                'dimension': {'field': 'tag', 'id': 'dim1'},
                'metric': {'field': 'count(*)', 'id': 'metric1'},
            },
            # Bar (XY chart)
            {
                'type': 'bar',
                'query': 'FROM logs-* | STATS count() BY @timestamp',
                'dimension': {'field': '@timestamp', 'id': 'dim1'},
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            },
        ]

        for chart_config in test_cases:
            panel = ESQLPanel.model_validate({'position': {'x': 0, 'y': 0}, 'size': {'w': 24, 'h': 15}, 'esql': chart_config})

            state, layer_id = compile_esql_chart_state(panel)
            assert state.datasourceStates.textBased is not None
            assert state.datasourceStates.textBased.layers is not None
            layers = state.datasourceStates.textBased.layers.root
            layer = next(iter(layers.values()))

            # Verify timeField exists and has default value
            assert layer.timeField == '@timestamp', f'Chart type {chart_config["type"]} missing or incorrect timeField'

            # Verify layer_id is returned and adHocDataViews is empty
            assert layer_id in layers
            assert state.adHocDataViews == {}


class TestESQLDataTypeDate:
    """Tests for ES|QL dimension data_type: date feature.

    The data_type field allows dimensions to specify their type, particularly useful for date fields.
    When data_type: 'date' is set, the compiled column should have meta.type = 'date' and meta.esType = 'date'.
    """

    def test_dimension_with_data_type_date_sets_meta_fields(self) -> None:
        """Test that dimension with data_type: 'date' sets meta.type and meta.esType to 'date'."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'bar',
                    'query': 'FROM logs-* | STATS count() BY time_bucket',
                    'dimension': {'field': 'time_bucket', 'id': 'dim1', 'data_type': 'date'},
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        # Find the dimension column
        dim_column = next((col for col in layer.columns if col.columnId == 'dim1'), None)
        assert dim_column is not None

        # Verify meta fields are set correctly
        assert hasattr(dim_column, 'meta')
        assert dim_column.meta is not None  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert dim_column.meta.type == 'date'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert dim_column.meta.esType == 'date'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    def test_dimension_without_data_type_has_no_meta(self) -> None:
        """Test that dimension without data_type does not have meta field."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'pie',
                    'query': 'FROM logs-* | STATS count() BY status',
                    'dimensions': [{'field': 'status', 'id': 'dim1'}],
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        # Find the dimension column
        dim_column = next((col for col in layer.columns if col.columnId == 'dim1'), None)
        assert dim_column is not None

        # Verify meta field is None
        assert hasattr(dim_column, 'meta')
        assert dim_column.meta is None  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    def test_breakdown_dimension_with_data_type_date(self) -> None:
        """Test that breakdown dimension with data_type: 'date' works correctly."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'bar',
                    'query': 'FROM logs-* | STATS count() BY category, time_bucket',
                    'dimension': {'field': 'category', 'id': 'dim1'},
                    'breakdown': {'field': 'time_bucket', 'id': 'breakdown1', 'data_type': 'date'},
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        # Find the breakdown column
        breakdown_column = next((col for col in layer.columns if col.columnId == 'breakdown1'), None)
        assert breakdown_column is not None

        # Verify meta fields are set correctly
        assert hasattr(breakdown_column, 'meta')
        assert breakdown_column.meta is not None  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert breakdown_column.meta.type == 'date'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert breakdown_column.meta.esType == 'date'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    def test_pie_chart_with_date_dimension(self) -> None:
        """Test that pie chart with date dimension correctly sets meta fields."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'pie',
                    'query': 'FROM logs-* | STATS count() BY date_bucket',
                    'dimensions': [{'field': 'date_bucket', 'id': 'dim1', 'data_type': 'date'}],
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        dim_column = next((col for col in layer.columns if col.columnId == 'dim1'), None)
        assert dim_column is not None

        assert hasattr(dim_column, 'meta')
        assert dim_column.meta is not None  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert dim_column.meta.type == 'date'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]

    def test_heatmap_x_axis_with_data_type_date(self) -> None:
        """Test that heatmap x_axis with data_type: 'date' correctly sets meta fields."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'heatmap',
                    'query': 'FROM logs-* | STATS count() BY time_bucket, status',
                    'x_axis': {'field': 'time_bucket', 'id': 'x1', 'data_type': 'date'},
                    'y_axis': {'field': 'status', 'id': 'y1'},
                    'value': {'field': 'count(*)', 'id': 'metric1'},
                },
            }
        )

        state, _references = compile_esql_chart_state(panel)
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root
        layer = next(iter(layers.values()))

        x_axis_column = next((col for col in layer.columns if col.columnId == 'x1'), None)
        assert x_axis_column is not None

        assert hasattr(x_axis_column, 'meta')
        assert x_axis_column.meta is not None  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
        assert x_axis_column.meta.type == 'date'  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]


class TestCompileChartsPanelConfig:
    """Tests for compile_charts_panel_config function."""

    def test_lens_panel_with_hide_title_true(self) -> None:
        """Test that hide_title=True is correctly passed to embeddable config."""
        from dashboard_compiler.panels.charts.config import LensPanel

        panel = LensPanel.model_validate(
            {
                'title': 'My Metric Panel',
                'hide_title': True,
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'metric1'},
                },
            }
        )

        _references, embeddable_config = compile_charts_panel_config(panel)

        assert embeddable_config.hidePanelTitles is True

    def test_lens_panel_with_hide_title_false(self) -> None:
        """Test that hide_title=False is correctly passed to embeddable config."""
        from dashboard_compiler.panels.charts.config import LensPanel

        panel = LensPanel.model_validate(
            {
                'title': 'My Metric Panel',
                'hide_title': False,
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'metric1'},
                },
            }
        )

        _references, embeddable_config = compile_charts_panel_config(panel)

        assert embeddable_config.hidePanelTitles is False

    def test_lens_panel_without_hide_title(self) -> None:
        """Test that hide_title defaults to None when not specified."""
        from dashboard_compiler.panels.charts.config import LensPanel

        panel = LensPanel.model_validate(
            {
                'title': 'My Metric Panel',
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'lens': {
                    'type': 'metric',
                    'data_view': 'metrics-*',
                    'primary': {'aggregation': 'count', 'id': 'metric1'},
                },
            }
        )

        _references, embeddable_config = compile_charts_panel_config(panel)

        assert embeddable_config.hidePanelTitles is None

    def test_esql_panel_with_hide_title_true(self) -> None:
        """Test that hide_title=True is correctly passed for ESQL panels."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'title': 'My ESQL Metric',
                'hide_title': True,
                'position': {'x': 0, 'y': 0},
                'size': {'w': 24, 'h': 15},
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | STATS count()',
                    'primary': {'field': 'count(*)', 'id': 'metric1'},
                },
            }
        )

        _references, embeddable_config = compile_charts_panel_config(panel)

        assert embeddable_config.hidePanelTitles is True
