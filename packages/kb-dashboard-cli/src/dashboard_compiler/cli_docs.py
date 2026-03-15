"""CLI commands for accessing bundled documentation.

This module provides CLI access to LLM documentation content bundled in the
kb-dashboard-docs package.
"""

import rich_click as click

from dashboard_compiler.cli_output import print_error, print_plain


@click.group(invoke_without_command=True)
@click.pass_context
def docs(ctx: click.Context) -> None:
    r"""Access bundled LLM documentation.

    \b
    Examples:
        kb-dashboard docs list-guides        # List available guides
        kb-dashboard docs llms-full          # Output full documentation
        kb-dashboard docs llms-full | pbcopy # Copy to clipboard (macOS)
        kb-dashboard docs guide otel         # Get specific guide
    """
    if ctx.invoked_subcommand is None:
        print_plain(ctx.get_help())


@docs.command(name='llms-full')
def llms_full() -> None:
    """Output bundled llms-full documentation content."""
    try:
        from kb_dashboard_docs import get_full_docs

        content = get_full_docs()
        print_plain(content)
    except FileNotFoundError:
        print_error('Documentation not bundled. This may indicate an installation issue.')
        raise SystemExit(1) from None
    except ImportError:
        print_error('kb-dashboard-docs package not installed.')
        raise SystemExit(1) from None


@docs.command(name='list-guides')
def list_guides() -> None:
    """List available workflow guides.

    Displays names of bundled guides that can be accessed with the
    'guide' subcommand.
    """
    try:
        from kb_dashboard_docs import list_guides as do_list_guides

        guides = do_list_guides()
        if len(guides) == 0:
            print_plain('No guides bundled.')
            return

        print_plain('Available guides:\n')
        for guide in guides:
            print_plain(f'  {guide}')
    except ImportError:
        print_error('kb-dashboard-docs package not installed.')
        raise SystemExit(1) from None


@docs.command(name='guide')
@click.argument('name')
def get_guide(name: str) -> None:
    r"""Output a specific workflow guide.

    NAME is the guide name (with or without .md extension).

    \b
    Examples:
        kb-dashboard docs guide otel-dashboard-guide
        kb-dashboard docs guide breaking-changes
        kb-dashboard docs guide esql-language-reference
        kb-dashboard docs guide dashboard-style-guide
    """
    try:
        from kb_dashboard_docs import get_guide as do_get_guide

        content = do_get_guide(name)
        print_plain(content)
    except FileNotFoundError as e:
        print_error(str(e))
        raise SystemExit(1) from None
    except ImportError:
        print_error('kb-dashboard-docs package not installed.')
        raise SystemExit(1) from None
