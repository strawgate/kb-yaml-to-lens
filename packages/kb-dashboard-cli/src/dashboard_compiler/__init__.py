"""Dashboard CLI Package - CLI, LSP, and future MCP server for kb-yaml-to-lens."""

from beartype import BeartypeConf
from beartype.claw import beartype_this_package
from kb_dashboard_core.dashboard_compiler import dump, load, render
from kb_dashboard_tools import KibanaClient

# Enable strict BearType checking:
# - warning_cls_on_decorator_exception=None: Raises fatal exceptions instead of warnings
# - claw_is_pep526=True: Type-check annotated variable assignments (default, explicit for clarity)
beartype_this_package(
    conf=BeartypeConf(
        warning_cls_on_decorator_exception=None,
        claw_is_pep526=True,
    )
)

__all__ = [
    'KibanaClient',
    'dump',
    'load',
    'render',
]
