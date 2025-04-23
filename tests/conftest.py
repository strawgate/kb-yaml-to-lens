import pytest
from syrupy.filters import props
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension
import yaml


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
