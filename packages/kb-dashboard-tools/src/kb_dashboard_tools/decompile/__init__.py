"""Decompile a Kibana dashboard JSON object into a YAML dashboard stub.

Pipeline: raw JSON → validate → infer → serialize → CommentedMap
"""

# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from typing import Any

from ruamel.yaml.comments import CommentedMap

from .infer import infer_dashboard
from .kbn_raw_models.dashboard.view import KbnDashboard
from .serialize import serialize_dashboard

__all__ = ['decompile_dashboard']


def _normalize_dashboard_for_validation(dashboard: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw dashboard dict to safely pass to KbnDashboard.model_validate.

    Filters out invalid references (non-dict items, items missing required fields)
    since KbnReference requires type, id, and name.
    """
    refs = dashboard.get('references')
    if not isinstance(refs, list):
        return dashboard
    # Filter to only valid KbnReference-compatible dicts
    valid_refs = [r for r in refs if isinstance(r, dict) and 'type' in r and 'id' in r and 'name' in r]
    if len(valid_refs) == len(refs):
        return dashboard
    # Return a copy with only valid references
    result = dict(dashboard)
    result['references'] = valid_refs
    return result


def decompile_dashboard(dashboard: dict[str, Any]) -> CommentedMap:
    """Convert a Kibana dashboard object into a YAML stub document.

    This is the main entry point for the decompiler. The pipeline:
    1. Validate: raw JSON dict → KbnDashboard (typed view model)
    2. Infer: KbnDashboard → Dashboard config model
    3. Serialize: Dashboard config model → CommentedMap YAML with TODO annotations

    Args:
        dashboard: A raw Kibana dashboard JSON dict (as loaded from NDJSON).

    Returns:
        CommentedMap with structure: {dashboards: [{name: ..., panels: [...]}]}
    """
    # Phase 1: Validate into typed model (normalize references first)
    normalized = _normalize_dashboard_for_validation(dashboard)
    kbn = KbnDashboard.model_validate(normalized)

    # Phase 2: Infer (pass raw dict for reference/filter extraction)
    dashboard_model, _ = infer_dashboard(kbn, dashboard)

    # Phase 3: Serialize
    # Extract raw panels for TODO comment generation
    attrs = kbn.attributes
    raw_panels: list[dict[str, Any]] = []
    if attrs is not None and isinstance(attrs.panelsJSON, list):
        raw_panels.extend(item for item in attrs.panelsJSON if isinstance(item, dict))

    return serialize_dashboard(dashboard_model, kbn, raw_panels)
