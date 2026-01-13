from typing import TYPE_CHECKING, Any, TypeVar, overload

from dashboard_compiler.panels.charts.esql.columns.view import (
    KbnESQLFieldMetricColumn,
    KbnESQLMetricColumnTypes,
)
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensFieldMetricColumn,
    KbnLensFormulaColumn,
    KbnLensMetricColumnTypes,
)

if TYPE_CHECKING:
    from dashboard_compiler.panels.charts.esql.columns.config import ESQLMetricTypes, ESQLStaticValue
    from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes, LensStaticValue

T = TypeVar('T')
V = TypeVar('V')


def return_if(var: bool | None, is_false: T, is_true: T, default: T) -> T:
    """Evaluate var and return a corresponding value.

    Args:
        var: The variable to evaluate.
        is_false: The value to return if var is False.
        is_true: The value to return if var is True.
        default: The value to return if var is None.

    Returns:
        The value corresponding to the evaluation of var.

    """
    return default if var is None else (is_true if var else is_false)


def return_if_equals(var: V | None, equals: V, is_false: T, is_true: T, is_none: T) -> T:
    """Evaluate var against a value and return a corresponding value.

    Args:
        var: The variable to evaluate.
        equals: The value to compare against.
        is_false: The value to return if var does not equal equals.
        is_true: The value to return if var equals equals.
        is_none: The value to return if var is None.

    Returns:
        The value corresponding to the evaluation of var.

    """
    if var is None:
        return is_none
    return is_true if var == equals else is_false


@overload
def normalize_static_metric(value: int | float, static_value_class: type['LensStaticValue']) -> 'LensStaticValue': ...


@overload
def normalize_static_metric(value: int | float, static_value_class: type['ESQLStaticValue']) -> 'ESQLStaticValue': ...


@overload
def normalize_static_metric(value: 'LensMetricTypes', static_value_class: type['LensStaticValue']) -> 'LensMetricTypes': ...


@overload
def normalize_static_metric(value: 'ESQLMetricTypes', static_value_class: type['ESQLStaticValue']) -> 'ESQLMetricTypes': ...


def normalize_static_metric(value: Any, static_value_class: type) -> Any:  # pyright: ignore[reportAny]
    """Convert numeric values to StaticValue, keep metric configs as-is.

    Args:
        value: Value to normalize (number or metric config)
        static_value_class: StaticValue class (LensStaticValue or ESQLStaticValue)

    Returns:
        StaticValue instance if input is numeric, otherwise original value

    """
    if isinstance(value, (int, float)):
        return static_value_class(value=value)  # pyright: ignore[reportAny]
    return value  # pyright: ignore[reportAny]


def split_dimensions(all_dimension_ids: list[str]) -> tuple[list[str], list[str] | None]:
    """Split dimensions into primary (first) and secondary (rest).

    Args:
        all_dimension_ids: All dimension IDs

    Returns:
        Tuple of (primary_ids, secondary_ids or None)

    """
    primary = [all_dimension_ids[0]] if len(all_dimension_ids) > 0 else []
    secondary = all_dimension_ids[1:] if len(all_dimension_ids) > 1 else None
    return primary, secondary


def apply_decimal_places_to_lens_metric(
    metric: KbnLensMetricColumnTypes,
    decimal_places: int,
) -> KbnLensMetricColumnTypes:
    """Apply decimal places override to a compiled Lens metric column.

    Creates a new metric column with the decimals value overridden in the format params.
    Only applies to metrics that have a format defined. Preserves all other format properties.

    Args:
        metric: The compiled Lens metric column.
        decimal_places: The number of decimal places to apply.

    Returns:
        A new metric column with the decimals value overridden, or the original if no format is defined.

    """
    if isinstance(metric, (KbnLensFieldMetricColumn, KbnLensFormulaColumn)) and metric.params.format is not None:
        new_format_params = metric.params.format.params.model_copy(update={'decimals': decimal_places})
        new_format = metric.params.format.model_copy(update={'params': new_format_params})
        new_params = metric.params.model_copy(update={'format': new_format})
        return metric.model_copy(update={'params': new_params})
    return metric


def apply_decimal_places_to_esql_metric(
    metric: KbnESQLMetricColumnTypes,
    decimal_places: int,
) -> KbnESQLMetricColumnTypes:
    """Apply decimal places override to a compiled ES|QL metric column.

    Creates a new metric column with the decimals value overridden in the format params.
    Only applies to metrics that have a format defined. Preserves all other format properties.

    Args:
        metric: The compiled ES|QL metric column.
        decimal_places: The number of decimal places to apply.

    Returns:
        A new metric column with the decimals value overridden, or the original if no format is defined.

    """
    if isinstance(metric, KbnESQLFieldMetricColumn) and metric.params is not None and metric.params.format is not None:
        new_format_params = metric.params.format.params.model_copy(update={'decimals': decimal_places})
        new_format = metric.params.format.model_copy(update={'params': new_format_params})
        new_params = metric.params.model_copy(update={'format': new_format})
        return metric.model_copy(update={'params': new_params})
    return metric
