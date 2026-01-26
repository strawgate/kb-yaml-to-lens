"""Centralized CLI output helpers for consistent messaging and formatting."""

import os
import sys

from kb_dashboard_tools.kibana_client import SavedObjectError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Initialize shared console
console = Console()

# Use ASCII fallbacks on Windows to avoid encoding errors with cp1252
# The Windows console uses cp1252 by default which cannot encode Unicode symbols
_USE_ASCII_ICONS = sys.platform == 'win32' and os.environ.get('PYTHONUTF8') != '1'

ICON_SUCCESS = '[OK]' if _USE_ASCII_ICONS else '✓'
ICON_ERROR = '[X]' if _USE_ASCII_ICONS else '✗'
ICON_WARNING = '[!]' if _USE_ASCII_ICONS else '⚠'
ICON_UPLOAD = '[^]' if _USE_ASCII_ICONS else '📤'
ICON_DOWNLOAD = '[v]' if _USE_ASCII_ICONS else '📥'
ICON_BROWSER = '[>]' if _USE_ASCII_ICONS else '🌐'


def print_success(message: str) -> None:
    """Print a success message with green checkmark icon.

    The icon is styled green while the message text remains default.

    Args:
        message: The message to display.

    """
    console.print(f'[green]{ICON_SUCCESS}[/green] {message}')


def print_error(message: str) -> None:
    """Print an error message with red X icon.

    The icon is styled red while the message text remains default.

    Args:
        message: The message to display.

    """
    console.print(f'[red]{ICON_ERROR}[/red] {message}')


def print_warning(message: str) -> None:
    """Print a warning message with yellow warning icon.

    The icon is styled yellow while the message text remains default.

    Args:
        message: The message to display.

    """
    console.print(f'[yellow]{ICON_WARNING}[/yellow] {message}')


def print_info(message: str, icon: str | None = None) -> None:
    """Print an info message with optional custom icon.

    Args:
        message: The message to display.
        icon: Optional icon to use (defaults to blue color, no icon).

    """
    if icon is not None:
        console.print(f'[blue]{icon}[/blue] {message}')
    else:
        console.print(f'[blue]{message}[/blue]')


def print_upload(message: str) -> None:
    """Print an upload status message.

    Args:
        message: The message to display.

    """
    print_info(message, ICON_UPLOAD)


def print_download(message: str) -> None:
    """Print a download status message.

    Args:
        message: The message to display.

    """
    print_info(message, ICON_DOWNLOAD)


def print_browser(message: str) -> None:
    """Print a browser-related message.

    Args:
        message: The message to display.

    """
    print_info(message, ICON_BROWSER)


def print_detail(message: str, indent: int = 2) -> None:
    """Print a detail line with indentation.

    Args:
        message: The message to display.
        indent: Number of spaces to indent (default: 2).

    """
    prefix = ' ' * indent
    console.print(f'{prefix}{message}')


def print_bullet(message: str, style: str = 'red') -> None:
    """Print a bulleted list item.

    Args:
        message: The message to display.
        style: Color style for the text (default: red for errors).

    """
    console.print(f'  [{style}]•[/{style}] {message}', style=style)


def print_dim_bullet(message: str) -> None:
    """Print a dim bulleted list item for secondary information.

    Args:
        message: The message to display.

    """
    console.print(f'  [dim]•[/dim] {message}')


def print_plain(message: str, style: str | None = None) -> None:
    """Print a plain message with optional style.

    Args:
        message: The message to display.
        style: Optional Rich style to apply.

    """
    if style is not None:
        console.print(message, style=style)
    else:
        console.print(message)


def create_progress() -> Progress:
    """Create a configured Progress context manager for spinner-based progress.

    Returns:
        A Progress instance with spinner and text columns.

    Example:
        with create_progress() as progress:
            task = progress.add_task('Processing...', total=None)
            # do work
            progress.update(task, description='Done!')

    """
    return Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        console=console,
    )


def create_error_table(errors: list[SavedObjectError]) -> Table:
    """Create a Rich table to display errors.

    Args:
        errors: List of SavedObjectError instances from Kibana API.

    Returns:
        A formatted Rich table with error messages.

    """
    error_table = Table(show_header=True, header_style='bold red')
    error_table.add_column('Error', style='red')

    for error in errors:
        error_table.add_row(error.get_error_message())

    return error_table
