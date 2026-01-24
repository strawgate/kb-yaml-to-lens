"""
kb-dashboard-compiler meta-package.

This package provides backwards compatibility by re-exporting the main API
from kb-dashboard-core, kb-dashboard-cli, and kb-dashboard-tools.

For new code, prefer importing directly from the specific packages:
- `from kb_dashboard.core import load, render, dump`
- `from kb_dashboard.cli import cli`
- `from kb_dashboard.tools import disassemble_dashboard`
"""

# Re-export the main API for backwards compatibility
from kb_dashboard.core import dump, load, render

__all__ = [
    "dump",
    "load",
    "render",
]
