"""Decompile a Kibana dashboard JSON object into a YAML dashboard stub.

Pipeline: raw JSON → parse → infer → serialize → CommentedMap
"""

from typing import Any

from ruamel.yaml.comments import CommentedMap

from .infer import infer_dashboard
from .parse import ParsedDashboard as ParsedDashboard
from .parse import as_dict, parse_dashboard, parse_json_field
from .serialize import serialize_dashboard

__all__ = ['decompile_dashboard']


def _extract_raw_panels(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the original raw panel dicts for TODO comment generation."""
    attributes = as_dict(dashboard.get('attributes')) or {}
    panels_json = parse_json_field(attributes.get('panelsJSON'))
    if not isinstance(panels_json, list):
        return []
    result: list[dict[str, Any]] = []
    for item in panels_json:  # pyright: ignore[reportAny]
        d = as_dict(item)  # pyright: ignore[reportAny]
        if d is not None:
            result.append(d)
    return result


def decompile_dashboard(dashboard: dict[str, Any]) -> CommentedMap:
    """Convert a Kibana dashboard object into a YAML stub document.

    This is the main entry point for the decompiler. The pipeline:
    1. Parse: raw JSON dict → typed ParsedDashboard
    2. Infer: ParsedDashboard → Dashboard config model
    3. Serialize: Dashboard config model → CommentedMap YAML with TODO annotations

    Args:
        dashboard: A raw Kibana dashboard JSON dict (as loaded from NDJSON).

    Returns:
        CommentedMap with structure: {dashboards: [{name: ..., panels: [...]}]}
    """
    # Phase 1: Parse
    parsed = parse_dashboard(dashboard)

    # Phase 2: Infer
    dashboard_model, _ = infer_dashboard(parsed)

    # Phase 3: Serialize
    raw_panels = _extract_raw_panels(dashboard)
    return serialize_dashboard(dashboard_model, parsed, raw_panels)
