"""Type definitions for ES|QL controls."""

from enum import StrEnum


class ESQLVariableType(StrEnum):
    """Types of ES|QL variables.

    These match the ESQLVariableType enum from Kibana's kbn-esql-types package.
    """

    TIME_LITERAL = 'time_literal'
    """Time literal variable type."""

    FIELDS = 'fields'
    """Fields variable type."""

    VALUES = 'values'
    """Values variable type."""

    MULTI_VALUES = 'multi_values'
    """Multi-values variable type."""

    FUNCTIONS = 'functions'
    """Functions variable type."""


class EsqlControlType(StrEnum):
    """Types of ES|QL controls.

    These match the EsqlControlType enum from Kibana's kbn-esql-types package.
    """

    STATIC_VALUES = 'STATIC_VALUES'
    """Control with static values provided in configuration."""

    VALUES_FROM_QUERY = 'VALUES_FROM_QUERY'
    """Control with values dynamically fetched from an ES|QL query."""
