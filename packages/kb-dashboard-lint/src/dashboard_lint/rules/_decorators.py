"""Decorators for rule registration.

These decorators simplify rule registration by automatically creating
instances and registering them with the default registry.
"""

from collections.abc import Callable
from typing import Literal

from dashboard_compiler.panels.base import BasePanel
from dashboard_lint.registry import register_rule


def panel_rule[T](
    cls: type[T] | None = None,
    *,
    panel_types: tuple[type[BasePanel], ...] | None = None,
) -> type[T] | Callable[[type[T]], type[T]]:
    """Register a panel rule with the default registry.

    Can be used with or without arguments:

        @panel_rule
        @dataclass(frozen=True)
        class MyRule(PanelRule):
            ...

        @panel_rule(panel_types=(MarkdownPanel,))
        @dataclass(frozen=True)
        class MyRule(PanelRule):
            ...

    Args:
        cls: The rule class (when used without arguments).
        panel_types: Optional tuple of panel types to filter.

    Returns:
        The decorated class (unchanged except for registration side effect).

    """

    def decorator(cls: type[T]) -> type[T]:
        # Set panel_types on the class if provided and not already set
        if panel_types is not None:
            # Store on class for the instance to inherit
            original_init = cls.__init__  # type: ignore[misc]

            def patched_init(self: T, *args: object, **kwargs: object) -> None:
                original_init(self, *args, **kwargs)
                # Use object.__setattr__ for frozen dataclasses
                self_panel_types = getattr(self, 'panel_types', None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                if self_panel_types is None:
                    object.__setattr__(self, 'panel_types', panel_types)

            cls.__init__ = patched_init  # type: ignore[misc]

        # Create instance and register
        instance = cls()
        _ = register_rule(instance)  # pyright: ignore[reportArgumentType]
        return cls

    if cls is not None:
        # Used as @panel_rule without arguments
        return decorator(cls)
    # Used as @panel_rule(...) with arguments
    return decorator


def chart_rule[T](
    cls: type[T] | None = None,
    *,
    chart_types: tuple[str, ...] | None = None,
    panel_types: tuple[Literal['lens', 'esql'], ...] | None = None,
) -> type[T] | Callable[[type[T]], type[T]]:
    """Register a chart rule with the default registry.

    Can be used with or without arguments:

        @chart_rule
        @dataclass(frozen=True)
        class MyRule(ChartRule):
            ...

        @chart_rule(chart_types=('metric', 'gauge'))
        @dataclass(frozen=True)
        class MyRule(ChartRule):
            ...

    Args:
        cls: The rule class (when used without arguments).
        chart_types: Optional tuple of chart types to filter.
        panel_types: Optional tuple of panel types ('lens', 'esql') to filter.

    Returns:
        The decorated class (unchanged except for registration side effect).

    """

    def decorator(cls: type[T]) -> type[T]:
        original_init = cls.__init__  # type: ignore[misc]

        def patched_init(self: T, *args: object, **kwargs: object) -> None:
            original_init(self, *args, **kwargs)
            # Use object.__setattr__ for frozen dataclasses
            self_chart_types = getattr(self, 'chart_types', None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            self_panel_types = getattr(self, 'panel_types', None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            if chart_types is not None and self_chart_types is None:
                object.__setattr__(self, 'chart_types', chart_types)
            if panel_types is not None and self_panel_types is None:
                object.__setattr__(self, 'panel_types', panel_types)

        if chart_types is not None or panel_types is not None:
            cls.__init__ = patched_init  # type: ignore[misc]

        # Create instance and register
        instance = cls()
        _ = register_rule(instance)  # pyright: ignore[reportArgumentType]
        return cls

    if cls is not None:
        # Used as @chart_rule without arguments
        return decorator(cls)
    # Used as @chart_rule(...) with arguments
    return decorator


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
