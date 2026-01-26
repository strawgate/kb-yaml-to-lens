"""Rule: Panel titles should not start with redundant prefixes."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_compiler.panels.base import BasePanel
from dashboard_lint.rules.core import PanelContext, PanelRule, ViolationResult, panel_rule
from dashboard_lint.types import Severity, Violation

DEFAULT_PREFIXES: tuple[str, ...] = (
    'Chart of',
    'Graph of',
    'Table of',
    'Count of',
    'List of',
    'Number of',
    'Total of',
    'Sum of',
    'Average of',
)


class PanelTitleRedundantPrefixOptions(BaseModel):
    """Options for the panel-title-redundant-prefix rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    prefixes: list[str] = Field(
        default_factory=lambda: list(DEFAULT_PREFIXES),
        description='List of redundant prefixes to check for (case-insensitive)',
    )


@panel_rule
@dataclass(frozen=True)
class PanelTitleRedundantPrefixRule(PanelRule[BasePanel, PanelTitleRedundantPrefixOptions]):
    """Rule: Panel titles should not start with redundant prefixes.

    Prefixes like "Chart of", "Graph of", or "Table of" add no value since
    the visualization type is already visible. Titles should focus on
    what the data represents, not how it's displayed.

    Example fix:
        Before: "Chart of CPU Usage"
        After:  "CPU Usage"

    Options:
        prefixes (list[str]): Prefixes to check for. Case-insensitive.
            Default: ["Chart of", "Graph of", "Table of", "Count of",
                      "List of", "Number of", "Total of", "Sum of", "Average of"]
    """

    id: str = 'panel-title-redundant-prefix'
    description: str = 'Panel titles should not start with redundant prefixes like "Chart of"'
    default_severity: Severity = Severity.INFO
    options_model: type[PanelTitleRedundantPrefixOptions] = PanelTitleRedundantPrefixOptions

    def check_panel(  # pyright: ignore[reportImplicitOverride]
        self,
        panel: BasePanel,
        context: PanelContext,
        options: PanelTitleRedundantPrefixOptions,
    ) -> ViolationResult:
        """Check panel title for redundant prefixes.

        Args:
            panel: The panel to check.
            context: Panel context with location helpers.
            options: Validated rule options.

        Returns:
            Violation if redundant prefix found, None otherwise.

        """
        # Skip panels without titles
        if len(panel.title) == 0:
            return None

        title_lower = panel.title.lower()

        for prefix in options.prefixes:
            prefix_lower = prefix.lower()
            if title_lower.startswith(prefix_lower):
                # Extract what comes after the prefix for the suggestion
                suggested_title = panel.title[len(prefix) :].strip()
                return Violation(
                    rule_id=self.id,
                    message=f'Panel title starts with redundant prefix "{prefix}"; consider using "{suggested_title}" instead',
                    severity=self.default_severity,
                    dashboard_name=context.dashboard_name,
                    panel_title=context.panel_title,
                    location=context.location('title'),
                )

        return None
