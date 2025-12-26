from collections.abc import Sequence

from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
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
    columns_by_id = {}
    columns_by_name = {}
    for metric in metrics:
        columns_by_id[metric.id] = compile_lens_metric(metric)
        columns_by_name[metric.label] = columns_by_id[metric.id]

    for dimension in dimensions:
        columns_by_id[dimension.id] = compile_lens_dimension(dimension, kbn_metric_column_by_id=columns_by_id)  # pyright: ignore[reportUnknownArgumentType]

    return columns_by_id  # pyright: ignore[reportUnknownVariableType]


# def compile_lens_dimensions(dimensions: list[LensDimensionTypes], kbn_columns: list[KbnColumn]) -> dict[str, KbnColumn]:
#     dimensions_by_id = {}

#     for i, dimension in enumerate(dimensions):
#         id = dimension.id or stable_id_generator([str(i), dimension.type, dimension.field])

#         # Determine dataType and scale based on dimension type
#         data_type = 'string'
#         scale = 'ordinal'
#         params: dict[str, Any] = {}

#         if dimension.type == 'date_histogram':
#             data_type = 'date'
#             scale = 'interval'
#             params = {
#                 'interval': dimension.interval or 'auto',
#                 'includeEmptyRows': True,
#                 'dropPartials': False,
#                 # "parentFormat": {  # Added parentFormat for date_histogram
#                 #     "id": dimension.type,
#                 # },
#             }
#         elif dimension.type == 'terms':
#             params = {
#                 'size': dimension.size,
#                 'orderBy': {'type': 'column', 'columnId': metrics_by_name.get(dimension.sort.by)}
#                 if dimension.sort and dimension.sort.by in metrics_by_name
#                 else None,
#                 'orderDirection': dimension.sort.direction if dimension.sort else 'asc',
#                 'otherBucket': dimension.other_bucket or True,  # Mapped from config
#                 'missingBucket': dimension.missing_bucket or False,  # Mapped from config
#                 'parentFormat': {
#                     'id': dimension.type,
#                 },
#                 'include': dimension.include or [],  # Mapped from config
#                 'exclude': dimension.exclude or [],  # Mapped from config
#                 'includeIsRegex': dimension.include_is_regex or False,  # Mapped from config
#                 'excludeIsRegex': dimension.exclude_is_regex or False,  # Mapped from config
#             }
#         elif dimension.type == 'histogram':  # Added histogram type
#             data_type = 'number'
#             scale = 'interval'
#             params = {
#                 'interval': dimension.interval,  # Mapped from config
#                 # "parentFormat": {
#                 #     "id": dimension.type,
#                 # },
#             }
#         elif dimension.type == 'filters':  # Added filters type
#             data_type = 'string'
#             scale = 'ordinal'
#             params = {
#                 'filters': dimension.filters,  # Mapped from config
#                 # "parentFormat": {
#                 #     "id": dimension.type,
#                 # },
#             }

#         dimensions_by_id[id] = KbnColumn(
#             label=dimension.label or dimension.field,
#             dataType=data_type,
#             operationType=dimension.type,
#             scale=scale,
#             sourceField=dimension.field,
#             isBucketed=True,
#             params=params,
#         )

#     return dimensions_by_id
