"""Dashboard Lint Package.

A configurable linting system for Kibana dashboard YAML configurations.

Example usage:

    from dashboard_lint import check_dashboards
    from dashboard_compiler import load

    dashboards = load('inputs/')
    violations = check_dashboards(dashboards)

    for v in violations:
        print(f"{v.severity}: {v.rule_id} - {v.message}")

"""

from beartype import BeartypeConf
from beartype.claw import beartype_this_package

from dashboard_lint.config import LintConfig, RuleConfig, load_config
from dashboard_lint.registry import RuleRegistry, default_registry, register_rule
from dashboard_lint.runner import LintRunner, check_dashboards
from dashboard_lint.types import Rule, RuleResult, Severity, Violation

# Enable strict BearType checking
beartype_this_package(
    conf=BeartypeConf(
        warning_cls_on_decorator_exception=None,
        claw_is_pep526=True,
    )
)

__all__ = [
    'LintConfig',
    'LintRunner',
    'Rule',
    'RuleConfig',
    'RuleRegistry',
    'RuleResult',
    'Severity',
    'Violation',
    'check_dashboards',
    'default_registry',
    'load_config',
    'register_rule',
]
