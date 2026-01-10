"""Logging utilities for the dashboard compiler."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dashboard_compiler.controls import ControlTypes
    from dashboard_compiler.filters import RangeFilter
    from dashboard_compiler.filters.config import FilterTypes

logger = logging.getLogger('dashboard_compiler')


def get_filter_description(filter_obj: 'FilterTypes') -> str:  # noqa: PLR0911
    """Get a human-readable description of a filter.

    Args:
        filter_obj: A filter object (PhraseFilter, RangeFilter, etc.)

    Returns:
        A concise description of the filter.

    """
    # Import locally to avoid circular imports
    from dashboard_compiler.filters import (
        AndFilter,
        CustomFilter,
        ExistsFilter,
        NegateFilter,
        OrFilter,
        PhraseFilter,
        PhrasesFilter,
        RangeFilter,
    )

    match filter_obj:
        case PhraseFilter():
            return f'{filter_obj.field} = {filter_obj.equals!r}'
        case PhrasesFilter():
            return f'{filter_obj.field} in {list(filter_obj.in_list)!r}'
        case RangeFilter():
            parts = _get_range_parts(filter_obj)
            return f'{filter_obj.field} {" ".join(parts)}'
        case ExistsFilter():
            return f'exists({filter_obj.exists})'
        case AndFilter():
            return f'AND ({len(filter_obj.and_filters)} filters)'
        case OrFilter():
            return f'OR ({len(filter_obj.or_filters)} filters)'
        case NegateFilter():
            return f'NOT {get_filter_description(filter_obj.not_filter)}'
        case CustomFilter():
            return 'custom DSL'
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unknown filter type: {type(filter_obj).__name__}'
            raise TypeError(msg)  # pyright: ignore[reportUnreachable]


def _get_range_parts(filter_obj: 'RangeFilter') -> list[str]:
    """Build range description parts."""
    parts: list[str] = []
    if filter_obj.gte is not None:
        parts.append(f'>= {filter_obj.gte}')
    if filter_obj.gt is not None:
        parts.append(f'> {filter_obj.gt}')
    if filter_obj.lte is not None:
        parts.append(f'<= {filter_obj.lte}')
    if filter_obj.lt is not None:
        parts.append(f'< {filter_obj.lt}')
    return parts


def get_control_description(control_obj: 'ControlTypes') -> str:  # noqa: PLR0911
    """Get a human-readable description of a control.

    Args:
        control_obj: A control object (OptionsListControl, RangeSliderControl, etc.)

    Returns:
        A concise description of the control.

    """
    # Import locally to avoid circular imports
    from dashboard_compiler.controls.config import (
        ESQLFieldControl,
        ESQLFunctionControl,
        ESQLQueryControl,
        ESQLStaticMultiSelectControl,
        ESQLStaticSingleSelectControl,
        OptionsListControl,
        RangeSliderControl,
        TimeSliderControl,
    )

    match control_obj:
        case OptionsListControl():
            return control_obj.label or control_obj.field
        case RangeSliderControl():
            return control_obj.label or control_obj.field
        case TimeSliderControl():
            return 'time slider'
        case ESQLFieldControl():
            return control_obj.label or control_obj.variable_name
        case ESQLFunctionControl():
            return control_obj.label or control_obj.variable_name
        case ESQLStaticSingleSelectControl():
            return control_obj.label or control_obj.variable_name
        case ESQLStaticMultiSelectControl():
            return control_obj.label or control_obj.variable_name
        case ESQLQueryControl():
            return control_obj.label or control_obj.variable_name
        case _:  # pyright: ignore[reportUnnecessaryComparison]
            msg = f'Unknown control type: {type(control_obj).__name__}'
            raise TypeError(msg)  # pyright: ignore[reportUnreachable]
