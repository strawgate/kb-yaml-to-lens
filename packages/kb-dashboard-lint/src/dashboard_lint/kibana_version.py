"""Helpers for parsing and comparing Kibana versions."""

import re

VERSION_PATTERN = re.compile(r'^\s*(\d+)\.(\d+)(?:\.(\d+))?\s*$')


def parse_kibana_version(version: str) -> tuple[int, int, int] | None:
    """Parse a Kibana version string into a comparable tuple.

    Accepts `major.minor` or `major.minor.patch`.
    Returns None for invalid version formats.
    """
    match = VERSION_PATTERN.match(version)
    if match is None:
        return None

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    return (major, minor, patch)


def version_lt(version: str, minimum: str) -> bool | None:
    """Check if `version` is less than `minimum`.

    Returns:
        True if version < minimum
        False if version >= minimum
        None if either version string cannot be parsed
    """
    parsed_version = parse_kibana_version(version)
    parsed_minimum = parse_kibana_version(minimum)
    if parsed_version is None or parsed_minimum is None:
        return None
    return parsed_version < parsed_minimum
