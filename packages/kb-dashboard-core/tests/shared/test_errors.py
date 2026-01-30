"""Tests for custom exception classes."""

from kb_dashboard_core.shared.errors import (
    UnexpectedTypeError,
    YamlToLensError,
)


class TestYamlToLensError:
    """Tests for YamlToLensError exception."""

    def test_stores_message_attribute(self) -> None:
        """Test that YamlToLensError stores message in attribute."""
        error = YamlToLensError('Test error message')
        assert error.message == 'Test error message'


class TestUnexpectedTypeError:
    """Tests for UnexpectedTypeError exception."""

    def test_stores_expected_and_actual_types(self) -> None:
        """Test that UnexpectedTypeError stores expected and actual type attributes."""
        error = UnexpectedTypeError('str', 'int')
        assert error.expected_type == 'str'
        assert error.actual_type == 'int'

    def test_generates_proper_error_message(self) -> None:
        """Test that UnexpectedTypeError generates a proper error message."""
        error = UnexpectedTypeError('dict', 'list')
        assert error.message == "Expected type 'dict', but got 'list'."
        assert str(error) == "Expected type 'dict', but got 'list'."

    def test_inherits_from_yaml_to_lens_error(self) -> None:
        """Test that UnexpectedTypeError inherits from YamlToLensError."""
        error = UnexpectedTypeError('str', 'int')
        assert isinstance(error, YamlToLensError)
        assert isinstance(error, Exception)
