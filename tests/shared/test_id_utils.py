"""Tests for ID generation helper utilities."""

import re
import uuid

from dashboard_compiler.shared.id_utils import generate_id


class TestGenerateId:
    """Tests for generate_id helper."""

    def test_returns_provided_id_when_given(self) -> None:
        """Test that provided ID is returned when given."""
        assert generate_id('my-custom-id') == 'my-custom-id'
        assert generate_id('panel-123') == 'panel-123'

    def test_generates_stable_id_when_values_provided(self) -> None:
        """Test that stable ID is generated when values are provided."""
        values = ['panel', 'title', 'grid']
        id1 = generate_id(None, values, use_stable=True)
        id2 = generate_id(None, values, use_stable=True)

        # Should generate valid UUID format
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        assert uuid_pattern.match(id1)

        # Should be stable (same values = same ID)
        assert id1 == id2

    def test_generates_different_stable_ids_for_different_values(self) -> None:
        """Test that different values generate different stable IDs."""
        id1 = generate_id(None, ['panel', 'title'], use_stable=True)
        id2 = generate_id(None, ['panel', 'other'], use_stable=True)

        assert id1 != id2

    def test_generates_random_uuid_when_use_stable_false(self) -> None:
        """Test that random UUID is generated when use_stable is False."""
        id1 = generate_id(None, use_stable=False)
        id2 = generate_id(None, use_stable=False)

        # Should generate valid UUID format
        uuid.UUID(id1)  # Will raise if invalid
        uuid.UUID(id2)

        # Should be different (random)
        assert id1 != id2

    def test_generates_random_uuid_when_no_stable_values(self) -> None:
        """Test that random UUID is generated when no stable values provided."""
        id1 = generate_id(None, stable_values=None, use_stable=True)
        id2 = generate_id(None, stable_values=None, use_stable=True)

        # Should generate valid UUID format
        uuid.UUID(id1)
        uuid.UUID(id2)

        # Should be different (random, since no stable values)
        assert id1 != id2

    def test_provided_id_takes_precedence(self) -> None:
        """Test that provided ID takes precedence over all other options."""
        provided = 'my-id'
        result = generate_id(provided, ['some', 'values'], use_stable=True)
        assert result == provided

    def test_handles_mixed_type_stable_values(self) -> None:
        """Test that stable ID generation works with mixed types."""
        values = ['panel', 123, 45.67, None]
        id1 = generate_id(None, values, use_stable=True)
        id2 = generate_id(None, values, use_stable=True)

        # Should be stable
        assert id1 == id2

        # Should generate valid UUID format
        uuid.UUID(id1)
