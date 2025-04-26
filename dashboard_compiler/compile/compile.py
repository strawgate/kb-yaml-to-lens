from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.controls import BaseControl, OptionsListControl, RangeSliderControl
from dashboard_compiler.models.config.panels.base import BasePanel
from dashboard_compiler.models.config.panels import LensPanel
from dashboard_compiler.models.config.panels.lens_charts.base import BaseLensChart
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric
from dashboard_compiler.models.config.panels.markdown import MarkdownPanel
from dashboard_compiler.models.views.base import KbnGridData, KbnBasePanel
from dashboard_compiler.models.views.dashboard import KbnDashboard, KbnDashboardAttributes, KbnDashboardOptions
from dashboard_compiler.models.config.dashboard import Dashboard
from dashboard_compiler.models.views.panels.controls import (
    KbnBaseControlExplicitInput,
    KbnControl,
    KbnControlGroupInput,
    KbnControlSort,
    KbnOptionsListControlExplicitInput,
    KbnRangeSliderControlExplicitInput,
)
from dashboard_compiler.models.views.panels.lens import KbnColumn
from dashboard_compiler.models.views.panels.markdown import (
    KbnMarkdownEmbeddableConfig,
    KbnMarkdownPanel,
    KbnMarkdownSavedVis,
    KbnMarkdownSavedVisParams,
)


def compile_dashboard_panels(panels: BasePanel) -> list[KbnBasePanel]:
    """
    Compile the panels of a Dashboard object into their Kibana view model representation.

    Args:
        panels (list): The list of panel objects to compile.

    Returns:
        list: The compiled list of Kibana panel view models.
    """
    kbn_panels = []
    for panel in panels:
        if not isinstance(panel, BasePanel):
            raise TypeError(f"Panel {panel} is not supported in the dashboard compilation.")

        panel_index = stable_id_generator([panel.type, panel.title, str(panel.grid)])

        grid_data = KbnGridData(x=panel.grid.x, y=panel.grid.y, w=panel.grid.w, h=panel.grid.h, i=panel_index)

        if isinstance(panel, MarkdownPanel):
            kbn_panels.append(
                KbnMarkdownPanel(
                    type="visualization",
                    panelIndex=panel_index,
                    gridData=grid_data,
                    embeddableConfig=KbnMarkdownEmbeddableConfig(
                        savedVis=KbnMarkdownSavedVis(
                            id=panel_index,
                            title=panel.title,
                            description=panel.description,
                            type="markdown",
                            params=KbnMarkdownSavedVisParams(fontSize=12, openLinksInNewTab=False, markdown=panel.content),
                        )
                    ),
                )
            )

        if isinstance(panel, LensPanel):
            dimensions_by_id = {}
            metrics_by_id = {}
            metrics_by_name = {}
            columns_by_id = {}

            chart: BaseLensChart = panel.chart

            if hasattr(chart, "metrics") and chart.metrics:
                chart_metrics: list[Metric] = chart.metrics

                for metric in chart_metrics:
                    id = stable_id_generator([metric.type, metric.label, metric.field])

                    metrics_by_id[id] = KbnColumn(
                        label=metric.label,
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

            if hasattr(chart, "dimensions") and chart.dimensions:
                chart_dimensions: list[Dimension] = chart.dimensions

                for dimension in chart_dimensions:
                    id = stable_id_generator([dimension.type, dimension.label, dimension.field])

                    dimensions_by_id[id] = KbnColumn(
                        label=dimension.label,
                        dataType="string",
                        operationType=dimension.type,
                        scale="ordinal",
                        sourceField=dimension.field,
                        isBucketed=True,
                        params={
                            "size": dimension.size,
                            "orderBy": {"type": "column", "columnId": metrics_by_name[dimension.sort.by]},
                            "orderDirection": dimension.sort.direction if dimension.sort else "asc",
                            "otherBucket": True,
                            "missingBucket": True,
                            "parentFormat": {
                                "id": dimension.type,
                            },
                            "include": [],
                            "exclude": [],
                            "includeIsRegex": False,
                            "excludeIsRegex": False,
                        },
                    )

            all_columns_by_id = {**dimensions_by_id, **metrics_by_id, **columns_by_id}

            if panel.chart.type == "pie":
                pass
                # KbnPieChart

        # kbn_panels.append(
        #     KbnLensChartPanel(

        #     )

    return kbn_panels


def compile_dashboard_options(dashboard: Dashboard) -> KbnDashboardOptions:
    """
    Compile the options of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboardOptions: The compiled Kibana dashboard options view model.
    """

    return KbnDashboardOptions(
        useMargins=True,
        syncColors=True,
        syncCursor=True,
        syncTooltips=True,
        hidePanelTitles=False,
    )


def compile_control_group_input(dashboard: Dashboard) -> KbnControlGroupInput:
    """
    Compile the control group input for a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnControlGroupInput: The compiled Kibana control group input view model.
    """

    controls: dict[str, KbnBaseControlExplicitInput] = {}

    for i, control in enumerate(dashboard.controls):
        control_index = stable_id_generator([control.type, control.label, control.data_view, control.field])

        new_control: BaseControl
        new_type: str

        if isinstance(control, OptionsListControl):
            sort = KbnControlSort(by=control.sort.by, direction=control.sort.direction) if control.sort else None

            new_type = "optionsListControl"

            new_control = KbnOptionsListControlExplicitInput(
                dataViewId=control.data_view,
                fieldName=control.field,
                searchTechnique=control.search_technique or "prefix",
                selectedOptions=[],
                sort=sort,
            )

        elif isinstance(control, RangeSliderControl):
            new_type = "rangeSliderControl"

            new_control = KbnRangeSliderControlExplicitInput(dataViewId=control.data_view, fieldName=control.field, step=control.step)

        controls[control_index] = KbnControl(grow=True, order=i, type=new_type, width=control.width, explicitInput=new_control)

    return KbnControlGroupInput(
        chainingSystem="HIERARCHICAL",
        controlStyle="oneLine",
        ignoreParentSettingsJSON='{"ignoreFilters":false,"ignoreQuery":false,"ignoreTimerange":false,"ignoreValidations":false}',
        panelsJSON=controls,
        showApplySelections=False,
    )


def compile_dashboard_attributes(dashboard: Dashboard) -> KbnDashboardAttributes:
    """
    Compile the attributes of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboardAttributes: The compiled Kibana dashboard attributes view model.
    """

    return KbnDashboardAttributes(
        title=dashboard.title,
        description=dashboard.description,
        panelsJSON=compile_dashboard_panels(dashboard.panels),
        optionsJSON=compile_dashboard_options(dashboard),
        timeRestore=False,
        version=1,
        controlGroupInput=compile_control_group_input(dashboard),
    )


def compile_dashboard(dashboard: Dashboard) -> KbnDashboard:
    """
    Compile a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboard: The compiled Kibana dashboard view model.
    """
    # Create the KbnDashboard view model
    kbn_dashboard = KbnDashboard(
        attributes=compile_dashboard_attributes(dashboard),
        coreMigrationVersion="8.0.0",
        created_at="2023-10-01T00:00:00Z",
        created_by="admin",
        id=dashboard.id,
        managed=False,
        references=[],
        type="dashboard",
        typeMigrationVersion="8.0.0",
        updated_at="2023-10-01T00:00:00Z",
        updated_by="admin",
        version="1",
    )

    return kbn_dashboard
