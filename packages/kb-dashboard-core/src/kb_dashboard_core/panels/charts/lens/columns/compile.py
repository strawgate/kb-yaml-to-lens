from collections.abc import Sequence

from kb_dashboard_core.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimension
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes


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
        result = compile_lens_metric(metric)
        # Add the primary column
        columns_by_id[result.primary_id] = result.primary_column
        metrics_by_label[result.primary_column.label] = result.primary_column
        # Add any helper columns (for formulas)
        columns_by_id.update(result.helper_columns)

    for dimension in dimensions:
        dimension_id, dimension_column = compile_lens_dimension(dimension, kbn_metric_column_by_id=metrics_by_label)
        columns_by_id[dimension_id] = dimension_column

    return columns_by_id
