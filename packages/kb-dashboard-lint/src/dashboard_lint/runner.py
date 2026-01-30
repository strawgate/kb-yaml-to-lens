"""Lint runner for orchestrating rule execution."""

from dashboard_lint.config import LintConfig, get_effective_config
from dashboard_lint.registry import RuleRegistry, default_registry
from dashboard_lint.types import Violation
from kb_dashboard_core.dashboard.config import Dashboard


class LintRunner:
    """Orchestrates lint rule execution across dashboards.

    The runner manages rule discovery, configuration merging, and
    violation collection.
    """

    def __init__(
        self,
        registry: RuleRegistry | None = None,
        config: LintConfig | None = None,
    ) -> None:
        """Initialize the lint runner.

        Args:
            registry: Rule registry to use. Defaults to the global registry.
            config: Lint configuration. Defaults to empty configuration.

        """
        self._registry: RuleRegistry = registry if registry is not None else default_registry
        self._config: LintConfig = config if config is not None else LintConfig()

    def run(self, dashboards: list[Dashboard]) -> list[Violation]:
        """Run all enabled rules against the provided dashboards.

        Args:
            dashboards: List of dashboards to check.

        Returns:
            Sorted list of violations found across all dashboards.

        """
        violations: list[Violation] = []

        for rule in self._registry.get_all_rules():
            enabled, severity, options = get_effective_config(
                rule.id,
                self._config,
                rule.default_severity,
            )

            if not enabled:
                continue

            for dashboard in dashboards:
                rule_violations = rule.check(dashboard, options)

                # Apply configured severity override and collect violations
                for v in rule_violations:
                    if v.severity != severity:
                        # Create a new violation with the configured severity
                        violations.append(
                            Violation(
                                rule_id=v.rule_id,
                                message=v.message,
                                severity=severity,
                                dashboard_name=v.dashboard_name,
                                panel_title=v.panel_title,
                                location=v.location,
                                source_range=v.source_range,
                            )
                        )
                    else:
                        violations.append(v)

        # Sort by severity (descending) then dashboard name
        return sorted(violations)


def check_dashboards(
    dashboards: list[Dashboard],
    config: LintConfig | None = None,
) -> list[Violation]:
    """Check dashboards for lint violations using the default registry.

    Args:
        dashboards: List of dashboards to check.
        config: Optional lint configuration.

    Returns:
        Sorted list of violations found.

    """
    runner = LintRunner(config=config)
    return runner.run(dashboards)
