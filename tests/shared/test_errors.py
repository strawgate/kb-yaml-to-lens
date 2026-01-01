"""Tests for custom exception classes."""

import pytest

from dashboard_compiler.shared.errors import (
    ConfigValidationError,
    UnexpectedTypeError,
    YamlToLensError,
)


class TestConfigValidationError:
    """Tests for ConfigValidationError exception."""

    def test_can_be_raised_and_caught(self) -> None:
        """Test that ConfigValidationError can be raised and caught."""
        msg = 'Test error message'
        with pytest.raises(ConfigValidationError):
            raise ConfigValidationError(msg)

    def test_inherits_from_exception(self) -> None:
        """Test that ConfigValidationError inherits from Exception."""
        error = ConfigValidationError('Test error')
        assert isinstance(error, Exception)

    def test_error_message_is_preserved(self) -> None:
        """Test that error message is preserved when exception is raised."""
        msg = 'Validation failed'
        with pytest.raises(ConfigValidationError, match='Validation failed'):
            raise ConfigValidationError(msg)


class TestYamlToLensError:
    """Tests for YamlToLensError exception."""

    def test_can_be_raised_and_caught(self) -> None:
        """Test that YamlToLensError can be raised and caught."""
        msg = 'Test error message'
        with pytest.raises(YamlToLensError):
            raise YamlToLensError(msg)

    def test_stores_message_attribute(self) -> None:
        """Test that YamlToLensError stores message in attribute."""
        error = YamlToLensError('Test error message')
        assert error.message == 'Test error message'

    def test_inherits_from_exception(self) -> None:
        """Test that YamlToLensError inherits from Exception."""
        error = YamlToLensError('Test error')
        assert isinstance(error, Exception)

    def test_error_message_is_preserved(self) -> None:
        """Test that error message is preserved when exception is raised."""
        msg = 'Conversion failed'
        with pytest.raises(YamlToLensError, match='Conversion failed'):
            raise YamlToLensError(msg)


class TestUnexpectedTypeError:
    """Tests for UnexpectedTypeError exception."""

    def test_can_be_raised_and_caught(self) -> None:
        """Test that UnexpectedTypeError can be raised and caught."""
        expected = 'str'
        actual = 'int'
        with pytest.raises(UnexpectedTypeError):
            raise UnexpectedTypeError(expected, actual)

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

    def test_error_message_is_preserved(self) -> None:
        """Test that error message is preserved when exception is raised."""
        expected = 'float'
        actual = 'bool'
        with pytest.raises(UnexpectedTypeError, match=r"Expected type 'float', but got 'bool'\."):
            raise UnexpectedTypeError(expected, actual)
