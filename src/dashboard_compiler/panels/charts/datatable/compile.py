from typing import TYPE_CHECKING

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.view import KbnESQLFieldDimensionColumn

from dashboard_compiler.panels.charts.datatable.config import (
    DatatableAppearance,
    DatatableColumnConfig,
    DatatableDensityEnum,
    DatatableMetricColumnConfig,
    DatatablePagingConfig,
    DatatableRowHeightEnum,
    DatatableSortingConfig,
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
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.shared.config import get_layer_id


def _build_datatable_visualization_state(
    column_states: list[KbnDatatableColumnState],
    layer_id: str,
    sorting: DatatableSortingConfig | None,
    paging: DatatablePagingConfig | None,
    appearance: DatatableAppearance | None,
) -> KbnDatatableVisualizationState:
    """Build the visualization state for a datatable.

    Args:
        column_states: List of compiled column states
        layer_id: The layer ID
        sorting: Optional sorting configuration
        paging: Optional paging configuration
        appearance: Optional appearance configuration

    Returns:
        The compiled visualization state

    """
    sorting_state = None
    if sorting is not None:
        sorting_state = KbnDatatableSortingState(
            columnId=sorting.column_id,
            direction=sorting.direction,
        )

    paging_state = None
    if paging is not None:
        paging_state = KbnDatatablePagingState(
            size=paging.page_size,
            enabled=paging.enabled,
        )

    row_height_value = None
    header_row_height_value = None
    row_height_lines = None
    header_row_height_lines = None
    density_value = None

    if appearance is not None:
        row_height_value = None if appearance.row_height == DatatableRowHeightEnum.AUTO else appearance.row_height
        header_row_height_value = None if appearance.header_row_height == DatatableRowHeightEnum.AUTO else appearance.header_row_height
        density_value = None if appearance.density == DatatableDensityEnum.NORMAL else appearance.density
        row_height_lines = appearance.row_height_lines
        header_row_height_lines = appearance.header_row_height_lines

    return KbnDatatableVisualizationState(
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


def _build_datatable_column_states(
    column_order: list[str],
    metric_columns_ids: set[str],
    metric_columns_config: list[DatatableMetricColumnConfig] | None,
    row_columns_config: list[DatatableColumnConfig] | None,
) -> list[KbnDatatableColumnState]:
    """Build column states for a datatable visualization.

    Args:
        column_order: Ordered list of column IDs
        metric_columns_ids: Set of metric column IDs
        metric_columns_config: User configuration for metric columns
        row_columns_config: User configuration for row columns

    Returns:
        List of compiled column states

    """
    column_states: list[KbnDatatableColumnState] = []
    for column_id in column_order:
        is_metric = column_id in metric_columns_ids

        user_config = None
        if is_metric and metric_columns_config is not None:
            user_config = next((c for c in metric_columns_config if c.column_id == column_id), None)
        elif not is_metric and row_columns_config is not None:
            user_config = next((c for c in row_columns_config if c.column_id == column_id), None)

        summary_row = None
        summary_label = None
        if is_metric and isinstance(user_config, DatatableMetricColumnConfig):
            summary_row = user_config.summary_row
            summary_label = user_config.summary_label

        column_state = KbnDatatableColumnState(
            columnId=column_id,
            width=user_config.width if user_config is not None else None,
            hidden=user_config.hidden if user_config is not None and user_config.hidden is True else None,
            isTransposed=False,
            isMetric=is_metric,
            alignment=user_config.alignment if user_config is not None else None,
            colorMode=user_config.color_mode if user_config is not None else None,
            summaryRow=summary_row,
            summaryLabel=summary_label,
        )
        column_states.append(column_state)

    return column_states


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
    layer_id = get_layer_id(lens_datatable_chart)
    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {}
    column_order: list[str] = []

    # Compile metrics first (for dimension compilation to reference)
    kbn_metric_columns_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    for metric in lens_datatable_chart.metrics:
        metric_id, compiled_metric = compile_lens_metric(metric)
        kbn_metric_columns_by_id[metric_id] = compiled_metric

    # Compile row dimensions (these come FIRST in column order for datatables)
    for row in lens_datatable_chart.rows:
        row_id, compiled_row = compile_lens_dimension(
            dimension=row,
            kbn_metric_column_by_id=kbn_metric_columns_by_id,
        )
        kbn_columns_by_id[row_id] = compiled_row
        column_order.append(row_id)

    # Compile rows_by dimensions (split metrics by)
    if lens_datatable_chart.rows_by is not None:
        for rows_by_dim in lens_datatable_chart.rows_by:
            rows_by_id, compiled_rows_by = compile_lens_dimension(
                dimension=rows_by_dim,
                kbn_metric_column_by_id=kbn_metric_columns_by_id,
            )
            kbn_columns_by_id[rows_by_id] = compiled_rows_by
            column_order.append(rows_by_id)

    # Add metrics to kbn_columns_by_id AFTER dimensions (preserves insertion order)
    for metric_id, compiled_metric in kbn_metric_columns_by_id.items():
        kbn_columns_by_id[metric_id] = compiled_metric
        column_order.append(metric_id)

    # Build column states
    column_states = _build_datatable_column_states(
        column_order=column_order,
        metric_columns_ids=set(kbn_metric_columns_by_id.keys()),
        metric_columns_config=lens_datatable_chart.metric_columns,
        row_columns_config=lens_datatable_chart.columns,
    )

    visualization_state = _build_datatable_visualization_state(
        column_states=column_states,
        layer_id=layer_id,
        sorting=lens_datatable_chart.sorting,
        paging=lens_datatable_chart.paging,
        appearance=lens_datatable_chart.appearance,
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
    layer_id = get_layer_id(esql_datatable_chart)
    kbn_columns: list[KbnESQLColumnTypes] = []
    column_order: list[str] = []

    # Compile metrics first (to store for later, but don't add to kbn_columns yet)
    compiled_metrics: list[KbnESQLColumnTypes] = []
    metric_column_ids: list[str] = []
    for metric in esql_datatable_chart.metrics:
        compiled_metric = compile_esql_metric(metric)
        compiled_metrics.append(compiled_metric)
        metric_column_ids.append(compiled_metric.columnId)

    # Compile row dimensions (these come FIRST in column order for datatables)
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

    # Add metrics to kbn_columns AFTER dimensions
    kbn_columns.extend(compiled_metrics)
    column_order.extend(metric_column_ids)

    # Build column states
    column_states = _build_datatable_column_states(
        column_order=column_order,
        metric_columns_ids=set(metric_column_ids),
        metric_columns_config=esql_datatable_chart.metric_columns,
        row_columns_config=esql_datatable_chart.columns,
    )

    visualization_state = _build_datatable_visualization_state(
        column_states=column_states,
        layer_id=layer_id,
        sorting=esql_datatable_chart.sorting,
        paging=esql_datatable_chart.paging,
        appearance=esql_datatable_chart.appearance,
    )

    return layer_id, kbn_columns, visualization_state
