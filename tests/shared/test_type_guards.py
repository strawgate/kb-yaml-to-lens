"""Tests for type guard utilities."""

import pytest

from dashboard_compiler.shared.type_guards import ensure_dict, ensure_list, ensure_str, is_str_dict


class TestEnsureDict:
    """Tests for ensure_dict function."""

    def test_valid_dict(self) -> None:
        """Test that a valid dict is returned unchanged."""
        input_dict = {'key': 'value', 'number': 42}
        result = ensure_dict(input_dict, 'test context')
        assert result == input_dict
        assert result is input_dict

    def test_empty_dict(self) -> None:
        """Test that an empty dict is valid."""
        result = ensure_dict({}, 'test context')
        assert result == {}

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-dict values raise TypeError."""
        with pytest.raises(TypeError, match='test context must be a dictionary, got str'):
            _ = ensure_dict('not a dict', 'test context')

        with pytest.raises(TypeError, match='test context must be a dictionary, got list'):
            _ = ensure_dict(['a', 'list'], 'test context')

        with pytest.raises(TypeError, match='test context must be a dictionary, got int'):
            _ = ensure_dict(42, 'test context')

        with pytest.raises(TypeError, match='test context must be a dictionary, got NoneType'):
            _ = ensure_dict(None, 'test context')


class TestEnsureStr:
    """Tests for ensure_str function."""

    def test_valid_str(self) -> None:
        """Test that a valid string is returned unchanged."""
        input_str = 'hello world'
        result = ensure_str(input_str, 'test context')
        assert result == input_str
        assert result is input_str

    def test_empty_str(self) -> None:
        """Test that an empty string is valid."""
        result = ensure_str('', 'test context')
        assert result == ''

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-string values raise TypeError."""
        with pytest.raises(TypeError, match='test context must be a string, got int'):
            _ = ensure_str(42, 'test context')

        with pytest.raises(TypeError, match='test context must be a string, got dict'):
            _ = ensure_str({'key': 'value'}, 'test context')

        with pytest.raises(TypeError, match='test context must be a string, got NoneType'):
            _ = ensure_str(None, 'test context')


class TestEnsureList:
    """Tests for ensure_list function."""

    def test_valid_list(self) -> None:
        """Test that a valid list is returned unchanged."""
        input_list = [1, 2, 3, 'four']
        result = ensure_list(input_list, 'test context')
        assert result == input_list
        assert result is input_list

    def test_empty_list(self) -> None:
        """Test that an empty list is valid."""
        result = ensure_list([], 'test context')
        assert result == []

    def test_invalid_type_raises_error(self) -> None:
        """Test that non-list values raise TypeError."""
        with pytest.raises(TypeError, match='test context must be a list, got str'):
            _ = ensure_list('not a list', 'test context')

        with pytest.raises(TypeError, match='test context must be a list, got dict'):
            _ = ensure_list({'key': 'value'}, 'test context')

        with pytest.raises(TypeError, match='test context must be a list, got tuple'):
            _ = ensure_list((1, 2, 3), 'test context')


class TestIsStrDict:
    """Tests for is_str_dict type guard."""

    def test_valid_str_dict(self) -> None:
        """Test that dict with string keys returns True."""
        assert is_str_dict({'key': 'value', 'another': 42}) is True
        assert is_str_dict({}) is True
        assert is_str_dict({'a': None, 'b': [1, 2, 3]}) is True

    def test_non_dict_returns_false(self) -> None:
        """Test that non-dict values return False."""
        assert is_str_dict('not a dict') is False
        assert is_str_dict([1, 2, 3]) is False
        assert is_str_dict(None) is False
        assert is_str_dict(42) is False

    def test_dict_with_non_string_keys_returns_false(self) -> None:
        """Test that dict with non-string keys returns False."""
        assert is_str_dict({1: 'value'}) is False
        assert is_str_dict({'key': 'value', 42: 'number key'}) is False
        assert is_str_dict({None: 'none key'}) is False
