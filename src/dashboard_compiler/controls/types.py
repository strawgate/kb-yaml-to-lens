"""Type definitions for ES|QL controls."""

from enum import StrEnum


class ESQLVariableType(StrEnum):
    """Types of ES|QL variables."""

    VALUES = 'VALUES'
    """Variable represents a list of values."""

    FIELDS = 'FIELDS'
    """Variable represents field names."""

    TIME_LITERAL = 'TIME_LITERAL'
    """Variable represents a time literal."""


class EsqlControlType(StrEnum):
    """Types of ES|QL controls."""

    STATIC_VALUES = 'STATIC_VALUES'
    """Control with a predefined static list of values."""

    VALUES_FROM_QUERY = 'VALUES_FROM_QUERY'
    """Control with values dynamically populated from an ES|QL query."""
