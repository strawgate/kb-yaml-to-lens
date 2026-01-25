"""Decorators for rule registration.

These decorators simplify rule registration by automatically creating
instances and registering them with the default registry.
"""

from collections.abc import Callable

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
            original_init = cls.__init__  # type: ignore[misc]

            def patched_init(self: T, *args: object, **kwargs: object) -> None:
                original_init(self, *args, **kwargs)
                # Use object.__setattr__ for frozen dataclasses
                self_panel_types = getattr(self, 'panel_types', None)
                if self_panel_types is None:
                    object.__setattr__(self, 'panel_types', panel_types)

            cls.__init__ = patched_init  # type: ignore[method-assign]

        # Create instance and register
        instance = cls()
        register_rule(instance)  # type: ignore[arg-type]
        return cls

    if cls is not None:
        # Used as @panel_rule without arguments
        return decorator(cls)
    # Used as @panel_rule(...) with arguments
    return decorator


def chart_rule[T](
    cls: type[T] | None = None,
    *,
    config_types: tuple[type, ...] | None = None,
) -> type[T] | Callable[[type[T]], type[T]]:
    """Register a chart rule with the default registry.

    Can be used with or without arguments:

        @chart_rule
        @dataclass(frozen=True)
        class MyRule(ChartRule):
            ...

        @chart_rule(config_types=(LensGaugePanelConfig, ESQLGaugePanelConfig))
        @dataclass(frozen=True)
        class MyRule(ChartRule):
            ...

    Args:
        cls: The rule class (when used without arguments).
        config_types: Optional tuple of config types to filter. Use actual
            config classes like LensGaugePanelConfig instead of strings.

    Returns:
        The decorated class (unchanged except for registration side effect).

    """

    def decorator(cls: type[T]) -> type[T]:
        if config_types is not None:
            original_init = cls.__init__  # type: ignore[misc]

            def patched_init(self: T, *args: object, **kwargs: object) -> None:
                original_init(self, *args, **kwargs)
                # Use object.__setattr__ for frozen dataclasses
                self_config_types: tuple[type, ...] | None = getattr(self, 'config_types', None)
                if self_config_types is None:
                    object.__setattr__(self, 'config_types', config_types)

            cls.__init__ = patched_init  # type: ignore[method-assign]

        # Create instance and register
        instance = cls()
        register_rule(instance)  # type: ignore[arg-type]
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
    register_rule(instance)  # type: ignore[arg-type]
    return cls
