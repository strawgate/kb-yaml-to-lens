"""Tests for ID generation helper utilities."""

import uuid

from dashboard_compiler.shared.id_utils import generate_id


class TestGenerateId:
    """Tests for generate_id helper."""

    def test_returns_provided_id_when_given(self) -> None:
        """Test that provided ID is returned when given."""
        assert generate_id('my-custom-id') == 'my-custom-id'
        assert generate_id('panel-123') == 'panel-123'

    def test_generates_random_uuid_when_none(self) -> None:
        """Test that random UUID is generated when provided_id is None."""
        id1 = generate_id(None)
        id2 = generate_id(None)

        # Should generate valid UUID format
        uuid.UUID(id1)  # Will raise if invalid
        uuid.UUID(id2)

        # Should be different (random)
        assert id1 != id2

    def test_returns_empty_string_when_provided(self) -> None:
        """Test that empty string is returned when given (not converted to UUID)."""
        assert generate_id('') == ''
