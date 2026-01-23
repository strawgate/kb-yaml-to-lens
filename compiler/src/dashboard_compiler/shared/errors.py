"""Custom exceptions for the YAML to Lens conversion process."""


class ConfigValidationError(Exception):
    """Exception raised when YAML configuration fails schema validation."""


class YamlToLensError(Exception):
    """Exception raised for general errors during YAML to Lens conversion."""

    message: str

    def __init__(self, message: str) -> None:
        """Initialize the YamlToLensError with a message."""
        super().__init__(message)
        self.message = message


class UnexpectedTypeError(YamlToLensError):
    """Exception raised for unexpected types in the YAML to Lens conversion process."""

    expected_type: str
    actual_type: str

    def __init__(self, expected_type: str, actual_type: str) -> None:
        """Initialize the UnexpectedTypeError with expected and actual types."""
        message = f"Expected type '{expected_type}', but got '{actual_type}'."
        super().__init__(message)
        self.expected_type = expected_type
        self.actual_type = actual_type
