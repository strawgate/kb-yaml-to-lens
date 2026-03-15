"""Rule: Collapsible panels require a minimum Kibana version."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from dashboard_lint.kibana_version import version_lt
from dashboard_lint.rules.core import DashboardRule, ViolationResult, dashboard_rule
from dashboard_lint.types import Severity, Violation
from kb_dashboard_core.dashboard.config import Dashboard
from kb_dashboard_core.panels.collapsible import CollapsiblePanel


class CollapsibleMinimumKibanaVersionOptions(BaseModel):
    """Options for the collapsible-minimum-kibana-version rule."""

    model_config: dict[str, object] = {'extra': 'forbid', 'frozen': True, 'validate_default': True}

    minimum_supported_version: str = Field(
        default='9.1.0',
        description='Minimum Kibana version that supports collapsible section panels',
    )


@dashboard_rule
@dataclass(frozen=True)
class CollapsibleMinimumKibanaVersionRule(DashboardRule[CollapsibleMinimumKibanaVersionOptions]):
    """Rule: Collapsible panels require a sufficient dashboard minimum Kibana version."""

    id: str = 'collapsible-minimum-kibana-version'
    description: str = 'Dashboards using section panels should declare a compatible minimum_kibana_version'
    default_severity: Severity = Severity.WARNING
    options_model: type[CollapsibleMinimumKibanaVersionOptions] = CollapsibleMinimumKibanaVersionOptions

    def check_dashboard(  # pyright: ignore[reportImplicitOverride]
        self,
        dashboard: Dashboard,
        options: CollapsibleMinimumKibanaVersionOptions,
    ) -> ViolationResult:
        """Check section panels against the declared dashboard minimum version."""
        if not any(isinstance(panel, CollapsiblePanel) for panel in dashboard.panels):
            return None

        minimum_kibana_version = dashboard.minimum_kibana_version
        if minimum_kibana_version is None:
            return Violation(
                rule_id=self.id,
                message=(
                    'This dashboard uses section panels but does not declare minimum_kibana_version. '
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
                    "Use 'major.minor' or 'major.minor.patch' (for example, '9.1.0')."
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
                    f'Section panels require Kibana >= {options.minimum_supported_version}, '
                    f"but minimum_kibana_version is '{minimum_kibana_version}'."
                ),
                severity=self.default_severity,
                dashboard_name=dashboard.name,
                panel_title=None,
                location='minimum_kibana_version',
            )

        return None
