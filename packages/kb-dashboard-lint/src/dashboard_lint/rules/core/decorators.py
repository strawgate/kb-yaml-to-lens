"""Decorators for rule registration.

These simple decorators register rule instances with the default registry.
Type filtering is handled via class attributes (panel_types, config_types),
not decorator parameters.
"""

from dashboard_lint.registry import register_rule


def panel_rule[T](cls: type[T]) -> type[T]:
    """Register a panel rule with the default registry.

    Usage:
        @panel_rule
        @dataclass(frozen=True)
        class MyRule(PanelRule[MarkdownPanel]):
            panel_types = (MarkdownPanel,)  # Runtime filtering
            ...

    Args:
        cls: The rule class to register.

    Returns:
        The decorated class (unchanged except for registration side effect).

    """
    instance = cls()
    _ = register_rule(instance)  # pyright: ignore[reportArgumentType]
    return cls


def chart_rule[T](cls: type[T]) -> type[T]:
    """Register a chart rule with the default registry.

    Usage:
        @chart_rule
        @dataclass(frozen=True)
        class MyRule(ChartRule[LensGaugePanelConfig | ESQLGaugePanelConfig]):
            config_types = (LensGaugePanelConfig, ESQLGaugePanelConfig)  # Runtime filtering
            ...

    Args:
        cls: The rule class to register.

    Returns:
        The decorated class (unchanged except for registration side effect).

    """
    instance = cls()
    _ = register_rule(instance)  # pyright: ignore[reportArgumentType]
    return cls


def dashboard_rule[T](cls: type[T]) -> type[T]:
    """Register a dashboard rule with the default registry.

    Usage:
        @dashboard_rule
        @dataclass(frozen=True)
        class MyRule(DashboardRule):
            ...

    Args:
        cls: The rule class to register.

    Returns:
        The decorated class (unchanged except for registration side effect).

    """
    instance = cls()
    _ = register_rule(instance)  # pyright: ignore[reportArgumentType]
    return cls
