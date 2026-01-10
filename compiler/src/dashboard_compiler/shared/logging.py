"""Structured logging utilities for the dashboard compiler.

This module provides contextual logging that shows meaningful information about
the compilation process, including dashboard names, panel types, filter counts,
and hierarchical structure.

The logging is designed to be useful for debugging without being overly verbose.
It focuses on WHAT is being compiled rather than raw function entry/exit.
"""

import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import local

# Thread-local storage for indentation tracking
_context = local()


def _get_indent() -> int:
    """Return current indentation level."""
    if not hasattr(_context, 'indent'):
        _context.indent = 0
    return _context.indent


def _set_indent(level: int) -> None:
    """Set current indentation level."""
    _context.indent = level


def _indent_str() -> str:
    """Return indentation string for current level."""
    level = _get_indent()
    if level == 0:
        return ''
    return '│ ' * (level - 1) + '├─ '


@dataclass
class CompilationStats:
    """Track compilation statistics for summary logging."""

    dashboards: int = 0
    panels: int = 0
    filters: int = 0
    controls: int = 0
    panel_types: dict[str, int] = field(default_factory=dict)
    errors: int = 0

    def add_panel_type(self, panel_type: str) -> None:
        """Track a panel type occurrence."""
        self.panel_types[panel_type] = self.panel_types.get(panel_type, 0) + 1

    def summary(self) -> str:
        """Generate a summary string."""
        parts: list[str] = []
        if self.panels > 0:
            panel_breakdown = ', '.join(f'{count} {ptype}' for ptype, count in sorted(self.panel_types.items()))
            parts.append(f'{self.panels} panels ({panel_breakdown})')
        if self.filters > 0:
            parts.append(f'{self.filters} filters')
        if self.controls > 0:
            parts.append(f'{self.controls} controls')
        return ', '.join(parts) if len(parts) > 0 else 'empty dashboard'


# Global stats tracker (reset per compilation) - stored in a container to avoid global statement
_stats_container: dict[str, CompilationStats] = {'current': CompilationStats()}


def reset_stats() -> None:
    """Reset compilation statistics."""
    _stats_container['current'] = CompilationStats()


def get_stats() -> CompilationStats:
    """Return current compilation statistics."""
    return _stats_container['current']


@contextmanager
def log_compilation_phase(
    logger: logging.Logger,
    phase: str,
    context: str = '',
    level: int = logging.DEBUG,
) -> Generator[None, None, None]:
    """Log a compilation phase with timing and context.

    Args:
        logger: Logger instance to use.
        phase: Name of the phase (e.g., "Compiling dashboard").
        context: Additional context (e.g., dashboard name).
        level: Logging level. Defaults to DEBUG.

    Yields:
        None

    Example:
        >>> with log_compilation_phase(logger, "Compiling dashboard", "my-dashboard"):
        >>>     compile_dashboard(dashboard)

        Output:
        ├─ Compiling dashboard 'my-dashboard'...
        │ ├─ Processing 5 panels (3 lens, 1 markdown, 1 links)
        │ ├─ Processing 2 filters
        │ └─ Done (12.5ms)

    """
    indent = _indent_str()
    context_str = f" '{context}'" if len(context) > 0 else ''
    logger.log(level, '%s%s%s...', indent, phase, context_str)

    _set_indent(_get_indent() + 1)
    start = time.perf_counter()

    try:
        yield
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _set_indent(_get_indent() - 1)
        end_indent = _indent_str().replace('├─', '└─')
        logger.exception('%sFailed (%s)', end_indent, f'{elapsed_ms:.1f}ms')
        raise
    else:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _set_indent(_get_indent() - 1)
        end_indent = _indent_str().replace('├─', '└─')
        logger.log(level, '%sDone (%s)', end_indent, f'{elapsed_ms:.1f}ms')


def log_item(
    logger: logging.Logger,
    message: str,
    level: int = logging.DEBUG,
) -> None:
    """Log a single item at the current indentation level.

    Args:
        logger: Logger instance to use.
        message: Message to log.
        level: Logging level. Defaults to DEBUG.

    """
    indent = _indent_str()
    logger.log(level, '%s%s', indent, message)
