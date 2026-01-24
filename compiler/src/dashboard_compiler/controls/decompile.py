"""Decompile Kibana controls back to config models."""

from dashboard_compiler.controls.config import (
    ControlSettings,
    ControlTypes,
    ESQLFieldControl,
    ESQLFunctionControl,
    ESQLQueryMultiSelectControl,
    ESQLQuerySingleSelectControl,
    ESQLStaticMultiSelectControl,
    ESQLStaticSingleSelectControl,
    MatchTechnique,
    OptionsListControl,
    RangeSliderControl,
    TimeSliderControl,
)
from dashboard_compiler.controls.types import EsqlControlType, ESQLVariableType
from dashboard_compiler.controls.view import (
    ChainingSystemEnum,
    ControlStyleEnum,
    KbnControlGroupInput,
    KbnControlTypes,
    KbnESQLControl,
    KbnOptionsListControl,
    KbnRangeSliderControl,
    KbnTimeSliderControl,
    SearchTechnique,
)
from dashboard_compiler.shared.decompile_context import DecompileContext


def decompile_control_settings(
    control_group: KbnControlGroupInput | None,
) -> ControlSettings:
    """Decompile control group settings.

    Args:
        control_group: The Kibana control group input.

    Returns:
        The decompiled control settings.

    """
    if control_group is None:
        return ControlSettings()

    ignore = control_group.ignoreParentSettingsJSON

    # Invert the ignore semantics back to apply semantics
    apply_filters = not ignore.ignoreFilters if ignore.ignoreFilters else None
    apply_timerange = not ignore.ignoreTimerange if ignore.ignoreTimerange else None
    ignore_zero = ignore.ignoreValidations if ignore.ignoreValidations else None

    # Map chaining system
    chain = None
    if control_group.chainingSystem == ChainingSystemEnum.NONE:
        chain = False
    elif control_group.chainingSystem == ChainingSystemEnum.HIERARCHICAL:
        chain = None  # Default is hierarchical

    # Map control style to label position
    label_pos = None
    if control_group.controlStyle == ControlStyleEnum.TWO_LINE:
        label_pos = 'above'
    # ONE_LINE is default ('inline'), so leave as None

    return ControlSettings(
        label_position=label_pos,
        apply_global_filters=apply_filters,
        apply_global_timerange=apply_timerange,
        ignore_zero_results=ignore_zero,
        chain_controls=chain,
        click_to_apply=control_group.showApplySelections if control_group.showApplySelections else None,
    )


def decompile_options_list_control(
    control_id: str,
    kbn_control: KbnOptionsListControl,
) -> OptionsListControl:
    """Decompile an options list control."""
    explicit = kbn_control.explicitInput

    # Map search technique to match technique
    match_technique: MatchTechnique | None = None
    if explicit.searchTechnique == SearchTechnique.PREFIX:
        match_technique = None  # Default
    elif explicit.searchTechnique == SearchTechnique.WILDCARD:
        match_technique = MatchTechnique.CONTAINS
    elif explicit.searchTechnique == SearchTechnique.EXACT:
        match_technique = MatchTechnique.EXACT

    # Map singleSelect back to multiple
    multiple: bool | None = None
    if explicit.singleSelect is True:
        multiple = False
    elif explicit.singleSelect is False:
        multiple = True

    return OptionsListControl(
        id=control_id,
        field=explicit.fieldName,
        data_view=explicit.dataViewId,
        label=explicit.title,
        width=kbn_control.width if kbn_control.width != 'medium' else None,
        fill_width=kbn_control.grow,
        match_technique=match_technique,
        wait_for_results=explicit.runPastTimeout,
        preselected=explicit.selectedOptions or [],
        multiple=multiple,
    )


def decompile_range_slider_control(
    control_id: str,
    kbn_control: KbnRangeSliderControl,
) -> RangeSliderControl:
    """Decompile a range slider control."""
    explicit = kbn_control.explicitInput

    return RangeSliderControl(
        id=control_id,
        field=explicit.fieldName,
        data_view=explicit.dataViewId,
        label=explicit.title,
        width=kbn_control.width if kbn_control.width != 'medium' else None,
        fill_width=kbn_control.grow,
        step=explicit.step if explicit.step != 1 else None,
    )


def decompile_time_slider_control(
    control_id: str,
    kbn_control: KbnTimeSliderControl,
) -> TimeSliderControl:
    """Decompile a time slider control."""
    explicit = kbn_control.explicitInput

    # Default time range is 0.0 to 100.0
    default_start = 0.0
    default_end = 100.0

    return TimeSliderControl(
        id=control_id,
        width=kbn_control.width if kbn_control.width != 'medium' else None,
        label=None,  # Time slider doesn't have label in explicit input
        start_offset=explicit.timesliceStartAsPercentageOfTimeRange
        if explicit.timesliceStartAsPercentageOfTimeRange != default_start
        else None,
        end_offset=explicit.timesliceEndAsPercentageOfTimeRange if explicit.timesliceEndAsPercentageOfTimeRange != default_end else None,
    )


def decompile_esql_control(  # noqa: PLR0911
    control_id: str,
    kbn_control: KbnESQLControl,
    *,
    context: DecompileContext,
) -> ControlTypes | None:
    """Decompile an ES|QL control."""
    explicit = kbn_control.explicitInput

    # Determine control variant based on variable type and control type
    var_type = explicit.variableType
    control_type = explicit.controlType
    is_multi = explicit.singleSelect is not True

    # Fields control
    if var_type == ESQLVariableType.FIELDS:
        if control_type != EsqlControlType.STATIC_VALUES:
            context.warn(f'ES|QL fields control must be STATIC_VALUES, got {control_type}')
            return None

        return ESQLFieldControl(
            id=control_id,
            variable_name=explicit.variableName,
            choices=explicit.availableOptions or [],
            default=explicit.selectedOptions[0] if len(explicit.selectedOptions) > 0 else None,
            label=explicit.title,
            width=kbn_control.width if kbn_control.width != 'medium' else None,
        )

    # Functions control
    if var_type == ESQLVariableType.FUNCTIONS:
        if control_type != EsqlControlType.STATIC_VALUES:
            context.warn(f'ES|QL functions control must be STATIC_VALUES, got {control_type}')
            return None

        return ESQLFunctionControl(
            id=control_id,
            variable_name=explicit.variableName,
            choices=explicit.availableOptions or [],
            default=explicit.selectedOptions[0] if len(explicit.selectedOptions) > 0 else None,
            label=explicit.title,
            width=kbn_control.width if kbn_control.width != 'medium' else None,
        )

    # Static values control
    if control_type == EsqlControlType.STATIC_VALUES:
        if is_multi:
            return ESQLStaticMultiSelectControl(
                id=control_id,
                variable_name=explicit.variableName,
                variable_type=ESQLVariableType(var_type),
                choices=explicit.availableOptions or [],
                default=explicit.selectedOptions if len(explicit.selectedOptions) > 0 else None,
                label=explicit.title,
                width=kbn_control.width if kbn_control.width != 'medium' else None,
            )
        return ESQLStaticSingleSelectControl(
            id=control_id,
            variable_name=explicit.variableName,
            variable_type=ESQLVariableType(var_type),
            choices=explicit.availableOptions or [],
            default=explicit.selectedOptions[0] if len(explicit.selectedOptions) > 0 else None,
            label=explicit.title,
            width=kbn_control.width if kbn_control.width != 'medium' else None,
        )

    # Query-driven values control
    if control_type == EsqlControlType.VALUES_FROM_QUERY:
        if is_multi:
            return ESQLQueryMultiSelectControl(
                id=control_id,
                variable_name=explicit.variableName,
                variable_type=ESQLVariableType(var_type),
                query=explicit.esqlQuery,
                default=explicit.selectedOptions if len(explicit.selectedOptions) > 0 else None,
                label=explicit.title,
                width=kbn_control.width if kbn_control.width != 'medium' else None,
            )
        return ESQLQuerySingleSelectControl(
            id=control_id,
            variable_name=explicit.variableName,
            variable_type=ESQLVariableType(var_type),
            query=explicit.esqlQuery,
            default=explicit.selectedOptions[0] if len(explicit.selectedOptions) > 0 else None,
            label=explicit.title,
            width=kbn_control.width if kbn_control.width != 'medium' else None,
        )

    context.warn(f'Unsupported ES|QL control configuration: {control_type} / {var_type}')
    return None


def decompile_control(
    control_id: str,
    kbn_control: KbnControlTypes,
    *,
    context: DecompileContext,
) -> ControlTypes | None:
    """Decompile a single control.

    Args:
        control_id: The control's ID.
        kbn_control: The Kibana control view model.
        context: Decompilation context for warnings.

    Returns:
        The decompiled control config model, or None if unsupported.

    """
    if isinstance(kbn_control, KbnOptionsListControl):
        return decompile_options_list_control(control_id, kbn_control)
    if isinstance(kbn_control, KbnRangeSliderControl):
        return decompile_range_slider_control(control_id, kbn_control)
    if isinstance(kbn_control, KbnTimeSliderControl):
        return decompile_time_slider_control(control_id, kbn_control)
    if isinstance(kbn_control, KbnESQLControl):  # pyright: ignore[reportUnnecessaryIsInstance]
        return decompile_esql_control(control_id, kbn_control, context=context)

    context.warn(f'Unsupported control type: {type(kbn_control).__name__}')
    return None


def decompile_control_group(
    control_group: KbnControlGroupInput | None,
    *,
    context: DecompileContext,
) -> tuple[ControlSettings, list[ControlTypes]]:
    """Decompile control group input.

    Args:
        control_group: The Kibana control group input.
        context: Decompilation context for warnings.

    Returns:
        Tuple of (control settings, list of controls).

    """
    settings = decompile_control_settings(control_group)

    if control_group is None:
        return settings, []

    # Get controls sorted by order
    controls_dict = control_group.panelsJSON.root if hasattr(control_group.panelsJSON, 'root') else {}
    sorted_controls = sorted(
        controls_dict.items(),
        key=lambda x: x[1].order,
    )

    controls: list[ControlTypes] = []
    for control_id, kbn_control in sorted_controls:
        control = decompile_control(control_id, kbn_control, context=context)
        if control is not None:
            controls.append(control)

    return settings, controls
