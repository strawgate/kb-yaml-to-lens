import json
import re
from typing import Any

import pytest
import yaml
from freezegun.api import FrozenDateTimeFactory
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

DEEP_DIFF_DEFAULTS: dict[str, bool | int] = {
    'ignore_order': True,
    'threshold_to_diff_deeper': 0,
    'verbose_level': 2,
}


@pytest.fixture
def snapshot_json(snapshot: SnapshotAssertion):
    """Fixture to use the JSONSnapshotExtension with default matchers."""
    # Apply matchers globally for this fixture using with_defaults
    return snapshot.use_extension(JSONSnapshotExtension)  # .with_defaults(exclude=props("id", "i", "panelIndex", "gridData.i"))


@pytest.fixture(autouse=True)
def freezer(freezer: FrozenDateTimeFactory) -> FrozenDateTimeFactory:
    """Fixture to freeze time for consistent timestamps in snapshots."""
    # Freeze time to a fixed point for consistency in tests
    freezer.move_to('2023-10-01T12:00:00Z')
    return freezer


def parse_yaml_string(yaml_string: str) -> dict:
    """Parse a YAML string into a dictionary."""
    return yaml.safe_load(yaml_string)


def de_json_kbn_dashboard(kbn_dashboard_dict: dict) -> dict:
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


def replace_uuid_field(data: dict[str, Any], field_name: str, placeholder: str = 'DYNAMIC_ID') -> dict[str, Any]:
    """Replace a UUID field value with a placeholder for consistent snapshots.

    This helper is used to normalize dynamically generated UUIDs in test snapshots,
    making them deterministic and easier to compare.

    Args:
        data: Dictionary containing the field to replace
        field_name: Name of the field containing the UUID
        placeholder: Placeholder value to use (default: 'DYNAMIC_ID')

    Returns:
        The modified dictionary (note: modifies in place and returns for chaining)

    Example:
        result = replace_uuid_field(layer.model_dump(), 'layerId', 'DYNAMIC_LAYER_ID')
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if field_name in data and isinstance(data[field_name], str) and re.match(uuid_pattern, data[field_name]):
        data[field_name] = placeholder
    return data


def replace_nested_uuid_field(data: dict[str, Any], field_path: str, placeholder: str = 'DYNAMIC_ID') -> dict[str, Any]:
    """Replace a nested UUID field value with a placeholder for consistent snapshots.

    Supports dot-separated paths to navigate nested dictionaries.

    Args:
        data: Dictionary containing the nested field to replace
        field_path: Dot-separated path to the field (e.g., 'explicitInput.id')
        placeholder: Placeholder value to use (default: 'DYNAMIC_ID')

    Returns:
        The modified dictionary (note: modifies in place and returns for chaining)

    Example:
        result = replace_nested_uuid_field(result, 'explicitInput.id', 'DYNAMIC_ID')
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

    keys = field_path.split('.')
    current = data
    for key in keys[:-1]:
        if key in current and isinstance(current[key], dict):
            current = current[key]
        else:
            return data

    final_key = keys[-1]
    if final_key in current and isinstance(current[final_key], str) and re.match(uuid_pattern, current[final_key]):
        current[final_key] = placeholder

    return data
