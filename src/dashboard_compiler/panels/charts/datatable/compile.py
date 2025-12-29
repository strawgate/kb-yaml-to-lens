from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldDimensionColumn, KbnESQLFieldMetricColumn

from dashboard_compiler.panels.charts.datatable.config import (
    DatatableAlignmentEnum,
    DatatableColorModeEnum,
    DatatableDensityEnum,
    DatatableRowHeightEnum,
    DatatableSummaryRowEnum,
    ESQLDatatableChart,
    LensDatatableChart,
)
from dashboard_compiler.panels.charts.datatable.view import (
    KbnDatatableColumnState,
    KbnDatatablePagingState,
    KbnDatatableSortingState,
    KbnDatatableVisualizationState,
)
from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLColumnTypes
from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.shared.config import random_id_generator


def compile_lens_datatable_chart(
    lens_datatable_chart: LensDatatableChart,
) -> tuple[str, dict[str, KbnLensColumnTypes], KbnDatatableVisualizationState]:
    """Compile a LensDatatableChart config object into a Kibana Lens Datatable visualization state.

    Args:
        lens_datatable_chart (LensDatatableChart): The LensDatatableChart object to compile.

    Returns:
        tuple[str, dict[str, KbnLensColumnTypes], KbnDatatableVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (dict[str, KbnLensColumnTypes]): A dictionary of columns for the layer.
            - kbn_state_visualization (KbnDatatableVisualizationState): The compiled visualization state.

    """
    layer_id = lens_datatable_chart.id or random_id_generator()
    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {}
    column_order: list[str] = []

    # Compile metrics
    for metric in lens_datatable_chart.metrics:
        metric_id, compiled_metric = compile_lens_metric(metric)
        kbn_columns_by_id[metric_id] = compiled_metric
        column_order.append(metric_id)

    # Store metric columns for dimension compilation
    kbn_metric_columns_by_id = dict(kbn_columns_by_id)

    # Compile dimensions (breakdowns)
    for breakdown in lens_datatable_chart.breakdowns:
        breakdown_id, compiled_breakdown = compile_lens_dimension(
            dimension=breakdown,
            kbn_metric_column_by_id=kbn_metric_columns_by_id,  # pyright: ignore[reportArgumentType]
        )
        kbn_columns_by_id[breakdown_id] = compiled_breakdown
        column_order.append(breakdown_id)

    # Build column states
    column_states: list[KbnDatatableColumnState] = []
    for column_id in column_order:
        # Find user config for this column if exists
        user_config = None
        if lens_datatable_chart.columns:
            user_config = next((c for c in lens_datatable_chart.columns if c.column_id == column_id), None)

        # Handle enum fields which may be strings due to strict=False - always extract .value if enum
        alignment_val = None
        if user_config and user_config.alignment:
            alignment_val = (
                user_config.alignment.value
                if isinstance(user_config.alignment, DatatableAlignmentEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
                else user_config.alignment
            )

        color_mode_val = None
        if user_config and user_config.color_mode:
            color_mode_val = (
                user_config.color_mode.value
                if isinstance(user_config.color_mode, DatatableColorModeEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
                else user_config.color_mode
            )

        summary_row_val = None
        if user_config and user_config.summary_row:
            summary_row_val = (
                user_config.summary_row.value
                if isinstance(user_config.summary_row, DatatableSummaryRowEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
                else user_config.summary_row
            )

        column_state = KbnDatatableColumnState(
            columnId=column_id,
            width=user_config.width if user_config else None,
            hidden=user_config.hidden if user_config and user_config.hidden else None,
            alignment=alignment_val,
            colorMode=color_mode_val,
            summaryRow=summary_row_val,
            summaryLabel=user_config.summary_label if user_config else None,
        )
        column_states.append(column_state)

    # Build sorting state
    sorting_state = None
    if lens_datatable_chart.sorting:
        sorting_state = KbnDatatableSortingState(
            columnId=lens_datatable_chart.sorting.column_id,
            direction=lens_datatable_chart.sorting.direction,
        )

    # Build paging state
    paging_state = None
    if lens_datatable_chart.paging:
        paging_state = KbnDatatablePagingState(
            size=lens_datatable_chart.paging.page_size,
            enabled=lens_datatable_chart.paging.enabled,
        )

    # Build visualization state
    # Extract enum values, handling both enum and string types (pydantic may coerce with strict=False)
    row_height_val = (
        lens_datatable_chart.row_height.value
        if isinstance(lens_datatable_chart.row_height, DatatableRowHeightEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
        else lens_datatable_chart.row_height
    )
    row_height_value = None if row_height_val == 'auto' else row_height_val

    header_row_height_val = (
        lens_datatable_chart.header_row_height.value
        if isinstance(lens_datatable_chart.header_row_height, DatatableRowHeightEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
        else lens_datatable_chart.header_row_height
    )
    header_row_height_value = None if header_row_height_val == 'auto' else header_row_height_val

    density_val = (
        lens_datatable_chart.density.value
        if isinstance(lens_datatable_chart.density, DatatableDensityEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
        else lens_datatable_chart.density
    )
    density_value = None if density_val == 'normal' else density_val

    visualization_state = KbnDatatableVisualizationState(
        columns=column_states,
        layerId=layer_id,
        layerType='data',
        sorting=sorting_state,
        rowHeight=row_height_value,
        headerRowHeight=header_row_height_value,
        rowHeightLines=lens_datatable_chart.row_height_lines,
        headerRowHeightLines=lens_datatable_chart.header_row_height_lines,
        paging=paging_state,
        density=density_value,
    )

    return layer_id, kbn_columns_by_id, visualization_state


def compile_esql_datatable_chart(
    esql_datatable_chart: ESQLDatatableChart,
) -> tuple[str, list[KbnESQLColumnTypes], KbnDatatableVisualizationState]:
    """Compile an ESQL LensDatatableChart config object into a Kibana Lens Datatable visualization state.

    Args:
        esql_datatable_chart (ESQLDatatableChart): The ESQLDatatableChart object to compile.

    Returns:
        tuple[str, list[KbnESQLColumnTypes], KbnDatatableVisualizationState]: A tuple containing:
            - layer_id (str): The ID of the layer.
            - kbn_columns (list[KbnESQLColumnTypes]): A list of columns for the layer.
            - kbn_state_visualization (KbnDatatableVisualizationState): The compiled visualization state.

    """
    layer_id = esql_datatable_chart.id or random_id_generator()
    kbn_columns: list[KbnESQLColumnTypes] = []
    column_order: list[str] = []

    # Compile metrics
    for metric in esql_datatable_chart.metrics:
        compiled_metric: KbnESQLFieldMetricColumn = compile_esql_metric(metric)
        kbn_columns.append(compiled_metric)
        column_order.append(compiled_metric.columnId)

    # Compile dimensions (breakdowns)
    for breakdown in esql_datatable_chart.breakdowns:
        compiled_breakdown: KbnESQLFieldDimensionColumn = compile_esql_dimension(breakdown)
        kbn_columns.append(compiled_breakdown)
        column_order.append(compiled_breakdown.columnId)

    # Build column states
    column_states: list[KbnDatatableColumnState] = []
    for column_id in column_order:
        # Find user config for this column if exists
        user_config = None
        if esql_datatable_chart.columns:
            user_config = next((c for c in esql_datatable_chart.columns if c.column_id == column_id), None)

        # Handle enum fields which may be strings due to strict=False - always extract .value if enum
        alignment_val = None
        if user_config and user_config.alignment:
            alignment_val = (
                user_config.alignment.value
                if isinstance(user_config.alignment, DatatableAlignmentEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
                else user_config.alignment
            )

        color_mode_val = None
        if user_config and user_config.color_mode:
            color_mode_val = (
                user_config.color_mode.value
                if isinstance(user_config.color_mode, DatatableColorModeEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
                else user_config.color_mode
            )

        summary_row_val = None
        if user_config and user_config.summary_row:
            summary_row_val = (
                user_config.summary_row.value
                if isinstance(user_config.summary_row, DatatableSummaryRowEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
                else user_config.summary_row
            )

        column_state = KbnDatatableColumnState(
            columnId=column_id,
            width=user_config.width if user_config else None,
            hidden=user_config.hidden if user_config and user_config.hidden else None,
            alignment=alignment_val,
            colorMode=color_mode_val,
            summaryRow=summary_row_val,
            summaryLabel=user_config.summary_label if user_config else None,
        )
        column_states.append(column_state)

    # Build sorting state
    sorting_state = None
    if esql_datatable_chart.sorting:
        sorting_state = KbnDatatableSortingState(
            columnId=esql_datatable_chart.sorting.column_id,
            direction=esql_datatable_chart.sorting.direction,
        )

    # Build paging state
    paging_state = None
    if esql_datatable_chart.paging:
        paging_state = KbnDatatablePagingState(
            size=esql_datatable_chart.paging.page_size,
            enabled=esql_datatable_chart.paging.enabled,
        )

    # Build visualization state
    # Extract enum values, handling both enum and string types (pydantic may coerce with strict=False)
    row_height_val = (
        esql_datatable_chart.row_height.value
        if isinstance(esql_datatable_chart.row_height, DatatableRowHeightEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
        else esql_datatable_chart.row_height
    )
    row_height_value = None if row_height_val == 'auto' else row_height_val

    header_row_height_val = (
        esql_datatable_chart.header_row_height.value
        if isinstance(esql_datatable_chart.header_row_height, DatatableRowHeightEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
        else esql_datatable_chart.header_row_height
    )
    header_row_height_value = None if header_row_height_val == 'auto' else header_row_height_val

    density_val = (
        esql_datatable_chart.density.value
        if isinstance(esql_datatable_chart.density, DatatableDensityEnum)  # pyright: ignore[reportUnnecessaryIsInstance]
        else esql_datatable_chart.density
    )
    density_value = None if density_val == 'normal' else density_val

    visualization_state = KbnDatatableVisualizationState(
        columns=column_states,
        layerId=layer_id,
        layerType='data',
        sorting=sorting_state,
        rowHeight=row_height_value,
        headerRowHeight=header_row_height_value,
        rowHeightLines=esql_datatable_chart.row_height_lines,
        headerRowHeightLines=esql_datatable_chart.header_row_height_lines,
        paging=paging_state,
        density=density_value,
    )

    return layer_id, kbn_columns, visualization_state
