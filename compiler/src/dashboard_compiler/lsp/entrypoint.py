"""Backward compatibility entrypoint for kb-dashboard-lsp.

This module provides a guarded entry point that checks for optional LSP dependencies
before attempting to start the LSP server. This prevents ImportError crashes when
the kb-dashboard-lsp entry point is invoked without LSP extras installed.

DEPRECATED: This entry point is deprecated. Use 'kb-dashboard lsp' instead.
"""

import sys


def main() -> None:
    """Entry point for kb-dashboard-lsp (deprecated).

    Prints deprecation warning and attempts to start the LSP server.
    If LSP dependencies are not installed, provides installation instructions.
    """
    # Print deprecation warning to stderr
    print(
        'Warning: kb-dashboard-lsp is deprecated. Use "kb-dashboard lsp" instead.',
        file=sys.stderr,
    )

    # Try to import and run the LSP server
    try:
        from dashboard_compiler.lsp.server import main as lsp_main

        lsp_main()
    except ImportError as e:
        print('Error: LSP server dependencies not installed.', file=sys.stderr)
        print('Install with: uv sync --extra lsp', file=sys.stderr)
        print(f'Import error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
