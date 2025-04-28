
import yaml

from dashboard_compiler.compile.panels.lens import compile_lens_panel
from dashboard_compiler.compile.panels.links import compile_links_panel
from dashboard_compiler.compile.panels.markdown import compile_markdown_panel
from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.controls import BaseControl, OptionsListControl, RangeSliderControl
from dashboard_compiler.models.config.dashboard import Dashboard
from dashboard_compiler.models.config.panels import LensPanel
from dashboard_compiler.models.config.panels.base import BasePanel
from dashboard_compiler.models.config.panels.links import LinksPanel
from dashboard_compiler.models.config.panels.markdown import MarkdownPanel
from dashboard_compiler.models.config.shared import (
    BaseFilter,
    BaseQuery,
    ExistsFilter,
    KqlQuery,
    LuceneQuery,
    NegationFilter,
    PhraseFilter,
    PhrasesFilter,
    RangeFilter,
)
from dashboard_compiler.models.views.base import KbnBasePanel, KbnFilter, KbnQuery, KbnSavedObjectMeta, KbnSearchSourceJSON
from dashboard_compiler.models.views.dashboard import KbnDashboard, KbnDashboardAttributes, KbnDashboardOptions
from dashboard_compiler.models.views.panels.controls import (
    KbnBaseControlExplicitInput,
    KbnControl,
    KbnControlGroupInput,
    KbnControlSort,
    KbnOptionsListControlExplicitInput,
    KbnRangeSliderControlExplicitInput,
)
from dashboard_compiler.models.views.panels.lens import KbnReference


def convert_to_panel_reference(kbn_reference: KbnReference, panel_index: str) -> KbnReference:
    """
    Convert a KbnReference object to a panel reference.

    Args:
        kbn_reference (KbnReference): The KbnReference object to convert.

    Returns:
        KbnReference: The converted panel reference.
    """
    return KbnReference(
        type=kbn_reference.type,
        id=kbn_reference.id,
        name=panel_index + ":" + kbn_reference.name,
    )


def compile_dashboard_panels(panels: BasePanel) -> tuple[list[KbnReference], list[KbnBasePanel]]:
    """
    Compile the panels of a Dashboard object into their Kibana view model representation.

    Args:
        panels (list): The list of panel objects to compile.

    Returns:
        list: The compiled list of Kibana panel view models.
    """
    kbn_panels = []
    kbn_references = []
    for panel in panels:
        if not isinstance(panel, BasePanel):
            raise TypeError(f"Panel {panel} is not supported in the dashboard compilation.")

        new_references: list[KbnReference] = []
        kbn_panel: KbnBasePanel

        if isinstance(panel, MarkdownPanel):
            kbn_panel = compile_markdown_panel(panel)

        if isinstance(panel, LensPanel):
            new_references, kbn_panel = compile_lens_panel(panel)

        if isinstance(panel, LinksPanel):
            new_references, kbn_panel = compile_links_panel(panel)

        kbn_panels.append(kbn_panel)
        kbn_references.extend([convert_to_panel_reference(ref, kbn_panel.panelIndex) for ref in new_references])

    #         dimensions_by_id = {}
    #         metrics_by_id = {}
    #         metrics_by_name = {}
    #         columns_by_id = {}

    #         chart: BaseLensChart = panel.chart

    #         if hasattr(chart, "metrics") and chart.metrics:
    #             chart_metrics: list[Metric] = chart.metrics

    #             for metric in chart_metrics:
    #                 id = stable_id_generator([metric.type, metric.label, metric.field])

    #                 metrics_by_id[id] = KbnColumn(
    #                     label=metric.label,
    #                     dataType="number",
    #                     operationType=metric.type,
    #                     scale="ratio",
    #                     sourceField=metric.field,
    #                     isBucketed=False,
    #                     params={
    #                         "emptyAsNull": True,
    #                     },
    #                 )

    #                 metrics_by_name[metric.label] = id

    #         if hasattr(chart, "dimensions") and chart.dimensions:
    #             chart_dimensions: list[Dimension] = chart.dimensions

    #             for dimension in chart_dimensions:
    #                 id = stable_id_generator([dimension.type, dimension.label, dimension.field])

    #                 dimensions_by_id[id] = KbnColumn(
    #                     label=dimension.label,
    #                     dataType="string",
    #                     operationType=dimension.type,
    #                     scale="ordinal",
    #                     sourceField=dimension.field,
    #                     isBucketed=True,
    #                     params={
    #                         "size": dimension.size,
    #                         "orderBy": {"type": "column", "columnId": metrics_by_name[dimension.sort.by]},
    #                         "orderDirection": dimension.sort.direction if dimension.sort else "asc",
    #                         "otherBucket": True,
    #                         "missingBucket": True,
    #                         "parentFormat": {
    #                             "id": dimension.type,
    #                         },
    #                         "include": [],
    #                         "exclude": [],
    #                         "includeIsRegex": False,
    #                         "excludeIsRegex": False,
    #                     },
    #                 )

    #         all_columns_by_id = {**dimensions_by_id, **metrics_by_id, **columns_by_id}

    #         if panel.chart.type == "pie":
    #             pass
    #             # KbnPieChart

    #     # kbn_panels.append(
    #     #     KbnLensChartPanel(

    #     #     )

    return kbn_references, kbn_panels


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
        control_index = control.id or stable_id_generator([control.type, control.label, control.data_view, control.field])

        new_control: BaseControl
        new_type: str

        if isinstance(control, OptionsListControl):
            sort = KbnControlSort(by=control.sort.by, direction=control.sort.direction) if control.sort else None

            new_type = "optionsListControl"

            new_control = KbnOptionsListControlExplicitInput(
                dataViewId=control.data_view,
                fieldName=control.field,
                title=control.label,
                searchTechnique=control.search_technique or "prefix",
                selectedOptions=[],
                sort=sort,
            )

        elif isinstance(control, RangeSliderControl):
            new_type = "rangeSliderControl"

            new_control = KbnRangeSliderControlExplicitInput(
                dataViewId=control.data_view, fieldName=control.field, step=control.step, title=control.label
            )

        controls[control_index] = KbnControl(grow=True, order=i, type=new_type, width=control.width, explicitInput=new_control)

    return KbnControlGroupInput(
        chainingSystem="HIERARCHICAL",
        controlStyle="oneLine",
        ignoreParentSettingsJSON='{"ignoreFilters":false,"ignoreQuery":false,"ignoreTimerange":false,"ignoreValidations":false}',
        panelsJSON=controls,
        showApplySelections=False,
    )


def compile_dashboard_query(query: BaseQuery) -> KbnQuery:
    """
    Compile the query of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnQuery: The compiled Kibana query view model.
    """
    if isinstance(query, KqlQuery):
        return KbnQuery(
            query=query.kql,
            language="kuery",
        )
    elif isinstance(query, LuceneQuery):
        return KbnQuery(
            query=query.lucene,
            language="lucene",
        )

    else:
        raise ValueError(f"Unsupported query type: {type(query)}. Supported types are Kql or Lucene.")


def compile_dashboard_filter(filter: BaseFilter, negate: bool = False) -> KbnFilter:
    """
    Compile a single Filter object into its Kibana view model representation.

    Args:
        filter (Filter): The Filter object to compile.

    Returns:
        KbnFilter: The compiled Kibana filter view model.
    """

    base_meta = {
        "field": filter.field,
        "key": filter.field,
        "disabled": False,
        "negate": False,
        "alias": None,
    }

    if isinstance(filter, NegationFilter):
        return compile_dashboard_filter(filter.not_filter, negate=True)

    if isinstance(filter, ExistsFilter):
        return KbnFilter(meta={"type": "exists", **base_meta}, query={"exists": {"field": filter.field}})

    if isinstance(filter, PhraseFilter):
        return KbnFilter(
            meta={"type": "phrase", "params": {"query": filter.equals}, **base_meta},
            query={"match_phrase": {filter.field: filter.equals}},
        )

    if isinstance(filter, PhrasesFilter):
        return KbnFilter(
            meta={"type": "phrases", "params": list(filter.in_list), **base_meta},
            query={"bool": {"minimum_should_match": 1, "should": [{"match_phrase": {filter.field: value}} for value in filter.in_list]}},
        )

    if isinstance(filter, RangeFilter):
        range_query = {}

        if filter.gte is not None:
            range_query["gte"] = filter.gte
        if filter.lte is not None:
            range_query["lte"] = filter.lte
        if filter.gt is not None:
            range_query["gt"] = filter.gt
        if filter.lt is not None:
            range_query["lt"] = filter.lt

        return KbnFilter(
            meta={
                "type": "range",
                "params": {
                    "gte": filter.gte,
                    "lte": filter.lte,
                    "gt": filter.gt,
                    "lt": filter.lt,
                },
                **base_meta,
            },
            query={"range": {filter.field: range_query}},
        )


def compile_dashboard_filters(filters: list[BaseFilter]) -> list[KbnFilter]:
    """
    Compile the filters of a Dashboard object into its Kibana view model representation.

    Args:
        filters (list[BaseFilter]): The list of filter objects to compile.

    Returns:
        list[KbnFilter]: The compiled list of Kibana filter view models.
    """

    return [compile_dashboard_filter(filter) for filter in filters]


def compile_dashboard_attributes(dashboard: Dashboard) -> tuple[list[KbnReference], KbnDashboardAttributes]:
    """
    Compile the attributes of a Dashboard object into its Kibana view model representation.

    Args:
        dashboard (Dashboard): The Dashboard object to compile.

    Returns:
        KbnDashboardAttributes: The compiled Kibana dashboard attributes view model.
    """

    references, panels = compile_dashboard_panels(dashboard.panels)

    return references, KbnDashboardAttributes(
        title=dashboard.title,
        description=dashboard.description,
        panelsJSON=panels,
        kibanaSavedObjectMeta=KbnSavedObjectMeta(
            searchSourceJSON=KbnSearchSourceJSON(
                filter=compile_dashboard_filters(dashboard.filters),
                query=compile_dashboard_query(dashboard.query),
            )
        ),
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
    id = dashboard.id or stable_id_generator([dashboard.title])

    references, attributes = compile_dashboard_attributes(dashboard)

    # Create the KbnDashboard view model
    kbn_dashboard = KbnDashboard(
        attributes=attributes,
        coreMigrationVersion="8.8.0",
        created_at="2023-10-01T00:00:00Z",
        created_by="admin",
        id=id,
        managed=False,
        references=references,
        type="dashboard",
        typeMigrationVersion="10.2.0",
        updated_at="2023-10-01T00:00:00Z",
        updated_by="admin",
        version="1",
    )

    return kbn_dashboard


def compile_dashboards(dashboards: list[Dashboard]) -> list[KbnDashboard]:
    """
    Compile a list of Dashboard objects into their Kibana view model representations.

    Args:
        dashboards (list[Dashboard]): The list of Dashboard objects to compile.

    Returns:
        list[KbnDashboard]: The compiled list of Kibana dashboard view models.
    """
    return [compile_dashboard(dashboard) for dashboard in dashboards]


def compile_yaml_dashboards(yaml_path: str) -> list[KbnDashboard]:
    """
    Compile a YAML dashboard configuration file into its Kibana view model representation.

    Args:
        yaml_path (str): The path to the YAML dashboard configuration file.

    Returns:
        KbnDashboard: The compiled Kibana dashboard view model.
    """
    # Load the YAML file and create a Dashboard object
    dashboard_dict = yaml.safe_load(open(yaml_path))

    dashboards = [Dashboard(**dashboard) for dashboard in dashboard_dict["dashboards"]]

    # Compile the Dashboard object into its Kibana view model
    return compile_dashboards(dashboards)


def compile_yaml_dashboard(yaml_path: str) -> KbnDashboard:
    """
    Compile a YAML dashboard configuration file into its Kibana view model representation.

    Args:
        yaml_path (str): The path to the YAML dashboard configuration file.

    Returns:
        KbnDashboard: The compiled Kibana dashboard view model.
    """
    # Load the YAML file and create a Dashboard object
    dashboard_dict = yaml.safe_load(open(yaml_path))

    dashboard = Dashboard(**dashboard_dict["dashboard"])

    # Compile the Dashboard object into its Kibana view model
    return compile_dashboard(dashboard)
