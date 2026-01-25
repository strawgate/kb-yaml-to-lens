"""ES|QL query parsing helpers for lint rules.

This module provides utilities for analyzing ES|QL queries in lint rules.
"""

import re

from dashboard_compiler.queries.config import ESQLQuery


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


# Regex patterns for detecting various ES|QL issues

# SQL syntax patterns
ORDER_BY_PATTERN = re.compile(r'\bORDER\s+BY\b', re.IGNORECASE)
"""Detects SQL ORDER BY (should be SORT in ES|QL)."""

SELECT_START_PATTERN = re.compile(r'^\s*SELECT\b', re.IGNORECASE | re.MULTILINE)
"""Detects queries starting with SELECT (ES|QL uses FROM first)."""

# Pattern for single = in WHERE comparison context (not ==, !=, <=, >=)
# This is a more targeted pattern that looks for WHERE followed by a comparison with single =
# Avoids matching assignment operators in STATS, EVAL, etc.
SINGLE_EQUALS_IN_WHERE_PATTERN = re.compile(
    r'\bWHERE\b[^|]*?\b(\w+)\s*=\s*(?=[\'"\d])',
    re.IGNORECASE,
)
"""Detects single = for equality in WHERE clauses (should be == in ES|QL)."""

# Pattern for SQL-style LIKE wildcards
SQL_LIKE_WILDCARD_PATTERN = re.compile(r"LIKE\s+['\"][^'\"]*%[^'\"]*['\"]", re.IGNORECASE)
"""Detects LIKE with % wildcard (should use * in ES|QL)."""

# Fixed time bucket patterns
# Matches: BUCKET(@timestamp, 1 minute), BUCKET(`@timestamp`, 5 minutes), etc.
FIXED_BUCKET_PATTERN = re.compile(
    r'BUCKET\s*\(\s*[`"]?@timestamp[`"]?\s*,\s*\d+\s+(?:second|minute|hour|day|week|month|year)s?\s*\)',
    re.IGNORECASE,
)
"""Detects fixed interval BUCKET(@timestamp, N units) patterns."""

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


def find_sql_order_by(query: str) -> list[re.Match[str]]:
    """Find ORDER BY usage in query.

    Args:
        query: The ES|QL query string.

    Returns:
        List of regex matches for ORDER BY patterns.

    """
    return list(ORDER_BY_PATTERN.finditer(query))


def find_sql_select(query: str) -> list[re.Match[str]]:
    """Find SELECT at start of query.

    Args:
        query: The ES|QL query string.

    Returns:
        List of regex matches for SELECT patterns.

    """
    return list(SELECT_START_PATTERN.finditer(query))


def find_single_equals(query: str) -> list[re.Match[str]]:
    """Find single = used for equality comparison in WHERE clauses.

    This function specifically looks for WHERE clauses that use single = for
    comparison instead of ==. It avoids false positives from assignment
    operators in STATS, EVAL, etc.

    Args:
        query: The ES|QL query string.

    Returns:
        List of regex matches for single = comparison patterns in WHERE.

    """
    return list(SINGLE_EQUALS_IN_WHERE_PATTERN.finditer(query))


def find_sql_like_wildcards(query: str) -> list[re.Match[str]]:
    """Find LIKE with % wildcards.

    Args:
        query: The ES|QL query string.

    Returns:
        List of regex matches for LIKE % patterns.

    """
    return list(SQL_LIKE_WILDCARD_PATTERN.finditer(query))


def find_fixed_time_buckets(query: str) -> list[re.Match[str]]:
    """Find fixed time bucket patterns.

    Args:
        query: The ES|QL query string.

    Returns:
        List of regex matches for fixed bucket patterns.

    """
    fixed_buckets = list(FIXED_BUCKET_PATTERN.finditer(query))
    tbucket_fixed = list(TBUCKET_FIXED_PATTERN.finditer(query))
    return fixed_buckets + tbucket_fixed


def find_unescaped_numeric_fields(query: str) -> list[re.Match[str]]:
    """Find field names with numeric suffixes that need backtick escaping.

    Args:
        query: The ES|QL query string.

    Returns:
        List of regex matches for unescaped numeric field patterns.

    """
    return list(UNESCAPED_NUMERIC_FIELD_PATTERN.finditer(query))
