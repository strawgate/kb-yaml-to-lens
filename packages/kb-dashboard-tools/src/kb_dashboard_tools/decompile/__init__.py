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


def decompile_dashboard(dashboard: dict[str, Any]) -> CommentedMap:
    """Convert a Kibana dashboard object into a YAML stub document.

    Pipeline: raw JSON → KbnDashboard → Dashboard config → CommentedMap YAML
    """
    kbn = KbnDashboard.model_validate(dashboard)
    dashboard_model = infer_dashboard(kbn)
    attrs = kbn.attributes
    panels_json = attrs.panelsJSON if attrs is not None else None
    raw_panels: list[dict[str, Any]] = (
        [item.model_dump(by_alias=True, exclude_none=True) for item in panels_json] if panels_json is not None else []
    )
    return serialize_dashboard(dashboard_model, kbn, raw_panels)
