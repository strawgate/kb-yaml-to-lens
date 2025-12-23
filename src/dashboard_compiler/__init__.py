"""Dashboard Compiler Package."""

from beartype import BeartypeConf
from beartype.claw import beartype_this_package

from dashboard_compiler.dashboard_compiler import dump, load, render

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
    'dump',
    'load',
    'render',
]
