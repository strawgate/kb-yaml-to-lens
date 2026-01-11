import json
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

import pytest
from freezegun.api import FrozenDateTimeFactory

if TYPE_CHECKING:
    from tests.fixtures.generator import FixtureGenerator


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


@pytest.fixture
async def require_fixture_generator() -> AsyncGenerator['FixtureGenerator', None]:
    """Async fixture that provides a FixtureGenerator, skipping if Docker unavailable."""
    from tests.fixtures.generator import FixtureGenerator, docker_available

    if not await docker_available():
        pytest.skip('Docker not available for fixture generation')

    try:
        async with FixtureGenerator() as generator:
            yield generator
    except RuntimeError as e:
        pytest.skip(f'Fixture generator unavailable: {e}')
