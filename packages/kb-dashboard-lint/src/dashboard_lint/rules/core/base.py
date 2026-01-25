"""Base classes for lint rules with automatic iteration and type-safe filtering.

This module provides generic base classes that leverage Python's type system to:
1. Automatically extract runtime types from the generic type parameter
2. Filter panels/configs at runtime based on the extracted types
3. Pass the correctly-typed object to the check method, eliminating redundant isinstance checks
4. Validate rule options through Pydantic models for type safety

Example:
    @chart_rule
    class GaugeRule(ChartRule[LensGaugePanelConfig | ESQLGaugePanelConfig]):
        # No config_types needed - automatically extracted from generic parameter!

        def check_chart(self, panel, config, context, options):
            # config is already LensGaugePanelConfig | ESQLGaugePanelConfig
            # No isinstance check needed - can use config.goal directly
            ...

"""

import types
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Annotated, Any, Literal, get_args, get_origin

from pydantic import BaseModel

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    LensPanel,
    LensPanelConfig,
)
from dashboard_lint.types import Severity, Violation


class EmptyOptions(BaseModel):
    """Empty options model for rules that don't accept any options.

    This model forbids extra fields, ensuring users don't accidentally
    pass options to rules that don't support them.
    """

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}


# Store Union for runtime comparison - needed for checking get_origin() results
# pyright: reportDeprecated=false
_UNION_TYPE: Any = typing.Union

# Type alias for flexible return types from check methods
type ViolationResult = Violation | list[Violation] | None

# Class-level caches for extracted types (keyed by class)
# Using class-level dicts because rule instances are frozen dataclasses
_panel_types_cache: dict[type, tuple[type, ...] | None] = {}
_config_types_cache: dict[type, tuple[type, ...] | None] = {}


def normalize_result(result: ViolationResult) -> list[Violation]:
    """Normalize rule check results to a list.

    Args:
        result: Single violation, list of violations, or None.

    Returns:
        List of violations (empty list if None).

    """
    if result is None:
        return []
    if isinstance(result, Violation):
        return [result]
    return result


def _unwrap_type_alias(type_arg: Any) -> tuple[type, ...]:  # pyright: ignore[reportAny]
    """Unwrap a type alias to get the underlying concrete types.

    Handles:
    - TypeAliasType (from `type X = A | B` syntax)
    - Union types (both runtime `A | B` and typing.Union[A, B])
    - Annotated types (extracts the underlying type for isinstance checks)
    - Plain types (A)

    Args:
        type_arg: A type, union, or type alias.

    Returns:
        Tuple of concrete types suitable for isinstance() checks.

    """
    # Handle Python 3.12+ type aliases: `type X = A | B`
    if hasattr(type_arg, '__value__'):  # pyright: ignore[reportAny]
        # This is a TypeAliasType - get its value
        inner = type_arg.__value__  # pyright: ignore[reportAny]
        return _unwrap_type_alias(inner)

    origin = get_origin(type_arg)  # pyright: ignore[reportAny]

    # Handle Union types: both runtime UnionType (A | B) and typing.Union
    if origin is types.UnionType or origin is _UNION_TYPE:
        result: list[type] = []
        for arg in get_args(type_arg):  # pyright: ignore[reportAny]
            result.extend(_unwrap_type_alias(arg))
        return tuple(result)

    # Handle Annotated types: Annotated[X, ...] -> extract X
    # This is crucial for Pydantic models which use Annotated extensively
    if origin is Annotated:
        args = get_args(type_arg)
        if args:
            # For Annotated[X, metadata...], args[0] is the actual type
            return _unwrap_type_alias(args[0])

    # Plain type - verify it's actually a type
    if isinstance(type_arg, type):
        return (type_arg,)

    # Fallback - shouldn't happen but return empty to avoid isinstance errors
    return ()


def _extract_types_from_generic(cls: type, base_class: type) -> tuple[type, ...] | None:
    """Extract concrete types from a generic type parameter.

    Inspects the class's __orig_bases__ to find the parameterized base class
    and extracts the type arguments. Handles Union types (X | Y), type
    aliases, and Annotated types, flattening them into a tuple of concrete
    types suitable for isinstance() checks.

    Args:
        cls: The class to inspect (e.g., GaugeRule).
        base_class: The generic base class to look for (e.g., ChartRule).

    Returns:
        Tuple of concrete types, or None if no type parameter found.

    Example:
        class GaugeRule(ChartRule[LensGaugePanelConfig | ESQLGaugePanelConfig]):
            pass

        _extract_types_from_generic(GaugeRule, ChartRule)
        # Returns: (LensGaugePanelConfig, ESQLGaugePanelConfig)

    """
    for orig_base in getattr(cls, '__orig_bases__', ()):  # pyright: ignore[reportAny]
        origin = get_origin(orig_base)  # pyright: ignore[reportAny]
        if origin is None:
            continue

        # Check if this is the base class we're looking for
        # For Python 3.12+ generic syntax, origin is the base class
        if origin is base_class or (hasattr(origin, '__mro__') and base_class in origin.__mro__):  # pyright: ignore[reportAny]
            args = get_args(orig_base)
            if not args:
                return None

            return _unwrap_type_alias(args[0])

    return None


@dataclass(frozen=True)
class PanelContext:
    """Context provided to panel-level rules.

    Contains information about the current panel being checked,
    including its position in the dashboard and helper methods
    for generating location strings.
    """

    dashboard_name: str
    """Name of the dashboard containing the panel."""

    panel_index: int
    """0-based index of the panel in the dashboard.panels list."""

    panel_title: str | None
    """Title of the panel, or None if empty/untitled."""

    def location(self, suffix: str = '') -> str:
        """Generate a location string for violations.

        Args:
            suffix: Optional path suffix (e.g., 'size', 'lens.metrics[0]').

        Returns:
            Location string like 'panels[2]' or 'panels[2].size'.

        """
        base = f'panels[{self.panel_index}]'
        if len(suffix) > 0:
            return f'{base}.{suffix}'
        return base


@dataclass(frozen=True)
class ChartContext(PanelContext):
    """Context provided to chart-level rules.

    Extends PanelContext with chart-specific information like
    the chart type and whether it's a Lens or ESQL panel.
    """

    chart_type: str
    """Chart type string (e.g., 'metric', 'gauge', 'line')."""

    panel_type: Literal['lens', 'esql']
    """Whether this is a 'lens' or 'esql' panel."""

    def location(self, suffix: str = '') -> str:  # pyright: ignore[reportImplicitOverride]
        """Generate a location string including panel type.

        Args:
            suffix: Optional path suffix (e.g., 'metrics[0]').

        Returns:
            Location string like 'panels[2].lens' or 'panels[2].esql.query'.

        """
        base = f'panels[{self.panel_index}].{self.panel_type}'
        if len(suffix) > 0:
            return f'{base}.{suffix}'
        return base


class DashboardRule[OptionsT: BaseModel](ABC):
    """Base class for dashboard-level rules.

    Dashboard rules check properties of the entire dashboard, such as
    filters, settings, or cross-panel consistency.

    Type Parameter:
        OptionsT: Pydantic model for rule options. Use EmptyOptions for rules
                  without configurable options.

    Subclasses must implement check_dashboard() and define id, description,
    default_severity, and options_model as class attributes.
    """

    id: str
    description: str
    default_severity: Severity
    options_model: type[OptionsT]
    """Pydantic model class for validating and parsing options."""

    @abstractmethod
    def check_dashboard(
        self,
        dashboard: Dashboard,
        options: OptionsT,
    ) -> ViolationResult:
        """Check the dashboard for violations.

        Args:
            dashboard: The dashboard to check.
            options: Validated rule-specific options.

        Returns:
            Single violation, list of violations, or None if no issues.

        """
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Implement Rule protocol by delegating to check_dashboard.

        Args:
            dashboard: The dashboard to check.
            options: Raw options dict to validate through options_model.

        Returns:
            List of violations found.

        """
        validated_options = self.options_model.model_validate(options)
        return normalize_result(self.check_dashboard(dashboard, validated_options))


class PanelRule[PanelT: BasePanel, OptionsT: BaseModel](ABC):
    """Base class for panel-level rules with automatic iteration and type filtering.

    Panel rules check individual panels. The base class handles iteration
    over all panels in the dashboard, filtering by panel type automatically
    extracted from the generic type parameter.

    Type Parameters:
        PanelT: The panel type(s) this rule accepts. Used for both static type
                checking AND automatic runtime filtering.
        OptionsT: Pydantic model for rule options. Use EmptyOptions for rules
                  without configurable options.

    Example:
        class MarkdownOptions(BaseModel):
            min_height: int = 3

        @panel_rule
        class MarkdownRule(PanelRule[MarkdownPanel, MarkdownOptions]):
            options_model = MarkdownOptions

            def check_panel(self, panel: MarkdownPanel, context, options):
                # options is typed as MarkdownOptions
                if panel.size.h < options.min_height:
                    ...

    Subclasses must:
    - Implement check_panel() with the correct panel type annotation
    - Define id, description, default_severity, and options_model as class attributes

    """

    id: str
    description: str
    default_severity: Severity
    options_model: type[OptionsT]
    """Pydantic model class for validating and parsing options."""

    def get_panel_types(self) -> tuple[type, ...] | None:
        """Get panel types to filter, extracted from generic type parameter.

        Returns:
            Tuple of panel types to check, or None to check all panels.

        """
        cls = type(self)
        if cls not in _panel_types_cache:
            _panel_types_cache[cls] = _extract_types_from_generic(cls, PanelRule)
        return _panel_types_cache[cls]

    @abstractmethod
    def check_panel(
        self,
        panel: PanelT,
        context: PanelContext,
        options: OptionsT,
    ) -> ViolationResult:
        """Check a single panel for violations.

        Args:
            panel: The panel to check (type matches panel_types filter).
            context: Context with dashboard name, panel index, and title.
            options: Validated rule-specific options.

        Returns:
            Single violation, list of violations, or None if no issues.

        """
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Implement Rule protocol with automatic panel iteration.

        Iterates over all panels in the dashboard, filtering by panel types
        extracted from the generic parameter, and calls check_panel for each.

        Args:
            dashboard: The dashboard to check.
            options: Raw options dict to validate through options_model.

        Returns:
            List of violations found across all panels.

        """
        validated_options = self.options_model.model_validate(options)
        violations: list[Violation] = []
        panel_types = self.get_panel_types()

        for idx, panel in enumerate(dashboard.panels):
            # Filter by panel type if specified
            if panel_types is not None and not isinstance(panel, panel_types):
                continue

            context = PanelContext(
                dashboard_name=dashboard.name,
                panel_index=idx,
                panel_title=panel.title if len(panel.title) > 0 else None,
            )

            result = self.check_panel(panel, context, validated_options)  # pyright: ignore[reportArgumentType]
            violations.extend(normalize_result(result))

        return violations


class ChartRule[ConfigT: (LensPanelConfig | ESQLPanelConfig), OptionsT: BaseModel](ABC):
    """Base class for chart-level rules with automatic iteration and type filtering.

    Chart rules check LensPanel and ESQLPanel configurations. The base
    class handles iteration and filtering by config types automatically
    extracted from the generic type parameter.

    Type Parameters:
        ConfigT: The config type(s) this rule accepts. Used for both static type
                 checking AND automatic runtime filtering.
        OptionsT: Pydantic model for rule options. Use EmptyOptions for rules
                  without configurable options.

    Example:
        class GaugeOptions(BaseModel):
            require_max: bool = True

        @chart_rule
        class GaugeRule(ChartRule[LensGaugePanelConfig, GaugeOptions]):
            options_model = GaugeOptions

            def check_chart(self, panel, config, context, options):
                # options is typed as GaugeOptions
                if options.require_max and config.maximum is None:
                    ...

    Subclasses must:
    - Implement check_chart() with the correct config type annotation
    - Define id, description, default_severity, and options_model as class attributes

    """

    id: str
    description: str
    default_severity: Severity
    options_model: type[OptionsT]
    """Pydantic model class for validating and parsing options."""

    def get_config_types(self) -> tuple[type, ...] | None:
        """Get config types to filter, extracted from generic type parameter.

        Returns:
            Tuple of config types to check, or None to check all configs.

        """
        cls = type(self)
        if cls not in _config_types_cache:
            _config_types_cache[cls] = _extract_types_from_generic(cls, ChartRule)
        return _config_types_cache[cls]

    @abstractmethod
    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,
        config: ConfigT,
        context: ChartContext,
        options: OptionsT,
    ) -> ViolationResult:
        """Check a single chart panel for violations.

        Args:
            panel: The LensPanel or ESQLPanel to check.
            config: The panel's chart configuration (type matches config_types filter).
            context: Context with dashboard name, panel info, and chart type.
            options: Validated rule-specific options.

        Returns:
            Single violation, list of violations, or None if no issues.

        """
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Implement Rule protocol with automatic chart iteration.

        Iterates over all LensPanel and ESQLPanel instances, filtering by
        config types extracted from the generic parameter, and calls check_chart.

        Args:
            dashboard: The dashboard to check.
            options: Raw options dict to validate through options_model.

        Returns:
            List of violations found across all chart panels.

        """
        validated_options = self.options_model.model_validate(options)
        violations: list[Violation] = []
        config_types = self.get_config_types()

        for idx, panel in enumerate(dashboard.panels):
            panel_type: Literal['lens', 'esql'] | None = None
            config: LensPanelConfig | ESQLPanelConfig | None = None
            chart_type: str | None = None

            if isinstance(panel, LensPanel):
                panel_type = 'lens'
                config = panel.lens
                chart_type = config.type
            elif isinstance(panel, ESQLPanel):
                panel_type = 'esql'
                config = panel.esql
                chart_type = config.type
            else:
                # Not a chart panel (e.g., MarkdownPanel)
                continue

            # Filter by config type if specified
            if config_types is not None and not isinstance(config, config_types):
                continue

            context = ChartContext(
                dashboard_name=dashboard.name,
                panel_index=idx,
                panel_title=panel.title if len(panel.title) > 0 else None,
                chart_type=chart_type,
                panel_type=panel_type,
            )

            result = self.check_chart(panel, config, context, validated_options)  # pyright: ignore[reportArgumentType]
            violations.extend(normalize_result(result))

        return violations
