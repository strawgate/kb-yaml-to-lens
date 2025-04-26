import pytest
from syrupy.filters import props
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension
import yaml

import re  # Import re module for regex escaping


@pytest.fixture
def snapshot_json(snapshot: SnapshotAssertion):
    """Fixture to use the JSONSnapshotExtension with default matchers."""
    # Apply matchers globally for this fixture using with_defaults
    return snapshot.use_extension(JSONSnapshotExtension).with_defaults(exclude=props("id", "i", "panelIndex", "gridData.i"))


@pytest.fixture(autouse=True)
def freezer(freezer):
    """Fixture to freeze time for consistent timestamps in snapshots."""
    # Freeze time to a fixed point for consistency in tests
    freezer.move_to("2023-10-01T12:00:00Z")
    return freezer


def parse_yaml_string(yaml_string):
    return yaml.safe_load(yaml_string)


def pydantic_error_regex(field_name: str, error_type: str, **kwargs) -> str:
    """
    Generates a regex pattern for Pydantic validation error messages.

    Args:
        field_name: The name of the field with the validation error.
        error_type: The type of Pydantic error (e.g., "missing", "type", "literal").
        **kwargs: Additional details for specific error types.

    Returns:
        A regex string matching the expected Pydantic error message.
    """
    if error_type == "missing":
        return f"{field_name}\n  Field required"
    elif error_type == "type":
        expected_type = kwargs.get("expected_type", "valid type")
        # Pydantic v2+ often includes the input type in the error message
        return f"{field_name}\n  Input should be a valid {expected_type}(?:.*)"
    elif error_type == "literal":
        expected_values = kwargs.get("expected_values")
        if isinstance(expected_values, (list, tuple)):
            if len(expected_values) == 2:
                # For two literal values, format as 'value1' or 'value2'
                return f"{field_name}\n  Input should be '{expected_values[0]}' or '{expected_values[1]}'(?:.*)"
            # Escape special characters in expected values for regex
            escaped_values = [re.escape(str(v)) for v in expected_values]
            values_str = "'" + "', '".join(escaped_values) + "'"
            return f"{field_name}\n  Input should be {values_str}(?:.*)"
        else:
            # Fallback for single literal or other cases
            return f"{field_name}\n  Input should be {re.escape(str(expected_values))}(?:.*)"
    elif error_type == "union":
        # Regex for Union errors can be complex, this is a basic attempt
        return f"{field_name}\n  Input should be a valid dictionary(?:.*)"  # Common for nested models in Unions
    elif error_type == "list_length":
        min_length = kwargs.get("min_length")
        max_length = kwargs.get("max_length")
        if min_length is not None and max_length is not None:
            return f"{field_name}\n  List should have between {min_length} and {max_length} items(?:.*)"
        elif min_length is not None:
            return f"{field_name}\n  List should have at least {min_length} item(?:s)?(?:.*)"
        elif max_length is not None:
            return f"{field_name}\n  List should have at most {max_length} item(?:s)?(?:.*)"
    # Add more error types as needed based on observed Pydantic errors
    else:
        # Fallback for unhandled error types
        return f"{field_name}\n  .*"
