"""Tests for ES|QL query parsing helpers.

These tests focus on edge cases for the core parsing utilities,
not on linting rule behavior (which belongs in rule-specific tests).
"""

import re

import pytest

from dashboard_lint.esql_helpers import (
    has_command_containing,
    has_command_starting_with,
    split_into_commands,
)


class TestSplitIntoCommands:
    """Tests for split_into_commands - the core ES|QL command parser."""

    @pytest.mark.parametrize(
        ('query', 'expected'),
        [
            # Basic splitting
            ('FROM logs-*', ['FROM logs-*']),
            ('FROM logs-* | WHERE status == 200', ['FROM logs-*', 'WHERE status == 200']),
            (
                'FROM logs-* | WHERE status == 200 | SORT @timestamp',
                ['FROM logs-*', 'WHERE status == 200', 'SORT @timestamp'],
            ),
            # Whitespace handling
            ('  FROM logs-*  |  WHERE status == 200  ', ['FROM logs-*', 'WHERE status == 200']),
            # Empty/edge cases
            ('', []),
            ('   ', []),
            ('|', []),
            ('| |', []),
        ],
        ids=[
            'single_command',
            'two_commands',
            'three_commands',
            'whitespace_trimming',
            'empty_string',
            'whitespace_only',
            'single_pipe',
            'multiple_empty_pipes',
        ],
    )
    def test_basic_splitting(self, query: str, expected: list[str]) -> None:
        """Should split queries correctly on pipes."""
        assert split_into_commands(query) == expected

    @pytest.mark.parametrize(
        ('query', 'expected'),
        [
            # Single quotes
            ("FROM logs-* | WHERE message LIKE '*|*'", ['FROM logs-*', "WHERE message LIKE '*|*'"]),
            ("FROM logs-* | WHERE x = 'a|b|c' | LIMIT 10", ['FROM logs-*', "WHERE x = 'a|b|c'", 'LIMIT 10']),
            # Double quotes
            ('FROM logs-* | WHERE message LIKE "*|*"', ['FROM logs-*', 'WHERE message LIKE "*|*"']),
            # Backticks
            ('FROM logs-* | WHERE `field|name` IS NOT NULL', ['FROM logs-*', 'WHERE `field|name` IS NOT NULL']),
        ],
        ids=[
            'single_quoted_pipe',
            'single_quoted_multiple_pipes',
            'double_quoted_pipe',
            'backtick_quoted_pipe',
        ],
    )
    def test_quoted_strings_preserve_pipes(self, query: str, expected: list[str]) -> None:
        """Should not split on pipes inside quoted strings."""
        assert split_into_commands(query) == expected

    @pytest.mark.parametrize(
        ('query', 'expected'),
        [
            # Escaped single quote
            (
                "FROM logs-* | WHERE message LIKE 'it\\'s | working' | LIMIT 10",
                ['FROM logs-*', "WHERE message LIKE 'it\\'s | working'", 'LIMIT 10'],
            ),
            # Escaped double quote
            (
                'FROM logs-* | WHERE msg = "say \\"hi | there\\"" | LIMIT 5',
                ['FROM logs-*', 'WHERE msg = "say \\"hi | there\\""', 'LIMIT 5'],
            ),
        ],
        ids=['escaped_single_quote', 'escaped_double_quote'],
    )
    def test_escaped_quotes(self, query: str, expected: list[str]) -> None:
        """Should handle escaped quotes correctly."""
        assert split_into_commands(query) == expected

    def test_multiline_query(self) -> None:
        """Should handle multiline queries."""
        query = """FROM logs-*
| WHERE status == 200
| STATS count = COUNT(*)"""
        commands = split_into_commands(query)
        assert commands == ['FROM logs-*', 'WHERE status == 200', 'STATS count = COUNT(*)']


class TestHasCommandContaining:
    """Tests for has_command_containing - pattern matching respecting quotes."""

    @pytest.mark.parametrize(
        ('query', 'pattern', 'expected'),
        [
            # Pattern in command
            (
                'FROM logs-* | STATS count = COUNT(*) BY bucket = BUCKET(@timestamp)',
                re.compile(r'\bBUCKET\b', re.IGNORECASE),
                True,
            ),
            # Pattern in string literal - should NOT match
            (
                "FROM logs-* | WHERE message = 'BUCKET example'",
                re.compile(r'\bBUCKET\b', re.IGNORECASE),
                False,
            ),
            # Pattern not present
            (
                'FROM logs-* | STATS count = COUNT(*) BY host.name',
                re.compile(r'\bBUCKET\b', re.IGNORECASE),
                False,
            ),
            # Pattern in double-quoted string - should NOT match
            (
                'FROM logs-* | WHERE message = "contains SORT keyword"',
                re.compile(r'\bSORT\b', re.IGNORECASE),
                False,
            ),
            # Pattern in backtick field name - should NOT match
            (
                'FROM logs-* | WHERE `SORT` IS NOT NULL',
                re.compile(r'\bSORT\b', re.IGNORECASE),
                False,
            ),
            # Pattern as actual command
            (
                'FROM logs-* | SORT @timestamp',
                re.compile(r'\bSORT\b', re.IGNORECASE),
                True,
            ),
        ],
        ids=[
            'pattern_in_command',
            'pattern_in_single_quoted_string',
            'pattern_not_present',
            'pattern_in_double_quoted_string',
            'pattern_in_backtick_field',
            'pattern_as_command',
        ],
    )
    def test_pattern_matching(self, query: str, pattern: re.Pattern[str], expected: bool) -> None:
        """Should correctly detect patterns while ignoring quoted strings."""
        assert has_command_containing(query, pattern) is expected


class TestHasCommandStartingWith:
    """Tests for has_command_starting_with - keyword detection respecting quotes."""

    @pytest.mark.parametrize(
        ('query', 'keyword', 'expected'),
        [
            # Keyword starts a command
            ('FROM logs-* | SORT @timestamp', 'SORT', True),
            ('FROM logs-* | LIMIT 10', 'LIMIT', True),
            ('FROM logs-* | WHERE status == 200', 'WHERE', True),
            # Keyword in string literal - should NOT match
            ("FROM logs-* | WHERE msg = 'SORT example'", 'SORT', False),
            ("FROM logs-* | WHERE msg = 'LIMIT this'", 'LIMIT', False),
            # Keyword not present
            ('FROM logs-* | STATS count = COUNT(*)', 'SORT', False),
            # Case insensitivity
            ('FROM logs-* | sort @timestamp', 'SORT', True),
            ('FROM logs-* | Sort @timestamp', 'sort', True),
        ],
        ids=[
            'sort_command',
            'limit_command',
            'where_command',
            'sort_in_string',
            'limit_in_string',
            'keyword_not_present',
            'lowercase_command',
            'mixed_case',
        ],
    )
    def test_keyword_detection(self, query: str, keyword: str, expected: bool) -> None:
        """Should correctly detect command keywords while ignoring quoted strings."""
        assert has_command_starting_with(query, keyword) is expected
