"""Tests for chart compilation utilities."""

import pytest

from dashboard_compiler.panels.charts.compile import (
    chart_type_to_kbn_type_lens,
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


class TestChartTypeToKbnTypeLens:
    """Tests for chart_type_to_kbn_type_lens function."""

    def test_identifies_lens_pie_chart(self) -> None:
        """Test that LensPieChart is identified correctly."""
        chart = LensPieChart.model_validate(
            {
                'type': 'pie',
                'data_view': 'metrics-*',
                'slice_by': [{'type': 'values', 'field': 'status', 'id': 'group1'}],
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
                'slice_by': [{'field': 'status', 'id': 'group1'}],
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
                'dimensions': [{'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'}],
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
                'dimensions': [{'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'}],
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
                'dimensions': [{'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'}],
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
                'dimensions': [{'field': '@timestamp', 'id': 'dim1'}],
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            }
        )
        assert chart_type_to_kbn_type_lens(area_chart) == KbnVisualizationTypeEnum.XY

        bar_chart = ESQLBarChart.model_validate(
            {
                'type': 'bar',
                'dimensions': [{'field': '@timestamp', 'id': 'dim1'}],
                'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
            }
        )
        assert chart_type_to_kbn_type_lens(bar_chart) == KbnVisualizationTypeEnum.XY

        line_chart = ESQLLineChart.model_validate(
            {
                'type': 'line',
                'dimensions': [{'field': '@timestamp', 'id': 'dim1'}],
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
                'tags': {'type': 'values', 'field': 'tag', 'id': 'tags1'},
                'metrics': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        result = chart_type_to_kbn_type_lens(chart)
        assert result == KbnVisualizationTypeEnum.TAGCLOUD

    def test_identifies_esql_tagcloud_chart(self) -> None:
        """Test that ESQLTagcloudChart is identified correctly."""
        chart = ESQLTagcloudChart.model_validate(
            {
                'type': 'tagcloud',
                'tags': {'field': 'tag', 'id': 'tags1'},
                'metrics': {'field': 'count(*)', 'id': 'metric1'},
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
        assert state is not None
        assert state.visualization is not None
        assert len(references) == 1
        assert references[0].type == 'index-pattern'

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
        assert state is not None
        assert state.visualization is not None
        assert len(references) == 1

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
        assert state is not None
        assert state.visualization is not None
        assert len(references) == 1

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
        assert state is not None
        assert state.visualization is not None
        assert len(references) == 1

    def test_compiles_tagcloud_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a tagcloud chart."""
        tagcloud_chart = LensTagcloudChart.model_validate(
            {
                'type': 'tagcloud',
                'data_view': 'metrics-*',
                'tags': {'type': 'values', 'field': 'tag', 'id': 'tags1'},
                'metrics': {'aggregation': 'count', 'id': 'metric1'},
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[tagcloud_chart])
        assert state is not None
        assert state.visualization is not None
        assert len(references) == 1

    def test_compiles_pie_chart(self) -> None:
        """Test that compile_lens_chart_state correctly compiles a pie chart."""
        pie_chart = LensPieChart.model_validate(
            {
                'type': 'pie',
                'data_view': 'metrics-*',
                'slice_by': [{'type': 'values', 'field': 'status', 'id': 'group1'}],
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        state, references = compile_lens_chart_state(query=None, filters=None, charts=[pie_chart])
        assert state is not None
        assert state.visualization is not None
        assert len(references) == 1

    def test_compiles_chart_with_reference_line_layer(self) -> None:
        """Test that compile_lens_chart_state merges reference line layers into XY visualization."""
        bar_chart = LensBarChart.model_validate(
            {
                'type': 'bar',
                'data_view': 'metrics-*',
                'dimensions': [{'type': 'date_histogram', 'field': '@timestamp', 'id': 'dim1'}],
                'metrics': [{'aggregation': 'count', 'id': 'metric1'}],
            }
        )
        ref_line = LensReferenceLineLayer.model_validate(
            {
                'data_view': 'metrics-*',
                'reference_lines': [{'value': 100.0, 'id': 'ref1'}],
            }
        )
        state, _references = compile_lens_chart_state(query=None, filters=None, charts=[bar_chart, ref_line])
        assert state is not None
        assert state.visualization is not None
        # Verify that reference lines were merged - should have both data layer and reference line layer
        layers = state.visualization.layers
        assert len(layers) == 2

        # Check first layer is the bar chart data layer
        data_layer = layers[0]
        assert isinstance(data_layer, XYDataLayerConfig)
        assert data_layer.seriesType == 'bar_stacked'
        assert data_layer.xAccessor == 'dim1'
        assert data_layer.accessors == ['metric1']

        # Check second layer is the reference line layer
        ref_layer = layers[1]
        assert isinstance(ref_layer, XYReferenceLineLayerConfig)
        assert ref_layer.layerType == 'referenceLine'
        assert ref_layer.accessors == ['ref1']
        assert ref_layer.yConfig is not None
        assert len(ref_layer.yConfig) == 1
        assert ref_layer.yConfig[0].forAccessor == 'ref1'


class TestCompileESQLChartState:
    """Tests for compile_esql_chart_state function."""

    def test_esql_metric_chart_default_time_field(self) -> None:
        """Test that ES|QL metric chart uses default timeField (@timestamp)."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | STATS count()',
                    'primary': {'field': 'count(*)', 'id': 'metric1'},
                },
            }
        )

        state, layer_id = compile_esql_chart_state(panel)

        assert state.datasourceStates is not None
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root

        # Access the specific layer using returned layer_id
        first_layer = layers[layer_id]
        assert first_layer.timeField == '@timestamp'

    def test_esql_metric_chart_custom_time_field(self) -> None:
        """Test that ES|QL metric chart uses custom timeField when specified."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                'esql': {
                    'type': 'metric',
                    'query': 'FROM logs-* | STATS count()',
                    'timeField': 'event.created',
                    'primary': {'field': 'count(*)', 'id': 'metric1'},
                },
            }
        )

        state, layer_id = compile_esql_chart_state(panel)

        assert state.datasourceStates is not None
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root

        # Access the specific layer using returned layer_id
        first_layer = layers[layer_id]
        assert first_layer.timeField == 'event.created'

    def test_esql_pie_chart_custom_time_field(self) -> None:
        """Test that ES|QL pie chart uses custom timeField when specified."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                'esql': {
                    'type': 'pie',
                    'query': 'FROM logs-* | STATS count() BY status',
                    'timeField': 'timestamp',
                    'slice_by': [{'field': 'status', 'id': 'group1'}],
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, layer_id = compile_esql_chart_state(panel)

        assert state.datasourceStates is not None
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root

        # Access the specific layer using returned layer_id
        first_layer = layers[layer_id]
        assert first_layer.timeField == 'timestamp'

    def test_esql_bar_chart_custom_time_field(self) -> None:
        """Test that ES|QL bar chart uses custom timeField when specified."""
        from dashboard_compiler.panels.charts.config import ESQLPanel

        panel = ESQLPanel.model_validate(
            {
                'grid': {'x': 0, 'y': 0, 'w': 24, 'h': 15},
                'esql': {
                    'type': 'bar',
                    'query': 'FROM metrics-* | STATS count() BY @timestamp',
                    'timeField': 'event.timestamp',
                    'dimensions': [{'field': '@timestamp', 'id': 'dim1'}],
                    'metrics': [{'field': 'count(*)', 'id': 'metric1'}],
                },
            }
        )

        state, layer_id = compile_esql_chart_state(panel)

        assert state.datasourceStates is not None
        assert state.datasourceStates.textBased is not None
        assert state.datasourceStates.textBased.layers is not None
        layers = state.datasourceStates.textBased.layers.root

        # Access the specific layer using returned layer_id
        first_layer = layers[layer_id]
        assert first_layer.timeField == 'event.timestamp'
