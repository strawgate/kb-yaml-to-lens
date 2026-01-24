"""Decompilation context and error handling."""

from dataclasses import dataclass, field

from dashboard_compiler.shared.view import KbnReference


@dataclass
class DecompileWarning:
    """A warning generated during decompilation."""

    message: str
    """The warning message."""
    panel_index: int | None = None
    """Optional panel index where the warning occurred."""
    panel_title: str | None = None
    """Optional panel title where the warning occurred."""

    def __str__(self) -> str:
        """Format the warning for display.

        Returns:
            Formatted warning string with context.

        """
        if self.panel_title is not None:
            return f'Panel "{self.panel_title}" (index {self.panel_index}): {self.message}'
        if self.panel_index is not None:
            return f'Panel index {self.panel_index}: {self.message}'
        return self.message


@dataclass
class DecompileContext:
    """Context for decompilation operations."""

    warnings: list[DecompileWarning] = field(default_factory=list)
    """List of warnings accumulated during decompilation."""
    references: list[KbnReference] = field(default_factory=list)
    """Dashboard references for resolving panel dependencies."""
    strict: bool = False
    """If True, raise errors instead of warnings for unsupported features."""

    def warn(
        self,
        message: str,
        *,
        panel_index: int | None = None,
        panel_title: str | None = None,
    ) -> None:
        """Add a warning to the context.

        Args:
            message: The warning message.
            panel_index: Optional panel index for context.
            panel_title: Optional panel title for context.

        Raises:
            DecompileError: If strict mode is enabled.

        """
        warning = DecompileWarning(
            message=message,
            panel_index=panel_index,
            panel_title=panel_title,
        )
        self.warnings.append(warning)

        if self.strict is True:
            raise DecompileError(str(warning))


class DecompileError(Exception):
    """Error raised during decompilation."""
