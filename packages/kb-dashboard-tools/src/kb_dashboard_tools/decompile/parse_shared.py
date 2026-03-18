"""Shared helpers for decompiler parse modules."""

import json
import logging
from typing import Any, cast

logger = logging.getLogger(__name__)


def parse_json_field(raw: str | dict[str, Any] | list[Any] | None) -> dict[str, Any] | list[Any] | None:
    """Parse a field that may be a JSON string or already-parsed object."""
    if raw is None:
        return None
    if isinstance(raw, str):
        try:
            parsed: dict[str, Any] | list[Any] = json.loads(raw)  # pyright: ignore[reportAny]
        except json.JSONDecodeError:
            logger.warning('Failed to decode JSON field in parse_json_field')
            return None
        return parsed
    return raw


def as_dict(value: object) -> dict[str, Any] | None:
    """Safely cast a value to dict if it is one, otherwise return None."""
    if isinstance(value, dict):
        return value  # pyright: ignore[reportUnknownVariableType]
    return None


def as_list(value: object) -> list[object] | None:
    """Safely cast a value to list if it is one, otherwise return None."""
    if isinstance(value, list):
        return cast('list[object]', value)
    return None


def get_dict(source: dict[str, Any], key: str) -> dict[str, Any] | None:
    """Extract a dict-valued key from a dict source."""
    return as_dict(source.get(key))


def get_list(source: dict[str, Any], key: str) -> list[object] | None:
    """Extract a list-valued key from a dict source."""
    return as_list(source.get(key))


def get_str(source: dict[str, Any], key: str) -> str | None:
    """Extract a string-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, str) else None


def get_int(source: dict[str, Any], key: str) -> int | None:
    """Extract an int-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def get_bool(source: dict[str, Any], key: str) -> bool | None:
    """Extract a bool-valued key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, bool) else None


def get_scalar(source: dict[str, Any], key: str) -> str | int | float | bool | None:
    """Extract a scalar (str, int, float, or bool) key from a dict source."""
    value = source.get(key)
    return value if isinstance(value, (str, int, float, bool)) else None


def get_nested(source: dict[str, Any], *keys: str) -> dict[str, Any] | None:
    """Navigate nested dict keys, returning None if any intermediate key is missing or not a dict."""
    current: dict[str, Any] | None = source
    for key in keys:
        if current is None:
            return None
        current = get_dict(current, key)
    return current


def get_number(source: dict[str, Any], key: str) -> int | float | None:
    """Extract a numeric (int or float, not bool) key from a dict source."""
    value = source.get(key)
    if isinstance(value, bool):
        return None
    return value if isinstance(value, (int, float)) else None
