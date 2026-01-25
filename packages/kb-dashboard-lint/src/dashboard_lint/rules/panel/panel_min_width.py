"""Rule: Panels should have minimum width for readability."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_lint.rules.core import PanelContext, PanelRule, ViolationResult, panel_rule
from dashboard_lint.types import Severity, Violation


class PanelMinWidthOptions(BaseModel):
    """Options for the panel-min-width rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    min_width: int = Field(default=6, ge=1, description='Minimum width in grid units')


@panel_rule
@dataclass(frozen=True)
class PanelMinWidthRule(PanelRule[BasePanel, PanelMinWidthOptions]):
    """Rule: Panels should have minimum width for readability.

    Very narrow panels (less than 6 grid units) are often too small to
    display content effectively and may indicate a configuration error.

    Options:
        min_width (int): Minimum width in grid units. Default: 6.
    """

    id: str = 'panel-min-width'
    description: str = 'Panels should have minimum width for readability'
    default_severity: Severity = Severity.WARNING
    options_model: type[PanelMinWidthOptions] = PanelMinWidthOptions

    def check_panel(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: BasePanel,
        context: PanelContext,
        options: PanelMinWidthOptions,
    ) -> ViolationResult:
        """Check panel for insufficient width.

        Args:
            panel: The panel to check.
            context: Panel context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if width below minimum, None otherwise.

        """
        # Use .width property which resolves semantic widths to integers
        width = panel.size.width

        if width < options.min_width:
            return Violation(
                rule_id=self.id,
                message=f'Panel width {width} is below minimum {options.min_width}; narrow panels may be hard to read',
                severity=self.default_severity,
                dashboard_name=context.dashboard_name,
                panel_title=context.panel_title,
                location=context.location('size'),
            )

        return None
