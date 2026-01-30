"""User-friendly formatting for Pydantic validation errors.

This module provides utilities to convert Pydantic's ValidationError into
human-readable error messages suitable for CLI output.

Based on patterns from https://docs.pydantic.dev/latest/errors/errors/
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from pydantic_core import ErrorDetails

# Custom messages for common error types, with optional {context} placeholders
CUSTOM_MESSAGES: dict[str, str] = {
    # Root-level errors
    'model_type': 'File is empty or invalid. Expected a YAML document with a "dashboards" key.',
    # Missing fields
    'missing': 'Field is required',
    # Type errors
    'string_type': 'Expected a string value',
    'int_type': 'Expected an integer value',
    'bool_type': 'Expected true or false',
    'list_type': 'Expected a list',
    'dict_type': 'Expected a mapping/dictionary',
    # Value errors
    'value_error': '{message}',
    # Union/discriminator errors
    'union_tag_invalid': "Unknown type '{tag}'. Valid types: {expected_tags}",
    # Constraint errors
    'greater_than_equal': 'Value must be >= {ge}',
    'less_than_equal': 'Value must be <= {le}',
    'string_too_short': 'String must have at least {min_length} characters',
    'string_too_long': 'String must have at most {max_length} characters',
}

# Special handling for specific field paths (loc tuples)
FIELD_HINTS: dict[tuple[str, ...], str] = {
    ('dashboards',): 'Your YAML file must have a "dashboards:" section at the top level.',
    ('dashboards', 'name'): 'Each dashboard requires a "name" field.',
}


def loc_to_path(loc: tuple[str | int, ...]) -> str:
    """Convert a Pydantic error location tuple to a readable dot-separated path.

    Args:
        loc: Error location as a tuple, e.g., ('dashboards', 0, 'panels', 1, 'grid')

    Returns:
        A readable path string, e.g., 'dashboards[0].panels[1].grid'

    Examples:
        >>> loc_to_path(('dashboards', 0, 'name'))
        'dashboards[0].name'
        >>> loc_to_path(('dashboards',))
        'dashboards'
        >>> loc_to_path(())
        '<root>'
        >>> loc_to_path(('dashboards', 0, 'panels', 0, 'markdown', 'markdown', 'content'))
        'dashboards[0].panels[0].markdown.content'

    """
    if len(loc) == 0:
        return '<root>'

    parts: list[str] = []
    prev_str: str | None = None

    for item in loc:
        if isinstance(item, int):
            parts.append(f'[{item}]')
            prev_str = None
        else:
            # item is str
            # Skip consecutive duplicate string segments (e.g., 'markdown', 'markdown')
            if item == prev_str:
                continue

            # Add dot separator if there's a previous part
            if len(parts) > 0:
                parts.append('.')
            parts.append(item)
            prev_str = item

    return ''.join(parts)


def get_field_key(loc: tuple[str | int, ...]) -> tuple[str, ...]:
    """Extract string-only field path for hint lookup.

    Args:
        loc: Error location tuple

    Returns:
        Tuple of string field names only (indices removed)

    """
    return tuple(part for part in loc if isinstance(part, str))


def format_error_message(error: ErrorDetails) -> str:
    """Format a single Pydantic error dict into a user-friendly message.

    Args:
        error: A single error dict from ValidationError.errors()

    Returns:
        Formatted error message string

    """
    error_type: str = error['type']
    loc: tuple[str | int, ...] = error['loc']
    msg: str = error['msg']
    ctx: dict[str, Any] | None = error.get('ctx')

    # Try to get a custom message for this error type
    custom_msg = CUSTOM_MESSAGES.get(error_type)
    if custom_msg is not None:
        if ctx is not None:
            try:
                # Handle special case where 'message' is in ctx (for value_error)
                if 'message' in ctx:
                    ctx_message: str = ctx['message']  # pyright: ignore[reportAny]
                    msg = ctx_message
                else:
                    msg = custom_msg.format(**ctx)  # pyright: ignore[reportAny]
            except KeyError:
                msg = custom_msg
        else:
            msg = custom_msg

    # Add field hint if available
    field_key = get_field_key(loc)
    hint = FIELD_HINTS.get(field_key)
    if hint is not None:
        msg = f'{msg}. {hint}'

    return msg


def format_validation_error(e: ValidationError, file_path: Path | None = None) -> str:
    """Format a Pydantic ValidationError into a user-friendly message.

    Args:
        e: The ValidationError from Pydantic
        file_path: Optional path to the file being validated (for context)

    Returns:
        A formatted multi-line error message string

    """
    errors = e.errors()
    error_count = len(errors)
    file_context = f' in {file_path.name}' if file_path is not None else ''

    # Special case: single root-level model_type error (empty/invalid file)
    if error_count == 1 and errors[0]['loc'] == () and errors[0]['type'] == 'model_type':
        msg = format_error_message(errors[0])
        if file_path is not None:
            return f'{file_path.name}: {msg}'
        return msg

    # Special case: single missing 'dashboards' key
    if error_count == 1 and errors[0]['loc'] == ('dashboards',) and errors[0]['type'] == 'missing':
        msg = format_error_message(errors[0])
        if file_path is not None:
            return f'{file_path.name}: {msg}'
        return msg

    # General case: format each error
    error_word = 'error' if error_count == 1 else 'errors'
    lines = [f'{error_count} validation {error_word}{file_context}:']

    for error in errors:
        loc = error['loc']
        path = loc_to_path(loc)
        msg = format_error_message(error)
        lines.append(f'  • {path}: {msg}')

    return '\n'.join(lines)


def format_yaml_error(e: yaml.YAMLError, file_path: Path | None = None) -> str:
    """Format a YAML parsing error into a user-friendly message.

    Args:
        e: The YAMLError from the yaml library
        file_path: Optional path to the file being parsed (for context)

    Returns:
        A formatted error message string

    """
    file_context = file_path.name if file_path is not None else 'YAML'

    # yaml.YAMLError subclasses set problem_mark/problem dynamically
    problem_mark = getattr(e, 'problem_mark', None)
    if problem_mark is not None:
        line: int = getattr(problem_mark, 'line', -1) + 1  # pyright: ignore[reportAny]
        column: int = getattr(problem_mark, 'column', -1) + 1  # pyright: ignore[reportAny]
        problem: str = getattr(e, 'problem', 'syntax error')
        return f'YAML syntax error in {file_context} at line {line}, column {column}: {problem}'

    return f'YAML syntax error in {file_context}: {e}'
