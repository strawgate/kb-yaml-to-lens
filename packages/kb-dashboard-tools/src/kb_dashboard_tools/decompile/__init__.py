"""Decompile a Kibana dashboard JSON object into a YAML dashboard stub.

Pipeline: raw JSON → KbnDashboard → infer → serialize → CommentedMap
"""

# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false, reportAny=false, reportUnknownMemberType=false

from typing import Any

from ruamel.yaml.comments import CommentedMap

from .infer import infer_dashboard
from .kbn_raw_models import KbnDashboard
from .parse_shared import as_dict, get_str
from .serialize import serialize_dashboard

__all__ = ['decompile_dashboard']


def _extract_raw_reference_lookup(raw: dict[str, Any]) -> dict[str, str]:
    """Build a name→id reference lookup directly from the raw dict.

    Handles non-dict items and partial references that don't satisfy KbnReference's
    strict name/type/id requirements.
    """
    lookup: dict[str, str] = {}
    refs = raw.get('references')
    if not isinstance(refs, list):
        return lookup
    for ref in refs:
        r = as_dict(ref)
        if r is None:
            continue
        name = get_str(r, 'name')
        ref_id = get_str(r, 'id')
        if name is not None and ref_id is not None:
            lookup[name] = ref_id
    return lookup


def _extract_raw_filters(raw: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract the raw filter list from dashboard attributes.searchSourceJSON.

    Returns None if no filters found so infer_dashboard falls back to KbnFilter objects.
    Extracts as raw dicts to preserve top-level keys like 'range' that KbnFilter drops.
    """
    attrs = as_dict(raw.get('attributes'))
    if attrs is None:
        return None
    meta = as_dict(attrs.get('kibanaSavedObjectMeta'))
    if meta is None:
        return None
    search_source_raw = meta.get('searchSourceJSON')
    if isinstance(search_source_raw, str):
        import json as _json

        try:
            search_source_raw = _json.loads(search_source_raw)
        except Exception:
            return None
    if not isinstance(search_source_raw, dict):
        return None
    filter_list = search_source_raw.get('filter')
    if not isinstance(filter_list, list):
        return None
    result: list[dict[str, Any]] = []
    for item in filter_list:
        f = as_dict(item)
        if f is not None:
            result.append(f)
    return result if result else None


def _sanitize_for_kbn_validate(raw: dict[str, Any]) -> dict[str, Any]:
    """Remove malformed reference items so KbnDashboard.model_validate can succeed.

    KbnReference requires name/type/id; filter to only those with all three fields.
    """
    refs = raw.get('references')
    if not isinstance(refs, list):
        return raw
    sanitized = [r for r in refs if isinstance(r, dict) and 'type' in r and 'id' in r and 'name' in r]
    if len(sanitized) == len(refs):
        return raw
    return {**raw, 'references': sanitized}


def decompile_dashboard(raw: dict[str, Any]) -> CommentedMap:
    """Convert a Kibana dashboard object into a YAML stub document.

    This is the main entry point for the decompiler. The pipeline:
    1. Parse: raw JSON dict → KbnDashboard view model
    2. Infer: KbnDashboard → Dashboard config model + raw panels
    3. Serialize: Dashboard config model → CommentedMap YAML with TODO annotations

    Args:
        raw: A raw Kibana dashboard JSON dict (as loaded from NDJSON).

    Returns:
        CommentedMap with structure: {dashboards: [{name: ..., panels: [...]}]}
    """
    # Extract lookup tables from raw dict before validation (handles partial/non-standard items)
    raw_reference_lookup = _extract_raw_reference_lookup(raw)
    raw_filters = _extract_raw_filters(raw)
    kbn = KbnDashboard.model_validate(_sanitize_for_kbn_validate(raw))
    dashboard_model, raw_panels = infer_dashboard(kbn, raw_reference_lookup, raw_filters)
    return serialize_dashboard(dashboard_model, raw_panels)
