"""Phase 3: Serialize inferred dashboard config dicts to CommentedMap YAML.

Produces a CommentedMap suitable for ruamel.yaml round-trip output,
with TODO comments attached to each panel.
"""

# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnusedCallResult=false

import json
from typing import Any, cast

from kb_dashboard_core.dashboard.config import Dashboard
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from .parse import ParsedDashboard, ParsedPanel


def _to_commented_map(d: dict[str, object]) -> CommentedMap:
    """Recursively convert a plain dict to CommentedMap."""
    cm = CommentedMap()
    cm_any = cast('Any', cm)
    for key, value in d.items():
        if isinstance(value, dict):
            cm_any[key] = _to_commented_map(cast('dict[str, object]', value))
        elif isinstance(value, list):
            cm_any[key] = _to_commented_seq(cast('list[object]', value))
        else:
            cm_any[key] = value
    return cm


def _to_commented_seq(lst: list[object]) -> CommentedSeq:
    """Recursively convert a plain list to CommentedSeq."""
    cs = CommentedSeq()
    cs_any = cast('Any', cs)
    for item in lst:
        if isinstance(item, dict):
            cs_any.append(_to_commented_map(cast('dict[str, object]', item)))
        elif isinstance(item, list):
            cs_any.append(_to_commented_seq(cast('list[object]', item)))
        else:
            cs_any.append(item)
    return cs


def _set_flow_style(cm: CommentedMap) -> None:
    """Set flow style on a CommentedMap for compact display (e.g., {w: 24, h: 15})."""
    if hasattr(cm, 'fa'):
        cm.fa.set_flow_style()


def _strip_default_panel_layout(panel_yaml: CommentedMap, parsed_panel: ParsedPanel | None) -> None:
    """Preserve legacy omission of size/position when Kibana omitted grid data."""
    if parsed_panel is None:
        return

    panel_yaml_any = cast('Any', panel_yaml)
    size = cast('object', panel_yaml_any.get('size'))
    if parsed_panel.grid is None or (parsed_panel.grid.w is None and parsed_panel.grid.h is None):
        if 'size' in panel_yaml:
            del panel_yaml['size']
    elif isinstance(size, CommentedMap):
        _set_flow_style(size)

    position = cast('object', panel_yaml_any.get('position'))
    if parsed_panel.grid is None or (parsed_panel.grid.x is None and parsed_panel.grid.y is None):
        if 'position' in panel_yaml:
            del panel_yaml['position']
    elif isinstance(position, CommentedMap):
        _set_flow_style(position)


def _format_panel_layouts(dashboard_yaml: CommentedMap, parsed: ParsedDashboard) -> None:
    """Compact panel layout fields and drop model-defaulted layout when absent in source."""
    dashboard_yaml_any = cast('Any', dashboard_yaml)
    panels = cast('object', dashboard_yaml_any.get('panels'))
    if not isinstance(panels, (list, CommentedSeq)):
        return

    for i, panel_yaml in enumerate(cast('list[object]', panels)):
        if not isinstance(panel_yaml, CommentedMap):
            continue
        parsed_panel = parsed.panels[i] if i < len(parsed.panels) else None
        _strip_default_panel_layout(panel_yaml, parsed_panel)


def serialize_dashboard(
    dashboard_model: Dashboard,
    parsed: ParsedDashboard,
    raw_panels: list[dict[str, Any]],
) -> CommentedMap:
    """Convert an inferred Dashboard config model to a CommentedMap YAML document.

    Args:
        dashboard_model: The dashboard config model from infer_dashboard().
        parsed: The parsed dashboard structure (for TODO comment generation).
        raw_panels: The original raw panel dicts for TODO comments.

    Returns:
        CommentedMap with structure: {dashboards: [{name: ..., panels: [...]}]}
    """
    document = CommentedMap()
    dashboards = CommentedSeq()
    document['dashboards'] = dashboards

    dashboard_dict = cast(
        'dict[str, object]',
        dashboard_model.model_dump(serialize_as_any=True, exclude_none=True, by_alias=True),
    )

    settings_dict = dashboard_model.settings.model_dump(exclude_none=True, exclude_defaults=True, by_alias=True)
    if settings_dict:
        dashboard_dict['settings'] = settings_dict
    else:
        dashboard_dict.pop('settings', None)

    if not dashboard_model.filters:
        dashboard_dict.pop('filters', None)

    if not dashboard_model.controls:
        dashboard_dict.pop('controls', None)

    dashboard_yaml = _to_commented_map(dashboard_dict)
    _format_panel_layouts(dashboard_yaml, parsed)

    # Attach TODO comments to each panel
    dashboard_yaml_any = cast('Any', dashboard_yaml)
    panels_seq = cast('object', dashboard_yaml_any.get('panels'))
    if isinstance(panels_seq, CommentedSeq) and len(parsed.panels) == len(panels_seq):
        panels_seq_any = cast('Any', panels_seq)
        for i, parsed_panel in enumerate(parsed.panels):
            panel_cm = cast('object', panels_seq[i])
            if not isinstance(panel_cm, CommentedMap):
                continue
            panel_type = _detect_panel_type_key(panel_cm)
            source_panel_type = panel_type
            if i < len(raw_panels):
                raw_type = raw_panels[i].get('type')
                if isinstance(raw_type, str):
                    source_panel_type = raw_type
            comment = _panel_todo_comment_from_raw(raw_panels, i, source_panel_type, parsed_panel)
            panels_seq_any.yaml_set_comment_before_after_key(i, before=comment)

    dashboards_any = cast('Any', dashboards)
    dashboards_any.append(dashboard_yaml)
    return document


def _detect_panel_type_key(panel: CommentedMap) -> str:
    """Detect which key is the panel type discriminator."""
    for key in ('lens', 'esql', 'markdown', 'search', 'links', 'image', 'vega'):
        if key in panel:
            return key
    return 'unknown'


def _panel_todo_comment_from_raw(
    raw_panels: list[dict[str, Any]],
    index: int,
    panel_type: str,
    parsed_panel: ParsedPanel,
) -> str:
    """Generate TODO comment using raw panel data when available, falling back to parsed data."""
    if index < len(raw_panels):
        raw = raw_panels[index]
    elif parsed_panel.simple is not None:
        raw = parsed_panel.simple.raw
    else:
        raw = {}
    raw_json = json.dumps(raw, indent=2, sort_keys=True) if raw else '{}'
    return f'TODO(decompile): complete `{panel_type}` panel config from original Kibana panel JSON.\nOriginal panel JSON:\n{raw_json}'
