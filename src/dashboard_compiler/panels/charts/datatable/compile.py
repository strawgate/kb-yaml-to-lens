from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldDimensionColumn, KbnESQLFieldMetricColumn

from dashboard_compiler.panels.charts.datatable.config import (
    DatatableDensityEnum,
    DatatableMetricColumnConfig,
    DatatableRowHeightEnum,
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

    # Compile row dimensions
    for row in lens_datatable_chart.rows:
        row_id, compiled_row = compile_lens_dimension(
            dimension=row,
            kbn_metric_column_by_id=kbn_metric_columns_by_id,  # pyright: ignore[reportArgumentType]
        )
        kbn_columns_by_id[row_id] = compiled_row
        column_order.append(row_id)

    # Compile rows_by dimensions (split metrics by)
    if lens_datatable_chart.rows_by is not None:
        for rows_by_dim in lens_datatable_chart.rows_by:
            rows_by_id, compiled_rows_by = compile_lens_dimension(
                dimension=rows_by_dim,
                kbn_metric_column_by_id=kbn_metric_columns_by_id,  # pyright: ignore[reportArgumentType]
            )
            kbn_columns_by_id[rows_by_id] = compiled_rows_by
            column_order.append(rows_by_id)

    # Build column states
    column_states: list[KbnDatatableColumnState] = []
    for column_id in column_order:
        # Determine if this is a metric column or a row column
        is_metric = column_id in kbn_metric_columns_by_id

        # Find user config for this column
        user_config = None
        if is_metric and lens_datatable_chart.metric_columns is not None:
            user_config = next((c for c in lens_datatable_chart.metric_columns if c.column_id == column_id), None)
        elif not is_metric and lens_datatable_chart.columns is not None:
            user_config = next((c for c in lens_datatable_chart.columns if c.column_id == column_id), None)

        # Build column state with summary fields only for metrics
        summary_row = None
        summary_label = None
        if is_metric and isinstance(user_config, DatatableMetricColumnConfig):
            summary_row = user_config.summary_row
            summary_label = user_config.summary_label

        column_state = KbnDatatableColumnState(
            columnId=column_id,
            width=user_config.width if user_config else None,
            hidden=user_config.hidden if user_config and user_config.hidden else None,
            alignment=user_config.alignment if user_config else None,
            colorMode=user_config.color_mode if user_config else None,
            summaryRow=summary_row,
            summaryLabel=summary_label,
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
    # Extract appearance settings if provided, otherwise use defaults
    appearance = lens_datatable_chart.appearance
    row_height_value = None
    header_row_height_value = None
    row_height_lines = None
    header_row_height_lines = None
    density_value = None

    if appearance is not None:
        # Omit default values (auto for row heights, normal for density) to match Kibana defaults
        row_height_value = None if appearance.row_height == DatatableRowHeightEnum.AUTO else appearance.row_height
        header_row_height_value = None if appearance.header_row_height == DatatableRowHeightEnum.AUTO else appearance.header_row_height
        density_value = None if appearance.density == DatatableDensityEnum.NORMAL else appearance.density
        row_height_lines = appearance.row_height_lines
        header_row_height_lines = appearance.header_row_height_lines

    visualization_state = KbnDatatableVisualizationState(
        columns=column_states,
        layerId=layer_id,
        layerType='data',
        sorting=sorting_state,
        rowHeight=row_height_value,
        headerRowHeight=header_row_height_value,
        rowHeightLines=row_height_lines,
        headerRowHeightLines=header_row_height_lines,
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

    # Compile row dimensions
    for row in esql_datatable_chart.rows:
        compiled_row: KbnESQLFieldDimensionColumn = compile_esql_dimension(row)
        kbn_columns.append(compiled_row)
        column_order.append(compiled_row.columnId)

    # Compile rows_by dimensions (split metrics by)
    if esql_datatable_chart.rows_by is not None:
        for rows_by_dim in esql_datatable_chart.rows_by:
            compiled_rows_by: KbnESQLFieldDimensionColumn = compile_esql_dimension(rows_by_dim)
            kbn_columns.append(compiled_rows_by)
            column_order.append(compiled_rows_by.columnId)

    # Build column states
    # Track which columns are metrics - the first len(metrics) columns in order are metrics
    metric_count = len(esql_datatable_chart.metrics)
    metric_column_ids = set(column_order[:metric_count])

    column_states: list[KbnDatatableColumnState] = []
    for column_id in column_order:
        # Determine if this is a metric column or a row column
        is_metric = column_id in metric_column_ids

        # Find user config for this column
        user_config = None
        if is_metric and esql_datatable_chart.metric_columns is not None:
            user_config = next((c for c in esql_datatable_chart.metric_columns if c.column_id == column_id), None)
        elif not is_metric and esql_datatable_chart.columns is not None:
            user_config = next((c for c in esql_datatable_chart.columns if c.column_id == column_id), None)

        # Build column state with summary fields only for metrics
        summary_row = None
        summary_label = None
        if is_metric and isinstance(user_config, DatatableMetricColumnConfig):
            summary_row = user_config.summary_row
            summary_label = user_config.summary_label

        column_state = KbnDatatableColumnState(
            columnId=column_id,
            width=user_config.width if user_config else None,
            hidden=user_config.hidden if user_config and user_config.hidden else None,
            alignment=user_config.alignment if user_config else None,
            colorMode=user_config.color_mode if user_config else None,
            summaryRow=summary_row,
            summaryLabel=summary_label,
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
    # Extract appearance settings if provided, otherwise use defaults
    appearance = esql_datatable_chart.appearance
    row_height_value = None
    header_row_height_value = None
    row_height_lines = None
    header_row_height_lines = None
    density_value = None

    if appearance is not None:
        # Omit default values (auto for row heights, normal for density) to match Kibana defaults
        row_height_value = None if appearance.row_height == DatatableRowHeightEnum.AUTO else appearance.row_height
        header_row_height_value = None if appearance.header_row_height == DatatableRowHeightEnum.AUTO else appearance.header_row_height
        density_value = None if appearance.density == DatatableDensityEnum.NORMAL else appearance.density
        row_height_lines = appearance.row_height_lines
        header_row_height_lines = appearance.header_row_height_lines

    visualization_state = KbnDatatableVisualizationState(
        columns=column_states,
        layerId=layer_id,
        layerType='data',
        sorting=sorting_state,
        rowHeight=row_height_value,
        headerRowHeight=header_row_height_value,
        rowHeightLines=row_height_lines,
        headerRowHeightLines=header_row_height_lines,
        paging=paging_state,
        density=density_value,
    )

    return layer_id, kbn_columns, visualization_state
