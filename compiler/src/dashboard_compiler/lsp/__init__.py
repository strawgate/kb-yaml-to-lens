"""LSP (Language Server Protocol) support for dashboard compiler.

This module provides LSP server functionality and grid editing utilities
for the VS Code extension.
"""

from dashboard_compiler.lsp.server import start_server

__all__ = ['start_server']
