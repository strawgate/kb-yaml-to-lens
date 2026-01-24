"""Core types for the dashboard linting system."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from dashboard_compiler.dashboard.config import Dashboard


class Severity(StrEnum):
    """Severity levels for lint violations."""

    ERROR = 'error'
    """Critical issues that should fail the build."""

    WARNING = 'warning'
    """Important issues that should be reviewed."""

    INFO = 'info'
    """Informational suggestions for improvement."""

    OFF = 'off'
    """Disabled rule."""


# Severity ordering for sorting (higher = more severe)
SEVERITY_ORDER: dict[Severity, int] = {
    Severity.ERROR: 3,
    Severity.WARNING: 2,
    Severity.INFO: 1,
    Severity.OFF: 0,
}


@dataclass(frozen=True)
class Violation:
    """A single lint violation found during checking.

    Violations are immutable and hashable, allowing them to be collected
    and deduplicated easily.
    """

    rule_id: str
    """The unique identifier of the rule that generated this violation."""

    message: str
    """Human-readable description of the violation."""

    severity: Severity
    """The severity level of this violation."""

    dashboard_name: str
    """The name of the dashboard where the violation was found."""

    panel_title: str | None = None
    """The title of the panel where the violation was found, if applicable."""

    location: str | None = None
    """Additional location context, e.g., 'panels[2].lens.metrics[0]'."""

    def __lt__(self, other: Violation) -> bool:
        """Compare violations by severity (descending) then dashboard name."""
        if not isinstance(other, Violation):
            return NotImplemented
        # Higher severity comes first
        self_order = SEVERITY_ORDER.get(self.severity, 0)
        other_order = SEVERITY_ORDER.get(other.severity, 0)
        if self_order != other_order:
            return self_order > other_order
        return self.dashboard_name < other.dashboard_name


@dataclass
class RuleResult:
    """Container for violations from a single rule execution."""

    violations: list[Violation] = field(default_factory=list)
    """List of violations found by the rule."""

    def add(self, violation: Violation) -> None:
        """Add a violation to the result.

        Args:
            violation: The violation to add.

        """
        self.violations.append(violation)


class Rule(Protocol):
    """Protocol defining the interface for lint rules.

    All lint rules must implement this protocol to be registered
    and executed by the linting system.
    """

    @property
    def id(self) -> str:
        """Unique identifier for this rule (e.g., 'markdown-header-height')."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what this rule checks."""
        ...

    @property
    def default_severity(self) -> Severity:
        """Default severity level for violations from this rule."""
        ...

    def check(self, dashboard: Dashboard, options: dict[str, Any]) -> list[Violation]:
        """Check a dashboard for violations of this rule.

        Args:
            dashboard: The dashboard to check.
            options: Rule-specific options from configuration.

        Returns:
            List of violations found, may be empty.

        """
        ...
