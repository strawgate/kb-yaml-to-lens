"""Phase 3: Serialize inferred dashboard config dicts to CommentedMap YAML.

Produces a CommentedMap suitable for ruamel.yaml round-trip output,
with TODO comments attached to each panel.
"""

# pyright: reportAny=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnusedCallResult=false

import json
from typing import Any, cast

from kb_dashboard_core.dashboard.config import Dashboard
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from .parse_shared import get_dict, get_int


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


def _has_grid_data(raw_panel: dict[str, Any]) -> tuple[bool, bool]:
    """Return (has_size, has_position) based on raw panel gridData."""
    grid = get_dict(raw_panel, 'gridData')
    if grid is None:
        return False, False
    has_size = get_int(grid, 'w') is not None or get_int(grid, 'h') is not None
    has_position = get_int(grid, 'x') is not None or get_int(grid, 'y') is not None
    return has_size, has_position


def _strip_default_panel_layout(panel_yaml: CommentedMap, raw_panel: dict[str, Any] | None) -> None:
    """Preserve legacy omission of size/position when Kibana omitted grid data."""
    if raw_panel is None:
        return

    panel_yaml_any = cast('Any', panel_yaml)
    has_size, has_position = _has_grid_data(raw_panel)

    size = cast('object', panel_yaml_any.get('size'))
    if not has_size:
        if 'size' in panel_yaml:
            del panel_yaml['size']
    elif isinstance(size, CommentedMap):
        _set_flow_style(size)

    position = cast('object', panel_yaml_any.get('position'))
    if not has_position:
        if 'position' in panel_yaml:
            del panel_yaml['position']
    elif isinstance(position, CommentedMap):
        _set_flow_style(position)


def _format_panel_layouts(dashboard_yaml: CommentedMap, raw_panels: list[dict[str, Any]]) -> None:
    """Compact panel layout fields and drop model-defaulted layout when absent in source."""
    dashboard_yaml_any = cast('Any', dashboard_yaml)
    panels = cast('object', dashboard_yaml_any.get('panels'))
    if not isinstance(panels, (list, CommentedSeq)):
        return

    for i, panel_yaml in enumerate(cast('list[object]', panels)):
        if not isinstance(panel_yaml, CommentedMap):
            continue
        raw_panel = raw_panels[i] if i < len(raw_panels) else None
        _strip_default_panel_layout(panel_yaml, raw_panel)


def serialize_dashboard(
    dashboard_model: Dashboard,
    raw_panels: list[dict[str, Any]],
) -> CommentedMap:
    """Convert an inferred Dashboard config model to a CommentedMap YAML document.

    Args:
        dashboard_model: The dashboard config model from infer_dashboard().
        raw_panels: The original raw panel dicts for layout stripping and TODO comments.

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
    _format_panel_layouts(dashboard_yaml, raw_panels)

    # Attach TODO comments to each panel
    dashboard_yaml_any = cast('Any', dashboard_yaml)
    panels_seq = cast('object', dashboard_yaml_any.get('panels'))
    if isinstance(panels_seq, CommentedSeq) and len(raw_panels) == len(panels_seq):
        panels_seq_any = cast('Any', panels_seq)
        for i, raw_panel in enumerate(raw_panels):
            panel_cm = cast('object', panels_seq[i])
            if not isinstance(panel_cm, CommentedMap):
                continue
            panel_type = _detect_panel_type_key(panel_cm)
            source_panel_type = panel_type
            raw_type = raw_panel.get('type')
            if isinstance(raw_type, str):
                source_panel_type = raw_type
            comment = _panel_todo_comment(raw_panel, source_panel_type)
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


def _panel_todo_comment(
    raw_panel: dict[str, Any],
    panel_type: str,
) -> str:
    """Generate TODO comment using raw panel data."""
    raw_json = json.dumps(raw_panel, indent=2, sort_keys=True) if raw_panel else '{}'
    return f'TODO(decompile): complete `{panel_type}` panel config from original Kibana panel JSON.\nOriginal panel JSON:\n{raw_json}'
