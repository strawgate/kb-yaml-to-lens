"""ES|QL query parsing helpers for lint rules.

This module provides utilities for analyzing ES|QL queries in lint rules.
"""

import re

from kb_dashboard_core.panels.charts.config import (
    ESQLAreaPanelConfig,
    ESQLBarPanelConfig,
    ESQLDatatablePanelConfig,
    ESQLGaugePanelConfig,
    ESQLHeatmapPanelConfig,
    ESQLLinePanelConfig,
    ESQLMetricPanelConfig,
    ESQLMosaicPanelConfig,
    ESQLPiePanelConfig,
    ESQLTagcloudPanelConfig,
)
from kb_dashboard_core.queries.config import ESQLQuery

type ESQLConfig = (
    ESQLMetricPanelConfig
    | ESQLGaugePanelConfig
    | ESQLHeatmapPanelConfig
    | ESQLPiePanelConfig
    | ESQLLinePanelConfig
    | ESQLBarPanelConfig
    | ESQLAreaPanelConfig
    | ESQLTagcloudPanelConfig
    | ESQLDatatablePanelConfig
    | ESQLMosaicPanelConfig
)
"""Union type for all ES|QL panel configuration types."""


def get_query_string(query: ESQLQuery) -> str:
    """Extract query string from an ESQLQuery.

    Args:
        query: Query object with 'root' attribute containing the query.

    Returns:
        Single string with the full query.

    """
    root = query.root
    if isinstance(root, list):
        return '\n'.join(str(part) for part in root)
    return str(root)


def split_into_commands(query: str) -> list[str]:
    """Split ES|QL query on pipes, respecting quoted strings and escapes.

    Args:
        query: The ES|QL query string.

    Returns:
        List of command segments (trimmed), split on unquoted pipe characters.

    """
    commands: list[str] = []
    current: list[str] = []
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    i = 0

    while i < len(query):
        char = query[i]

        # Handle escape sequences
        if char == '\\' and i + 1 < len(query):
            current.append(char)
            current.append(query[i + 1])
            i += 2
            continue

        # Track quote state
        if char == "'" and not in_double_quote and not in_backtick:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote and not in_backtick:
            in_double_quote = not in_double_quote
        elif char == '`' and not in_single_quote and not in_double_quote:
            in_backtick = not in_backtick
        elif char == '|' and not in_single_quote and not in_double_quote and not in_backtick:
            segment = ''.join(current).strip()
            if segment:
                commands.append(segment)
            current = []
            i += 1
            continue

        current.append(char)
        i += 1

    # Don't forget the last segment
    segment = ''.join(current).strip()
    if segment:
        commands.append(segment)

    return commands


# Regex patterns for detecting various ES|QL issues

# WHERE pattern (needed for SINGLE_EQUALS_IN_WHERE_PATTERN)
WHERE_PATTERN = re.compile(r'\bWHERE\b', re.IGNORECASE)
"""Detects WHERE clause in ES|QL queries (used internally for single equals detection)."""

BUCKET_PATTERN = re.compile(
    r'\bBUCKET\s*\(\s*[`"]?@?[a-zA-Z_][\w.]*[`"]?\s*,',
    re.IGNORECASE,
)
"""Detects BUCKET function calls with time field."""

# Pattern for single = in WHERE comparison context (not ==, !=, <=, >=)
# This is a more targeted pattern that looks for WHERE followed by a comparison with single =
# Avoids matching assignment operators in STATS, EVAL, etc.
# Supports dotted fields (host.name), backticked fields (`field.name`), and @-prefixed fields (@timestamp)
SINGLE_EQUALS_IN_WHERE_PATTERN = re.compile(
    r'\bWHERE\b[^|]*?(`[^`]+`|@?[a-zA-Z_][\w.]*)\s*(?<![!<>])=(?!=)',
    re.IGNORECASE,
)
"""Detects single = for equality in WHERE clauses (should be == in ES|QL)."""

# Pattern for SQL-style LIKE wildcards
SQL_LIKE_WILDCARD_PATTERN = re.compile(r"LIKE\s+['\"][^'\"]*%[^'\"]*['\"]", re.IGNORECASE)
"""Detects LIKE with % wildcard (should use * in ES|QL)."""

# Fixed time bucket patterns
# Matches: BUCKET(@timestamp, 1 minute), BUCKET(`@timestamp`, 5 minutes), BUCKET(event.ingested, 1 hour), etc.
# Accepts any field name (dotted, backticked, or @-prefixed) to catch fixed buckets on custom time fields
FIXED_BUCKET_PATTERN = re.compile(
    r'BUCKET\s*\(\s*[`"]?@?[a-zA-Z_][\w.]*[`"]?\s*,\s*\d+\s+(?:second|minute|hour|day|week|month|year)s?\s*\)',
    re.IGNORECASE,
)
"""Detects fixed interval BUCKET(field, N units) patterns on any field."""

# Matches: TBUCKET(5 minutes), TBUCKET(1 hour), etc.
TBUCKET_FIXED_PATTERN = re.compile(
    r'TBUCKET\s*\(\s*\d+\s+(?:second|minute|hour|day|week|month|year)s?\s*\)',
    re.IGNORECASE,
)
"""Detects fixed interval TBUCKET(N units) patterns."""

# Field escaping patterns
# Matches fields ending with a number that need backticks: apache.load.1, system.cpu.0
# Should not match: properly escaped `apache.load.1`
UNESCAPED_NUMERIC_FIELD_PATTERN = re.compile(
    r'(?<![`\w])([a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*\.\d+)(?![`\w])',
)
"""Detects field names ending with numbers that need backtick escaping."""


# Command-based checking helpers
# These functions split queries into commands and check them individually,
# avoiding false positives from string literals or comments.


def _strip_quoted_sections(text: str) -> str:
    """Remove quoted sections from text to avoid false positives.

    This removes content between single quotes, double quotes, and backticks,
    replacing them with spaces to preserve word boundaries.

    Args:
        text: Text to process.

    Returns:
        Text with quoted sections removed.

    """
    result: list[str] = []
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    i = 0

    while i < len(text):
        char = text[i]

        # Handle escape sequences
        if char == '\\' and i + 1 < len(text):
            if not (in_single_quote or in_double_quote or in_backtick):
                result.append(char)
                result.append(text[i + 1])
            i += 2
            continue

        # Track quote state
        if char == "'" and not in_double_quote and not in_backtick:
            in_single_quote = not in_single_quote
            result.append(' ')  # Replace quote with space
        elif char == '"' and not in_single_quote and not in_backtick:
            in_double_quote = not in_double_quote
            result.append(' ')  # Replace quote with space
        elif char == '`' and not in_single_quote and not in_double_quote:
            in_backtick = not in_backtick
            result.append(' ')  # Replace quote with space
        elif not (in_single_quote or in_double_quote or in_backtick):
            result.append(char)
        else:
            result.append(' ')  # Replace quoted content with space

        i += 1

    return ''.join(result)


def has_command_containing(query: str, pattern: re.Pattern[str]) -> bool:
    r"""Check if any command in the query contains the given pattern.

    This splits the query into commands (respecting quoted strings) and
    checks each command individually, avoiding false positives from
    patterns appearing in string literals.

    Args:
        query: The ES|QL query string.
        pattern: Compiled regex pattern to search for.

    Returns:
        True if any command contains the pattern, False otherwise.

    Example:
        >>> import re
        >>> pattern = re.compile(r'\bBUCKET\b', re.IGNORECASE)
        >>> has_command_containing("FROM logs-* | STATS count BY bucket = BUCKET(@timestamp)", pattern)
        True
        >>> has_command_containing("FROM logs-* | WHERE msg = 'BUCKET example'", pattern)
        False  # BUCKET is in a string literal, not a command

    """
    commands = split_into_commands(query)
    for command in commands:
        # Strip quoted sections to avoid false positives
        unquoted = _strip_quoted_sections(command)
        if pattern.search(unquoted):
            return True
    return False


def has_command_starting_with(query: str, keyword: str) -> bool:
    """Check if any command in the query starts with the given keyword.

    This splits the query into commands and checks if any command starts
    with the keyword (case-insensitive), avoiding false positives from
    keywords appearing in string literals.

    Args:
        query: The ES|QL query string.
        keyword: Keyword to check for (e.g., "SORT", "LIMIT").

    Returns:
        True if any command starts with the keyword, False otherwise.

    Example:
        >>> has_command_starting_with("FROM logs-* | SORT @timestamp", "SORT")
        True
        >>> has_command_starting_with("FROM logs-* | WHERE msg = 'SORT example'", "SORT")
        False  # SORT is in a string literal, not a command

    """
    commands = split_into_commands(query)
    keyword_lower = keyword.lower()
    return any(command.strip().lower().startswith(keyword_lower) for command in commands)


def first_command_starts_with(query: str, keyword: str) -> bool:
    """Check if the first command starts with the given keyword.

    This is useful for checking query structure (e.g., queries should
    start with FROM, not SELECT).

    Args:
        query: The ES|QL query string.
        keyword: Keyword to check for (e.g., "FROM", "SELECT").

    Returns:
        True if the first command starts with the keyword, False otherwise.

    Example:
        >>> first_command_starts_with("FROM logs-* | STATS count", "FROM")
        True
        >>> first_command_starts_with("SELECT * FROM logs", "SELECT")
        True

    """
    commands = split_into_commands(query)
    if len(commands) == 0:
        return False
    return commands[0].strip().lower().startswith(keyword.lower())


def last_command_starts_with(query: str, keyword: str) -> bool:
    """Check if the last command starts with the given keyword.

    This is useful for checking query structure (e.g., queries with
    BUCKET should end with SORT).

    Args:
        query: The ES|QL query string.
        keyword: Keyword to check for (e.g., "SORT", "LIMIT").

    Returns:
        True if the last command starts with the keyword, False otherwise.

    Example:
        >>> last_command_starts_with("FROM logs-* | STATS count BY bucket | SORT bucket", "SORT")
        True
        >>> last_command_starts_with("FROM logs-* | STATS count", "SORT")
        False

    """
    commands = split_into_commands(query)
    if len(commands) == 0:
        return False
    return commands[-1].strip().lower().startswith(keyword.lower())


def has_sort_desc_command(query: str) -> bool:
    """Check if any command is a SORT with DESC.

    This checks if any command starts with SORT and contains DESC,
    avoiding false positives from DESC appearing in string literals.

    Args:
        query: The ES|QL query string.

    Returns:
        True if any command is SORT ... DESC, False otherwise.

    Example:
        >>> has_sort_desc_command("FROM logs-* | SORT count DESC")
        True
        >>> has_sort_desc_command("FROM logs-* | SORT count ASC")
        False

    """
    commands = split_into_commands(query)
    desc_pattern = re.compile(r'\bDESC\b', re.IGNORECASE)
    for command in commands:
        command_lower = command.strip().lower()
        if command_lower.startswith('sort') and desc_pattern.search(command):
            return True
    return False


def has_order_by(query: str) -> bool:
    """Check if query contains SQL ORDER BY syntax.

    ORDER BY is SQL syntax and should not appear in ES|QL queries.
    ES|QL uses SORT instead.

    Args:
        query: The ES|QL query string.

    Returns:
        True if ORDER BY is found in any command, False otherwise.

    Example:
        >>> has_order_by("FROM logs-* | ORDER BY @timestamp")
        True
        >>> has_order_by("FROM logs-* | WHERE msg = 'ORDER BY example'")
        False  # ORDER BY is in a string literal

    """
    commands = split_into_commands(query)
    for command in commands:
        unquoted = _strip_quoted_sections(command)
        if 'order by' in unquoted.lower():
            return True
    return False


def has_group_by(query: str) -> bool:
    """Check if query contains SQL GROUP BY syntax.

    GROUP BY is SQL syntax and should not appear in ES|QL queries.
    ES|QL uses BY within STATS instead.

    Args:
        query: The ES|QL query string.

    Returns:
        True if GROUP BY is found in any command, False otherwise.

    Example:
        >>> has_group_by("FROM logs-* | STATS count GROUP BY host.name")
        True
        >>> has_group_by("FROM logs-* | WHERE msg = 'GROUP BY example'")
        False  # GROUP BY is in a string literal

    """
    commands = split_into_commands(query)
    for command in commands:
        unquoted = _strip_quoted_sections(command)
        if 'group by' in unquoted.lower():
            return True
    return False
