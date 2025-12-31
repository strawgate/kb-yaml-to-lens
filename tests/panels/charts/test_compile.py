
import pytest

from dashboard_compiler.panels.charts.compile import chart_type_to_kbn_type_lens, compile_lens_chart_state
from dashboard_compiler.panels.charts.config import LensBarChart, LensMetricChart, LensPieChart
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDateHistogramDimension
from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
from dashboard_compiler.panels.charts.view import KbnVisualizationTypeEnum


def test_chart_type_to_kbn_type_lens_pie() -> None:
    """Test chart type conversion for Pie charts."""
    chart = LensPieChart(
        data_view='test_view',
        slice_by=[
            LensDateHistogramDimension(field='@timestamp')
        ],
        metric=LensCountAggregatedMetric()
    )
    assert chart_type_to_kbn_type_lens(chart) == KbnVisualizationTypeEnum.PIE


def test_chart_type_to_kbn_type_lens_xy() -> None:
    """Test chart type conversion for XY charts."""
    chart = LensBarChart(
        data_view='test_view',
        dimensions=[
            LensDateHistogramDimension(field='@timestamp')
        ],
        metrics=[
            LensCountAggregatedMetric()
        ]
    )
    assert chart_type_to_kbn_type_lens(chart) == KbnVisualizationTypeEnum.XY


def test_chart_type_to_kbn_type_lens_metric() -> None:
    """Test chart type conversion for Metric charts."""
    chart = LensMetricChart(
        data_view='test_view',
        primary=LensCountAggregatedMetric()
    )
    assert chart_type_to_kbn_type_lens(chart) == KbnVisualizationTypeEnum.METRIC


def test_compile_lens_chart_state_empty_charts() -> None:
    """Test that empty charts list raises ValueError."""
    with pytest.raises(ValueError, match='At least one chart must be provided'):
        compile_lens_chart_state(query=None, filters=None, charts=[])


def test_compile_lens_chart_state_unsupported_chart() -> None:
    """Test that unsupported chart types raise NotImplementedError."""
    class UnsupportedChart:
        data_view = 'test'

    with pytest.raises(NotImplementedError, match='Unsupported chart type'):
        compile_lens_chart_state(query=None, filters=None, charts=[UnsupportedChart()]) # pyright: ignore[reportArgumentType]
