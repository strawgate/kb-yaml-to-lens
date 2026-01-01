"""Compile Control configurations into Kibana view models."""

from collections.abc import Sequence

from dashboard_compiler.controls import ControlTypes
from dashboard_compiler.controls.config import (
    ControlSettings,
    ESQLQueryControl,
    ESQLStaticValuesControl,
    MatchTechnique,
    OptionsListControl,
    RangeSliderControl,
    TimeSliderControl,
)
from dashboard_compiler.controls.types import EsqlControlType
from dashboard_compiler.controls.view import (
    KBN_DEFAULT_CONTROL_WIDTH,
    ChainingSystemEnum,
    ControlStyleEnum,
    KbnControlGroupInput,
    KbnControlPanelsJson,
    KbnControlSort,
    KbnControlTypes,
    KbnESQLControl,
    KbnESQLControlExplicitInput,
    KbnIgnoreParentSettingsJson,
    KbnOptionsListControl,
    KbnOptionsListControlExplicitInput,
    KbnRangeSliderControl,
    KbnRangeSliderControlExplicitInput,
    KbnTimeSliderControl,
    KbnTimeSliderControlExplicitInput,
    SearchTechnique,
)
from dashboard_compiler.shared.compile import return_if, return_if_equals
from dashboard_compiler.shared.defaults import default_false, default_if_none
from dashboard_compiler.shared.id_utils import generate_id


def compile_options_list_control(order: int, *, control: OptionsListControl) -> KbnOptionsListControl:
    """Compile an OptionsListControl into its Kibana view model representation.

    Args:
        order (int): The order of the control in the dashboard.
        control (OptionsListControl): The OptionsListControl object to compile.

    Returns:
        KbnOptionsListControl: The compiled Kibana options list control view model.

    """
    match_technique_to_search_technique: dict[MatchTechnique | None, SearchTechnique] = {
        MatchTechnique.PREFIX: SearchTechnique.PREFIX,
        MatchTechnique.CONTAINS: SearchTechnique.WILDCARD,
        MatchTechnique.EXACT: SearchTechnique.EXACT,
    }
    stable_id = generate_id(control.id)

    return KbnOptionsListControl(
        grow=default_false(control.fill_width),
        order=order,
        width=default_if_none(control.width, KBN_DEFAULT_CONTROL_WIDTH),
        explicitInput=KbnOptionsListControlExplicitInput(
            id=stable_id,
            dataViewId=control.data_view,
            fieldName=control.field,
            title=control.label,
            runPastTimeout=control.wait_for_results or None,
            singleSelect=control.singular or None,
            searchTechnique=match_technique_to_search_technique.get(control.match_technique, SearchTechnique.PREFIX),
            selectedOptions=[],
            sort=KbnControlSort(by='_count', direction='desc'),
        ),
    )


def compile_range_slider_control(order: int, *, control: RangeSliderControl) -> KbnRangeSliderControl:
    """Compile a RangeSliderControl into its Kibana view model representation.

    Args:
        order (int): The order of the control in the dashboard.
        control (RangeSliderControl): The RangeSliderControl object to compile.

    Returns:
        KbnRangeSliderControl: The compiled Kibana range slider control view model.

    """
    stable_id = generate_id(control.id)

    return KbnRangeSliderControl(
        grow=default_false(control.fill_width),
        order=order,
        width=default_if_none(control.width, 'medium'),
        explicitInput=KbnRangeSliderControlExplicitInput(
            id=stable_id,
            dataViewId=control.data_view,
            fieldName=control.field,
            step=default_if_none(control.step, 1),
            title=control.label,
        ),
    )


def compile_time_slider_control(order: int, *, control: TimeSliderControl) -> KbnTimeSliderControl:
    """Compile a TimeSliderControl into its Kibana view model representation.

    Args:
        order (int): The order of the control in the dashboard.
        control (TimeSliderControl): The TimeSliderControl object to compile.

    Returns:
        KbnTimeSliderControl: The compiled Kibana time slider control view model.

    """
    stable_id = generate_id(control.id)

    return KbnTimeSliderControl(
        grow=True,
        order=order,
        width=default_if_none(control.width, 'medium'),
        explicitInput=KbnTimeSliderControlExplicitInput(
            id=stable_id,
            timesliceEndAsPercentageOfTimeRange=default_if_none(control.end_offset, 100.0),
            timesliceStartAsPercentageOfTimeRange=default_if_none(control.start_offset, 0.0),
        ),
    )


def compile_esql_static_control(order: int, *, control: ESQLStaticValuesControl) -> KbnESQLControl:
    """Compile an ESQLStaticValuesControl into its Kibana view model representation.

    Args:
        order (int): The order of the control in the dashboard.
        control (ESQLStaticValuesControl): The ESQLStaticValuesControl object to compile.

    Returns:
        KbnESQLControl: The compiled Kibana ES|QL control view model.

    """
    stable_id = generate_id(control.id)

    return KbnESQLControl(
        grow=False,
        order=order,
        width=default_if_none(control.width, 'medium'),
        explicitInput=KbnESQLControlExplicitInput(
            id=stable_id,
            variableName=control.variable_name,
            variableType=control.variable_type,
            esqlQuery='',
            controlType=EsqlControlType.STATIC_VALUES.value,
            title=control.title,
            selectedOptions=[],
            singleSelect=control.single_select or None,
            availableOptions=control.available_options,
        ),
    )


def compile_esql_query_control(order: int, *, control: ESQLQueryControl) -> KbnESQLControl:
    """Compile an ESQLQueryControl into its Kibana view model representation.

    Args:
        order (int): The order of the control in the dashboard.
        control (ESQLQueryControl): The ESQLQueryControl object to compile.

    Returns:
        KbnESQLControl: The compiled Kibana ES|QL control view model.

    """
    stable_id = generate_id(control.id)

    return KbnESQLControl(
        grow=False,
        order=order,
        width=default_if_none(control.width, 'medium'),
        explicitInput=KbnESQLControlExplicitInput(
            id=stable_id,
            variableName=control.variable_name,
            variableType=control.variable_type,
            esqlQuery=control.esql_query,
            controlType=EsqlControlType.VALUES_FROM_QUERY.value,
            title=control.title,
            selectedOptions=[],
            singleSelect=control.single_select or None,
            availableOptions=None,
        ),
    )


def compile_control(order: int, *, control: ControlTypes) -> KbnControlTypes:
    """Compile a single control into its Kibana view model representation.

    Args:
        order (int): The order of the control in the dashboard.
        control (ControlTypes): The control object to compile.

    Returns:
        KbnControlTypes: The compiled Kibana control view model.

    """
    if isinstance(control, OptionsListControl):
        return compile_options_list_control(order, control=control)

    if isinstance(control, TimeSliderControl):
        return compile_time_slider_control(order, control=control)

    if isinstance(control, RangeSliderControl):
        return compile_range_slider_control(order, control=control)

    if isinstance(control, ESQLStaticValuesControl):
        return compile_esql_static_control(order, control=control)

    if isinstance(control, ESQLQueryControl):  # pyright: ignore[reportUnnecessaryIsInstance]
        return compile_esql_query_control(order, control=control)

    # Explicit check to satisfy exhaustive checking pattern
    msg = f'Unknown control type: {type(control).__name__}'
    raise TypeError(msg)  # pyright: ignore[reportUnreachable]


def compile_control_panels_json(controls: Sequence[ControlTypes]) -> KbnControlPanelsJson:
    """Compile the control group input for a Dashboard object into its Kibana view model representation.

    Args:
        controls (Sequence[ControlTypes]): The sequence of control objects to compile.

    Returns:
        KbnControlPanelsJson: The compiled Kibana control panels JSON view model.

    """
    kbn_control_panels_json: KbnControlPanelsJson = KbnControlPanelsJson()

    for i, config_control in enumerate(iterable=controls):
        kbn_control: KbnControlTypes = compile_control(i, control=config_control)

        kbn_control_id: str = kbn_control.explicitInput.id

        kbn_control_panels_json.add(key=kbn_control_id, value=kbn_control)

    return kbn_control_panels_json


def compile_control_group(*, control_settings: ControlSettings, controls: Sequence[ControlTypes]) -> KbnControlGroupInput:
    """Compile a control group from a sequence of ControlTypes into a Kibana view model.

    Args:
        control_settings (ControlSettings): The settings for the control group.
        controls (Sequence[ControlTypes]): The sequence of control configurations to compile.

    Returns:
        KbnControlGroupInput: The compiled Kibana control group input view model.

    """
    panels_json = compile_control_panels_json(controls)

    # Kibana's control API uses "ignore" semantics (ignoreFilters, ignoreQuery, etc.)
    # but our config uses "apply" semantics for better UX. We invert the booleans here:
    # - apply_global_filters: True  → ignoreFilters: False  (respect filters)
    # - apply_global_filters: False → ignoreFilters: True   (ignore filters)
    ignore_parent_settings_json = KbnIgnoreParentSettingsJson(
        ignoreFilters=return_if(var=control_settings.apply_global_filters, is_true=False, is_false=True, default=False),
        ignoreQuery=return_if(var=control_settings.apply_global_filters, is_true=False, is_false=True, default=False),
        ignoreTimerange=return_if(var=control_settings.apply_global_timerange, is_true=False, is_false=True, default=False),
        ignoreValidations=return_if(var=control_settings.ignore_zero_results, is_true=True, is_false=False, default=False),
    )

    return KbnControlGroupInput(
        chainingSystem=return_if(
            var=control_settings.chain_controls,
            is_false=ChainingSystemEnum.NONE,
            is_true=ChainingSystemEnum.HIERARCHICAL,
            default=ChainingSystemEnum.HIERARCHICAL,
        ),
        controlStyle=return_if_equals(
            var=control_settings.label_position,
            equals='inline',
            is_true=ControlStyleEnum.ONE_LINE,
            is_false=ControlStyleEnum.TWO_LINE,
            is_none=ControlStyleEnum.ONE_LINE,
        ),
        ignoreParentSettingsJSON=ignore_parent_settings_json,
        panelsJSON=panels_json,
        showApplySelections=control_settings.click_to_apply or False,
    )
