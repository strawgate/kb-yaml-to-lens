from typing import TYPE_CHECKING

from kb_dashboard_core.panels.charts.base.compile import compile_color_range_mapping
from kb_dashboard_core.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric

if TYPE_CHECKING:
    from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLFieldDimensionColumn

from kb_dashboard_core.panels.charts.datatable.appearance import (
    DatatableColumnAppearanceMixin,
    DatatableMetricAppearanceMixin,
)
from kb_dashboard_core.panels.charts.datatable.breakdowns import (
    ESQLDatatableBreakdownTypes,
    LensDatatableBreakdownTypes,
)
from kb_dashboard_core.panels.charts.datatable.config import (
    DatatableAppearance,
    DatatableDensityEnum,
    DatatablePagingConfig,
    DatatableRowHeightEnum,
    DatatableSortingConfig,
    ESQLDatatableChart,
    LensDatatableChart,
)
from kb_dashboard_core.panels.charts.datatable.dimensions import (
    ESQLDatatableDimensionTypes,
    LensDatatableDimensionTypes,
)
from kb_dashboard_core.panels.charts.datatable.metrics import (
    ESQLDatatableMetricTypes,
    LensDatatableMetricTypes,
)
from kb_dashboard_core.panels.charts.datatable.view import (
    KbnDatatableColumnState,
    KbnDatatablePagingState,
    KbnDatatableSortingState,
    KbnDatatableVisualizationState,
)
from kb_dashboard_core.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from kb_dashboard_core.panels.charts.esql.columns.view import KbnESQLColumnTypes
from kb_dashboard_core.panels.charts.lens.breakdowns.config import LensBreakdownTypes
from kb_dashboard_core.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensMetricColumnTypes,
)
from kb_dashboard_core.panels.charts.lens.dimensions.compile import compile_lens_dimension
from kb_dashboard_core.panels.charts.lens.dimensions.config import LensDimensionTypes
from kb_dashboard_core.panels.charts.lens.metrics.compile import compile_lens_metric
from kb_dashboard_core.panels.charts.lens.metrics.config import LensMetricTypes


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


def _build_datatable_column_state(
    column_id: str,
    is_metric: bool,
    config: (
        LensDatatableBreakdownTypes
        | LensBreakdownTypes
        | LensDatatableDimensionTypes
        | LensDimensionTypes
        | ESQLDatatableBreakdownTypes
        | ESQLDimensionTypes
        | LensDatatableMetricTypes
        | LensMetricTypes
        | ESQLDatatableMetricTypes
        | ESQLMetricTypes
    ),
    is_transposed: bool = False,
) -> KbnDatatableColumnState:
    metric_appearance = config.appearance if is_metric and isinstance(config, DatatableMetricAppearanceMixin) else None
    if metric_appearance is not None:
        column_appearance = metric_appearance
    elif isinstance(config, DatatableColumnAppearanceMixin):
        column_appearance = config.appearance
    else:
        column_appearance = None

    summary_row = metric_appearance.summary_row if metric_appearance is not None else None
    summary_label = metric_appearance.summary_label if metric_appearance is not None else None
    metric_color = metric_appearance.color if metric_appearance is not None else None
    palette = compile_color_range_mapping(metric_color.to_range_mapping()) if metric_color is not None else None
    hidden = column_appearance.hidden if column_appearance is not None else False
    one_click_filter = column_appearance.one_click_filter if column_appearance is not None else False
    color_mode = metric_color.apply_to if metric_color is not None else None

    return KbnDatatableColumnState(
        columnId=column_id,
        width=column_appearance.width if column_appearance is not None else None,
        hidden=hidden if hidden is True else None,
        isTransposed=is_transposed,
        isMetric=is_metric,
        oneClickFilter=one_click_filter if one_click_filter is True else None,
        alignment=column_appearance.alignment if column_appearance is not None else None,
        colorMode=color_mode,
        summaryRow=summary_row,
        summaryLabel=summary_label,
        palette=palette,
    )


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
    layer_id = lens_datatable_chart.get_id()
    kbn_columns_by_id: dict[str, KbnLensColumnTypes] = {}
    datatable_columns: list[
        tuple[
            str,
            bool,
            LensDatatableBreakdownTypes
            | LensBreakdownTypes
            | LensDatatableDimensionTypes
            | LensDimensionTypes
            | LensDatatableMetricTypes
            | LensMetricTypes,
            bool,
        ]
    ] = []

    # Compile metrics first (for dimension compilation to reference)
    kbn_metric_columns_by_id: dict[str, KbnLensMetricColumnTypes] = {}
    primary_metric_ids: list[str] = []
    for metric in lens_datatable_chart.metrics:
        result = compile_lens_metric(metric)
        metric_id = result.primary_id
        compiled_metric = result.primary_column
        kbn_metric_columns_by_id[metric_id] = compiled_metric
        kbn_metric_columns_by_id.update(result.helper_columns)
        primary_metric_ids.append(metric_id)

    # Compile breakdowns (these come FIRST in column order for datatables)
    for dimension in lens_datatable_chart.breakdowns:
        dimension_id, compiled_dimension = compile_lens_dimension(
            dimension=dimension,
            kbn_metric_column_by_id=kbn_metric_columns_by_id,
        )
        kbn_columns_by_id[dimension_id] = compiled_dimension
        datatable_columns.append((dimension_id, False, dimension, False))

    # Compile metrics_split_by dimensions
    if lens_datatable_chart.metrics_split_by is not None:
        for metrics_split_by_dim in lens_datatable_chart.metrics_split_by:
            metrics_split_by_id, compiled_metrics_split_by = compile_lens_dimension(
                dimension=metrics_split_by_dim,
                kbn_metric_column_by_id=kbn_metric_columns_by_id,
            )
            kbn_columns_by_id[metrics_split_by_id] = compiled_metrics_split_by
            datatable_columns.append((metrics_split_by_id, False, metrics_split_by_dim, True))

    # Add all metric columns (including helper columns) to kbn_columns_by_id
    # but only add primary metric IDs to datatable columns (helper columns are not visible)
    kbn_columns_by_id.update(kbn_metric_columns_by_id)
    datatable_columns.extend((mid, True, m, False) for mid, m in zip(primary_metric_ids, lens_datatable_chart.metrics, strict=True))
    column_states = [
        _build_datatable_column_state(column_id=column_id, is_metric=is_metric, config=config, is_transposed=is_transposed)
        for column_id, is_metric, config, is_transposed in datatable_columns
    ]

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
    layer_id = esql_datatable_chart.get_id()
    kbn_columns: list[KbnESQLColumnTypes] = []
    datatable_columns: list[
        tuple[
            str,
            bool,
            ESQLDatatableBreakdownTypes | ESQLDimensionTypes | ESQLDatatableDimensionTypes | ESQLDatatableMetricTypes | ESQLMetricTypes,
            bool,
        ]
    ] = []

    # Compile metrics first (to store for later, but don't add to kbn_columns yet)
    compiled_metrics: list[KbnESQLColumnTypes] = []
    metric_column_ids: list[str] = []
    for metric in esql_datatable_chart.metrics:
        compiled_metric = compile_esql_metric(metric)
        compiled_metrics.append(compiled_metric)
        metric_column_ids.append(compiled_metric.columnId)

    # Compile breakdowns (these come FIRST in column order for datatables)
    for dimension in esql_datatable_chart.breakdowns:
        compiled_dimension: KbnESQLFieldDimensionColumn = compile_esql_dimension(dimension)
        kbn_columns.append(compiled_dimension)
        datatable_columns.append((compiled_dimension.columnId, False, dimension, False))

    # Compile metrics_split_by dimensions
    if esql_datatable_chart.metrics_split_by is not None:
        for metrics_split_by_dim in esql_datatable_chart.metrics_split_by:
            compiled_metrics_split_by: KbnESQLFieldDimensionColumn = compile_esql_dimension(metrics_split_by_dim)
            kbn_columns.append(compiled_metrics_split_by)
            datatable_columns.append((compiled_metrics_split_by.columnId, False, metrics_split_by_dim, True))

    # Add metrics to kbn_columns AFTER dimensions
    kbn_columns.extend(compiled_metrics)
    datatable_columns.extend((mid, True, m, False) for mid, m in zip(metric_column_ids, esql_datatable_chart.metrics, strict=True))
    column_states = [
        _build_datatable_column_state(column_id=column_id, is_metric=is_metric, config=config, is_transposed=is_transposed)
        for column_id, is_metric, config, is_transposed in datatable_columns
    ]

    visualization_state = _build_datatable_visualization_state(
        column_states=column_states,
        layer_id=layer_id,
        sorting=esql_datatable_chart.sorting,
        paging=esql_datatable_chart.paging,
        appearance=esql_datatable_chart.appearance,
    )

    return layer_id, kbn_columns, visualization_state
