from typing import Any

from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric
from dashboard_compiler.models.views.panels.lens import (
    KbnColumn,
)


def compile_metrics(metrics: list[Metric]) -> tuple[dict[str, KbnColumn], dict[str, str]]:
    metrics_by_id = {}
    metrics_by_name = {}

    for i, metric in enumerate(metrics):
        id = metric.id or stable_id_generator([str(i), metric.type, metric.field])

        metrics_by_id[id] = KbnColumn(
            label=metric.label, #f"{metric.type} of {metric.field}",
            customLabel=metric.label is not None,
            dataType="number",
            operationType=metric.type,
            scale="ratio",
            sourceField=metric.field,
            isBucketed=False,
            params={
                "emptyAsNull": True,
            },
        )

        metrics_by_name[metric.label] = id

    return metrics_by_id, metrics_by_name


def compile_dimensions(dimensions: list[Dimension], metrics_by_name: dict[str, str]) -> dict[str, KbnColumn]:
    dimensions_by_id = {}

    for i, dimension in enumerate(dimensions):
        id = dimension.id or stable_id_generator([str(i), dimension.type, dimension.field])

        # Determine dataType and scale based on dimension type
        data_type = "string"
        scale = "ordinal"
        params: dict[str, Any] = {}

        if dimension.type == "date_histogram":
            data_type = "date"
            scale = "interval"
            params = {
                "interval": dimension.interval or "auto",
                "includeEmptyRows": True,
                "dropPartials": False,
                # "parentFormat": {  # Added parentFormat for date_histogram
                #     "id": dimension.type,
                # },
            }
        elif dimension.type == "terms":

            params = {
                "size": dimension.size,
                "orderBy": {"type": "column", "columnId": metrics_by_name.get(dimension.sort.by)}
                if dimension.sort and dimension.sort.by in metrics_by_name
                else None,
                "orderDirection": dimension.sort.direction if dimension.sort else "asc",
                "otherBucket": dimension.other_bucket,  # Mapped from config
                "missingBucket": dimension.missing_bucket,  # Mapped from config
                "parentFormat": {
                    "id": dimension.type,
                },
                "include": dimension.include,  # Mapped from config
                "exclude": dimension.exclude,  # Mapped from config
                "includeIsRegex": dimension.include_is_regex,  # Mapped from config
                "excludeIsRegex": dimension.exclude_is_regex,  # Mapped from config
            }
        elif dimension.type == "histogram":  # Added histogram type
            data_type = "number"
            scale = "interval"
            params = {
                "interval": dimension.interval,  # Mapped from config
                # "parentFormat": {
                #     "id": dimension.type,
                # },
            }
        elif dimension.type == "filters":  # Added filters type
            data_type = "string"
            scale = "ordinal"
            params = {
                "filters": dimension.filters,  # Mapped from config
                # "parentFormat": {
                #     "id": dimension.type,
                # },
            }

        dimensions_by_id[id] = KbnColumn(
            label=dimension.label or dimension.field,
            dataType=data_type,
            operationType=dimension.type,
            scale=scale,
            sourceField=dimension.field,
            isBucketed=True,
            params=params,
        )

    return dimensions_by_id
