"""Rule: ES|QL panels require a minimum Kibana version declaration."""

from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.kibana_version import version_lt
from dashboard_lint.rules.core import DashboardRule, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.base import BasePanel
from kb_dashboard_core.panels.charts.config import ESQLPanel
from kb_dashboard_core.panels.collapsible import CollapsiblePanel


class ESQLMinimumKibanaVersionOptions(BaseModel):
    """Options for the esql-minimum-kibana-version rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    minimum_supported_version: str = Field(
        default='8.14.0',
        description='Minimum Kibana version that supports ES|QL panels',
    )


def _iter_panels(panels: Sequence[BasePanel]) -> list[BasePanel]:
    """Flatten dashboard panels, including panels nested inside sections."""
    flattened: list[BasePanel] = []
    for panel in panels:
        flattened.append(panel)
        if isinstance(panel, CollapsiblePanel):
            flattened.extend(_iter_panels(panel.section.panels))
    return flattened


@dashboard_rule
@dataclass(frozen=True)
class ESQLMinimumKibanaVersionRule(DashboardRule[ESQLMinimumKibanaVersionOptions]):
    """Rule: Dashboards with ES|QL panels should declare a compatible minimum version."""

    id: str = 'esql-minimum-kibana-version'
    description: str = 'Dashboards using ES|QL panels should declare a compatible minimum_kibana_version'
    default_severity: Severity = Severity.WARNING
    options_model: type[ESQLMinimumKibanaVersionOptions] = ESQLMinimumKibanaVersionOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: ESQLMinimumKibanaVersionOptions,
    ) -> ViolationResult:
        """Check ES|QL panel usage against the declared dashboard minimum version."""
        has_esql_panels = any(isinstance(panel, ESQLPanel) for panel in _iter_panels(dashboard.panels))
        if not has_esql_panels:
            return None

        minimum_kibana_version = dashboard.minimum_kibana_version
        if minimum_kibana_version is None:
            return Violation(
                rule_id=self.id,
                message=(
                    'This dashboard uses ES|QL panels but does not declare minimum_kibana_version. '
                    f"Set minimum_kibana_version to at least '{options.minimum_supported_version}'."
                ),
                severity=self.default_severity,
                dashboard_name=dashboard.name,
                panel_title=None,
                location='minimum_kibana_version',
            )

        is_below_minimum = version_lt(minimum_kibana_version, options.minimum_supported_version)
        if is_below_minimum is None:
            return Violation(
                rule_id=self.id,
                message=(
                    f"minimum_kibana_version='{minimum_kibana_version}' is not a valid version. "
                    "Use 'major.minor' or 'major.minor.patch' (for example, '8.14.0')."
                ),
                severity=self.default_severity,
                dashboard_name=dashboard.name,
                panel_title=None,
                location='minimum_kibana_version',
            )

        if is_below_minimum:
            return Violation(
                rule_id=self.id,
                message=(
                    f'ES|QL panels require Kibana >= {options.minimum_supported_version}, '
                    f"but minimum_kibana_version is '{minimum_kibana_version}'."
                ),
                severity=self.default_severity,
                dashboard_name=dashboard.name,
                panel_title=None,
                location='minimum_kibana_version',
            )

        return None
