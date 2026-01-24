import json
from typing import Any


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
