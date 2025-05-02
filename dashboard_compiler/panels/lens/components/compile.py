from typing import Any

from dashboard_compiler.panels.lens.dimension.config import Dimension
from dashboard_compiler.panels.lens.view import (
    KbnColumn,
)
from dashboard_compiler.shared.config import stable_id_generator


def compile_dimensions(dimensions: list[Dimension], metrics_by_name: dict[str, str]) -> dict[str, KbnColumn]:
    dimensions_by_id = {}

    for i, dimension in enumerate(dimensions):
        id = dimension.id or stable_id_generator([str(i), dimension.type, dimension.field])

        # Determine dataType and scale based on dimension type
        data_type = 'string'
        scale = 'ordinal'
        params: dict[str, Any] = {}

        if dimension.type == 'date_histogram':
            data_type = 'date'
            scale = 'interval'
            params = {
                'interval': dimension.interval or 'auto',
                'includeEmptyRows': True,
                'dropPartials': False,
                # "parentFormat": {  # Added parentFormat for date_histogram
                #     "id": dimension.type,
                # },
            }
        elif dimension.type == 'terms':
            params = {
                'size': dimension.size,
                'orderBy': {'type': 'column', 'columnId': metrics_by_name.get(dimension.sort.by)}
                if dimension.sort and dimension.sort.by in metrics_by_name
                else None,
                'orderDirection': dimension.sort.direction if dimension.sort else 'asc',
                'otherBucket': dimension.other_bucket or True,  # Mapped from config
                'missingBucket': dimension.missing_bucket or False,  # Mapped from config
                'parentFormat': {
                    'id': dimension.type,
                },
                'include': dimension.include or [],  # Mapped from config
                'exclude': dimension.exclude or [],  # Mapped from config
                'includeIsRegex': dimension.include_is_regex or False,  # Mapped from config
                'excludeIsRegex': dimension.exclude_is_regex or False,  # Mapped from config
            }
        elif dimension.type == 'histogram':  # Added histogram type
            data_type = 'number'
            scale = 'interval'
            params = {
                'interval': dimension.interval,  # Mapped from config
                # "parentFormat": {
                #     "id": dimension.type,
                # },
            }
        elif dimension.type == 'filters':  # Added filters type
            data_type = 'string'
            scale = 'ordinal'
            params = {
                'filters': dimension.filters,  # Mapped from config
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
