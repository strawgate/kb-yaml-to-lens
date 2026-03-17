"""Normalization/extraction adapters for decompiler raw payloads."""

from typing import Any, cast

from .parse_shared import as_dict, get_str


def coerce_bool(value: object) -> bool | None:
    """Coerce booleans from native bool or common string forms."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == 'true':
            return True
        if normalized == 'false':
            return False
    return None


def normalize_partition_visualization(vis_raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize partition visualization fields with common Kibana shape drift."""
    normalized = dict(vis_raw)
    layers = normalized.get('layers')
    if not isinstance(layers, list):
        return normalized
    layers_list = cast('list[object]', layers)
    if len(layers_list) == 0:
        return normalized
    first_layer = as_dict(layers_list[0])
    if first_layer is None:
        return normalized

    normalized_layer = dict(first_layer)
    for key in ('showSingleSeries', 'nestedLegend', 'truncateLegend'):
        coerced = coerce_bool(normalized_layer.get(key))
        if coerced is not None:
            normalized_layer[key] = coerced

    updated_layers = list(layers_list)
    updated_layers[0] = normalized_layer
    normalized['layers'] = updated_layers
    return normalized


def extract_search_saved_object_id(panel_raw: dict[str, Any]) -> str | None:
    """Extract search saved object id from common Kibana panel locations."""
    embeddable_config = as_dict(panel_raw.get('embeddableConfig')) or {}
    saved_object_id = get_str(embeddable_config, 'savedObjectId')
    if saved_object_id is not None:
        return saved_object_id
    return get_str(panel_raw, 'savedSearchId')
