"""Core types for the dashboard linting system."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from kb_dashboard_core.dashboard.config import Dashboard


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
class SourcePosition:
    """Represents a position in a YAML source file.

    Line and character are 0-indexed to match LSP specification.
    This allows direct use in Language Server Protocol diagnostics.
    """

    line: int
    """0-indexed line number in the source file."""

    character: int
    """0-indexed character offset within the line."""

    def to_lsp_position(self) -> dict[str, int]:
        """Convert to LSP Position format.

        Returns:
            Dictionary with 'line' and 'character' keys (0-indexed).

        """
        return {'line': self.line, 'character': self.character}


@dataclass(frozen=True)
class SourceRange:
    """Represents a range in a YAML source file for highlighting.

    Uses LSP-compatible format where start is inclusive and end is exclusive.
    """

    start: SourcePosition
    """Start position (inclusive)."""

    end: SourcePosition
    """End position (exclusive)."""

    file_path: str | None = None
    """Optional path to the source file."""

    def to_lsp_range(self) -> dict[str, dict[str, int]]:
        """Convert to LSP Range format.

        Returns:
            Dictionary with 'start' and 'end' positions (0-indexed).

        """
        return {
            'start': self.start.to_lsp_position(),
            'end': self.end.to_lsp_position(),
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

    source_range: SourceRange | None = None
    """Source file position for this violation, if available."""

    def __lt__(self, other: object) -> bool:
        """Compare violations by severity (descending) then dashboard name."""
        if not isinstance(other, Violation):
            return NotImplemented
        # Higher severity comes first
        self_order = SEVERITY_ORDER.get(self.severity, 0)
        other_order = SEVERITY_ORDER.get(other.severity, 0)
        if self_order != other_order:
            return self_order > other_order
        return self.dashboard_name < other.dashboard_name

    def with_source_range(self, source_range: SourceRange) -> 'Violation':
        """Create a copy of this violation with source position information.

        Args:
            source_range: The source range to add.

        Returns:
            A new Violation with the source range set.

        """
        return Violation(
            rule_id=self.rule_id,
            message=self.message,
            severity=self.severity,
            dashboard_name=self.dashboard_name,
            panel_title=self.panel_title,
            location=self.location,
            source_range=source_range,
        )


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
