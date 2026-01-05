from typing import TYPE_CHECKING, Any, TypeVar, overload

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


def extract_metrics_from_config(config: Any) -> list[Any]:  # pyright: ignore[reportAny]
    """Extract metrics from either 'metric' or 'metrics' attribute.

    Args:
        config: Object with either 'metric' or 'metrics' attribute

    Returns:
        List of metric configs

    Raises:
        ValueError: If neither metric nor metrics is provided

    """
    if hasattr(config, 'metric') and config.metric is not None:  # pyright: ignore[reportAny]
        return [config.metric]  # pyright: ignore[reportAny]
    if hasattr(config, 'metrics') and config.metrics is not None and len(config.metrics) > 0:  # pyright: ignore[reportAny]
        return config.metrics  # pyright: ignore[reportAny]
    msg = "Either 'metric' or 'metrics' must be provided"
    raise ValueError(msg)


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
