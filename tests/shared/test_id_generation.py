"""Unit tests for ID generation functions."""

import uuid

from dashboard_compiler.shared.config import random_id_generator, stable_id_generator


def test_stable_id_generator_consistency():
    """Verify that the same input produces the same output."""
    id1 = stable_id_generator(['field', 'aggregation'])
    id2 = stable_id_generator(['field', 'aggregation'])
    assert id1 == id2


def test_stable_id_generator_different_inputs():
    """Verify that different inputs produce different outputs."""
    id1 = stable_id_generator(['field', 'sum'])
    id2 = stable_id_generator(['field', 'count'])
    assert id1 != id2


def test_stable_id_generator_order_matters():
    """Verify that order of inputs affects the output."""
    id1 = stable_id_generator(['a', 'b'])
    id2 = stable_id_generator(['b', 'a'])
    assert id1 != id2


def test_stable_id_generator_uuid_format():
    """Verify that output is a valid UUID format."""
    result = stable_id_generator(['test'])
    # This will raise ValueError if the result is not a valid UUID
    uuid.UUID(result)


def test_stable_id_generator_with_numbers():
    """Verify stable ID generation with numeric values."""
    id1 = stable_id_generator(['field', 100])
    id2 = stable_id_generator(['field', 100])
    id3 = stable_id_generator(['field', 200])

    assert id1 == id2
    assert id1 != id3
    # Verify it's a valid UUID
    uuid.UUID(id1)


def test_stable_id_generator_with_floats():
    """Verify stable ID generation with float values."""
    id1 = stable_id_generator(['field', 95.5])
    id2 = stable_id_generator(['field', 95.5])
    id3 = stable_id_generator(['field', 95.6])

    assert id1 == id2
    assert id1 != id3
    uuid.UUID(id1)


def test_stable_id_generator_with_none():
    """Verify stable ID generation with None values."""
    id1 = stable_id_generator(['field', None])
    id2 = stable_id_generator(['field', None])
    id3 = stable_id_generator(['field', 'value'])

    assert id1 == id2
    assert id1 != id3
    uuid.UUID(id1)


def test_stable_id_generator_mixed_types():
    """Verify stable ID generation with mixed types."""
    id1 = stable_id_generator(['field', 'aggregation', 100, 95.5, None])
    id2 = stable_id_generator(['field', 'aggregation', 100, 95.5, None])

    assert id1 == id2
    uuid.UUID(id1)


def test_stable_id_generator_empty_list():
    """Verify stable ID generation with empty list."""
    id1 = stable_id_generator([])
    id2 = stable_id_generator([])

    assert id1 == id2
    uuid.UUID(id1)


def test_random_id_generator_uniqueness():
    """Verify that random IDs are unique."""
    # Generate 100 random IDs
    ids = {random_id_generator() for _ in range(100)}
    # All should be unique
    assert len(ids) == 100


def test_random_id_generator_uuid_format():
    """Verify that random ID generator produces valid UUIDs."""
    result = random_id_generator()
    # This will raise ValueError if the result is not a valid UUID
    uuid.UUID(result)


def test_random_id_generator_different_from_stable():
    """Verify that random and stable generators produce different results."""
    stable_id = stable_id_generator(['test'])
    random_id = random_id_generator()

    # These should be different (extremely unlikely to be the same)
    assert stable_id != random_id
