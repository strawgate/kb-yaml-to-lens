"""Logging utilities for the dashboard compiler."""

import functools
import logging
from collections.abc import Callable
from typing import Any, cast

logger = logging.getLogger('dashboard_compiler')
logger.addHandler(logging.NullHandler())


def log_compile[F: Callable[..., Any]](func: F) -> F:
    """Log function inputs and outputs at DEBUG level.

    Logs the function name, all arguments, and the return value.

    Args:
        func (F): The function to wrap with logging.

    Returns:
        F: The wrapped function with debug logging.

    """

    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        # Build argument string
        arg_parts: list[str] = []
        if len(args) > 0:
            arg_parts.extend(repr(arg) for arg in args)
        if len(kwargs) > 0:
            arg_parts.extend(f'{k}={v!r}' for k, v in kwargs.items())

        args_str = ', '.join(arg_parts)
        logger.debug('Calling %s(%s)', func.__name__, args_str)

        result: object = func(*args, **kwargs)  # pyright: ignore[reportAny]

        logger.debug('%s returned: %r', func.__name__, result)

        return result

    return cast('F', wrapper)
