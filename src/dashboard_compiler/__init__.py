"""Dashboard Compiler Package."""

from beartype.claw import beartype_this_package

from dashboard_compiler.dashboard_compiler import dump, load, render

beartype_this_package()

__all__ = [
    'dump',
    'load',
    'render',
]
