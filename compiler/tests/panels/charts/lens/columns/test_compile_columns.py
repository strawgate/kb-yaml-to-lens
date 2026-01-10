"""Tests for Lens column compilation."""

from pydantic import TypeAdapter

from dashboard_compiler.panels.charts.lens.columns.compile import compile_lens_columns
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


def test_compile_lens_columns_combines_metrics_and_dimensions() -> None:
    """Ensure metric and dimension columns are compiled together."""
    metric_config = {'aggregation': 'count', 'id': 'metric-1'}
    dimension_config = {'type': 'date_histogram', 'field': '@timestamp', 'id': 'dimension-1'}

    metric = TypeAdapter(LensMetricTypes).validate_python(metric_config)
    dimension = TypeAdapter(LensDimensionTypes).validate_python(dimension_config)

    columns = compile_lens_columns([dimension], [metric])

    assert set(columns.keys()) == {'metric-1', 'dimension-1'}
    assert columns['metric-1'].label == 'Count of records'
    assert columns['dimension-1'].operationType == 'date_histogram'
    assert columns['dimension-1'].sourceField == '@timestamp'
