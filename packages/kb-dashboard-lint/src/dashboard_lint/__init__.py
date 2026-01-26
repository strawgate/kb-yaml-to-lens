"""Dashboard Lint Package.

A configurable linting system for Kibana dashboard YAML configurations.

Example usage:

    from dashboard_lint import check_dashboards
    from kb_dashboard_core import load

    dashboards = load('inputs/')
    violations = check_dashboards(dashboards)

    for v in violations:
        print(f"{v.severity}: {v.rule_id} - {v.message}")

For advanced usage (custom rules, configuration), import from submodules:
    - dashboard_lint.config: LintConfig, RuleConfig, load_config
    - dashboard_lint.registry: RuleRegistry, default_registry, register_rule
    - dashboard_lint.runner: LintRunner
    - dashboard_lint.types: Rule, RuleResult, SourcePosition, SourceRange, Violation
    - dashboard_lint.rules: Base classes and decorators for custom rules

"""

from beartype import BeartypeConf
from beartype.claw import beartype_this_package

from dashboard_lint.runner import check_dashboards
from dashboard_lint.types import Severity, Violation

# Enable strict BearType checking
beartype_this_package(
    conf=BeartypeConf(
        warning_cls_on_decorator_exception=None,
        claw_is_pep526=True,
    )
)

__all__ = [
    'Severity',
    'Violation',
    'check_dashboards',
]
