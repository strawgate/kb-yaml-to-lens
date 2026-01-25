"""Base classes for lint rules with automatic iteration."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.charts.config import (
    ESQLPanel,
    ESQLPanelConfig,
    LensPanel,
    LensPanelConfig,
)
from dashboard_lint.types import Severity, Violation

# Type alias for flexible return types from check methods
type ViolationResult = Violation | list[Violation] | None


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

    def location(self, suffix: str = '') -> str:
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


class DashboardRule(ABC):
    """Base class for dashboard-level rules.

    Dashboard rules check properties of the entire dashboard, such as
    filters, settings, or cross-panel consistency.

    Subclasses must implement check_dashboard() and define id, description,
    and default_severity as class attributes.
    """

    id: str
    description: str
    default_severity: Severity

    @abstractmethod
    def check_dashboard(
        self,
        dashboard: Dashboard,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check the dashboard for violations.

        Args:
            dashboard: The dashboard to check.
            options: Rule-specific options from configuration.

        Returns:
            Single violation, list of violations, or None if no issues.

        """
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Implement Rule protocol by delegating to check_dashboard.

        Args:
            dashboard: The dashboard to check.
            options: Rule-specific options.

        Returns:
            List of violations found.

        """
        return normalize_result(self.check_dashboard(dashboard, options))


class PanelRule(ABC):
    """Base class for panel-level rules with automatic iteration.

    Panel rules check individual panels. The base class handles iteration
    over all panels in the dashboard, filtering by panel type if specified.

    Subclasses must implement check_panel() and define id, description,
    and default_severity as class attributes. Optionally set panel_types
    to filter which panel types to check.
    """

    id: str
    description: str
    default_severity: Severity
    panel_types: tuple[type[BasePanel], ...] | None = None
    """Panel types to check. None means check all panels."""

    @abstractmethod
    def check_panel(
        self,
        panel: BasePanel,
        context: PanelContext,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check a single panel for violations.

        Args:
            panel: The panel to check.
            context: Context with dashboard name, panel index, and title.
            options: Rule-specific options from configuration.

        Returns:
            Single violation, list of violations, or None if no issues.

        """
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Implement Rule protocol with automatic panel iteration.

        Iterates over all panels in the dashboard, filtering by panel_types
        if specified, and calls check_panel for each.

        Args:
            dashboard: The dashboard to check.
            options: Rule-specific options.

        Returns:
            List of violations found across all panels.

        """
        violations: list[Violation] = []

        for idx, panel in enumerate(dashboard.panels):
            # Filter by panel type if specified
            if self.panel_types is not None and not isinstance(panel, self.panel_types):
                continue

            context = PanelContext(
                dashboard_name=dashboard.name,
                panel_index=idx,
                panel_title=panel.title if len(panel.title) > 0 else None,
            )

            result = self.check_panel(panel, context, options)
            violations.extend(normalize_result(result))

        return violations


class ChartRule(ABC):
    """Base class for chart-level rules with automatic iteration.

    Chart rules check LensPanel and ESQLPanel configurations. The base
    class handles iteration and filtering by config type.

    Subclasses must implement check_chart() and define id, description,
    and default_severity as class attributes. Optionally set config_types
    to filter which chart configuration types to check.

    Example:
        @chart_rule(config_types=(LensGaugePanelConfig, ESQLGaugePanelConfig))
        @dataclass(frozen=True)
        class GaugeRule(ChartRule):
            ...

    """

    id: str
    description: str
    default_severity: Severity
    config_types: tuple[type, ...] | None = None
    """Config types to check (e.g., (LensGaugePanelConfig,)). None means all."""

    @abstractmethod
    def check_chart(
        self,
        panel: LensPanel | ESQLPanel,
        config: LensPanelConfig | ESQLPanelConfig,
        context: ChartContext,
        options: dict[str, Any],
    ) -> ViolationResult:
        """Check a single chart panel for violations.

        Args:
            panel: The LensPanel or ESQLPanel to check.
            config: The panel's chart configuration.
            context: Context with dashboard name, panel info, and chart type.
            options: Rule-specific options from configuration.

        Returns:
            Single violation, list of violations, or None if no issues.

        """
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Implement Rule protocol with automatic chart iteration.

        Iterates over all LensPanel and ESQLPanel instances, filtering by
        config_types if specified, and calls check_chart for each.

        Args:
            dashboard: The dashboard to check.
            options: Rule-specific options.

        Returns:
            List of violations found across all chart panels.

        """
        violations: list[Violation] = []

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
            if self.config_types is not None and not isinstance(config, self.config_types):
                continue

            context = ChartContext(
                dashboard_name=dashboard.name,
                panel_index=idx,
                panel_title=panel.title if len(panel.title) > 0 else None,
                chart_type=chart_type,
                panel_type=panel_type,
            )

            result = self.check_chart(panel, config, context, options)
            violations.extend(normalize_result(result))

        return violations
