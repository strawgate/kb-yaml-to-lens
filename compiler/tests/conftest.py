import json
from typing import Any

import pytest
import pytest_asyncio
from freezegun.api import FrozenDateTimeFactory


@pytest.fixture(autouse=True)
def freezer(freezer: FrozenDateTimeFactory) -> FrozenDateTimeFactory:
    """Fixture to freeze time for consistent timestamps in snapshots."""
    # Freeze time to a fixed point for consistency in tests
    freezer.move_to('2023-10-01T12:00:00Z')
    return freezer


def de_json_kbn_dashboard(kbn_dashboard_dict: dict[str, Any]) -> dict[str, Any]:
    """Deserialize any stringified JSON in the kibana dashboard."""
    attributes = kbn_dashboard_dict['attributes']
    if attributes['optionsJSON'] and isinstance(attributes['optionsJSON'], str):
        attributes['optionsJSON'] = json.loads(attributes['optionsJSON'])

    if attributes['panelsJSON'] and isinstance(attributes['panelsJSON'], str):
        attributes['panelsJSON'] = json.loads(attributes['panelsJSON'])

    if (
        attributes['kibanaSavedObjectMeta']
        and attributes['kibanaSavedObjectMeta']['searchSourceJSON']
        and isinstance(attributes['kibanaSavedObjectMeta']['searchSourceJSON'], str)
    ):
        attributes['kibanaSavedObjectMeta']['searchSourceJSON'] = json.loads(attributes['kibanaSavedObjectMeta']['searchSourceJSON'])

    if (
        attributes['controlGroupInput']
        and attributes['controlGroupInput']['panelsJSON']
        and isinstance(attributes['controlGroupInput']['panelsJSON'], str)
    ):
        attributes['controlGroupInput']['panelsJSON'] = json.loads(attributes['controlGroupInput']['panelsJSON'])

    if (
        attributes['controlGroupInput']
        and attributes['controlGroupInput']['ignoreParentSettingsJSON']
        and isinstance(attributes['controlGroupInput']['ignoreParentSettingsJSON'], str)
    ):
        attributes['controlGroupInput']['ignoreParentSettingsJSON'] = json.loads(
            attributes['controlGroupInput']['ignoreParentSettingsJSON']
        )

    return kbn_dashboard_dict


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def shared_fixture_container():
    """Session-scoped fixture providing a persistent container for fixture generation.

    This fixture creates a single Docker container that persists for the entire
    test session, significantly improving test performance by avoiding container
    startup overhead for each test.

    Yields:
        Tuple of (container, output_dir) for use with generate_fixture
    """
    import shutil
    import tempfile
    from pathlib import Path

    from .fixtures.generator import shared_fixture_container as get_container

    # Create a temporary output directory for the session
    output_dir = Path(tempfile.mkdtemp(prefix='fixture_shared_'))
    try:
        async with get_container(output_dir) as container:
            yield (container, output_dir)
    finally:
        # Cleanup output directory
        if output_dir.exists():
            shutil.rmtree(output_dir)
