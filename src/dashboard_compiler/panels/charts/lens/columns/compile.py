from collections.abc import Sequence

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


def compile_lens_columns(dimensions: Sequence[LensDimensionTypes], metrics: Sequence[LensMetricTypes]) -> dict[str, KbnLensColumnTypes]:
    """Compile sequences of LensDimensionTypes and LensMetricTypes into their Kibana view model representation.

    Args:
        dimensions (Sequence[LensDimensionTypes]): The sequence of LensDimensionTypes to compile.
        metrics (Sequence[LensMetricTypes]): The sequence of LensMetricTypes to compile.

    Returns:
        dict[str, KbnLensColumnTypes]: A dictionary mapping column IDs to their compiled KbnLensColumnTypes.

    """
    columns_by_id: dict[str, KbnLensColumnTypes] = {}
    metrics_by_label: dict[str, KbnLensMetricColumnTypes] = {}

    for metric in metrics:
        metric_id, metric_column = compile_lens_metric(metric)
        columns_by_id[metric_id] = metric_column
        metrics_by_label[metric_column.label] = metric_column

    for dimension in dimensions:
        dimension_id, dimension_column = compile_lens_dimension(dimension, kbn_metric_column_by_id=metrics_by_label)
        columns_by_id[dimension_id] = dimension_column

    return columns_by_id
