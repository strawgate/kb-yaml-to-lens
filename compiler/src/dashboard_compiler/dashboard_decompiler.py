"""Decompile Kibana dashboard JSON back to YAML configuration.

This module provides the inverse of dashboard_compiler.py, transforming
Kibana dashboard NDJSON back into the YAML configuration format.
"""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard.view import KbnDashboard
from dashboard_compiler.shared.decompile_context import DecompileContext, DecompileError, DecompileWarning
from dashboard_compiler.tools.yaml_writer import dashboard_to_yaml, dashboards_to_yaml, model_to_yaml_dict

# Re-export for public API
__all__ = ['DecompileContext', 'DecompileError', 'DecompileWarning', 'decompile', 'decompile_to_yaml', 'load_ndjson']


def parse_ndjson_dashboards(content: str) -> list[dict[str, Any]]:
    """Parse NDJSON content and extract all dashboard objects.

    Args:
        content: NDJSON content (newline-delimited JSON objects).

    Returns:
        List of dashboard dictionaries.

    """
    dashboards: list[dict[str, Any]] = []
    for line in content.strip().split('\n'):
        if len(line.strip()) == 0:
            continue
        obj = json.loads(line)  # pyright: ignore[reportAny]
        if obj.get('type') == 'dashboard':  # pyright: ignore[reportAny]
            dashboards.append(obj)  # pyright: ignore[reportAny]
    return dashboards


def load_ndjson(path: Path) -> list[dict[str, Any]]:
    """Load dashboards from an NDJSON file.

    Args:
        path: Path to the NDJSON file.

    Returns:
        List of dashboard dictionaries.

    """
    content = path.read_text(encoding='utf-8')
    return parse_ndjson_dashboards(content)


def decompile_dashboard_dict(
    dashboard_dict: dict[str, Any],
    *,
    context: DecompileContext | None = None,
) -> Dashboard:
    """Decompile a dashboard dictionary to a Dashboard config model.

    Args:
        dashboard_dict: The raw dashboard dictionary from JSON.
        context: Optional decompilation context for warnings.

    Returns:
        The decompiled Dashboard configuration model.

    """
    if context is None:
        context = DecompileContext()

    # Parse through KbnDashboard view model for validation
    kbn_dashboard = KbnDashboard.model_validate(dashboard_dict)

    # Store references for panel decompilation
    context.references = kbn_dashboard.references

    # Import here to avoid circular imports
    from dashboard_compiler.dashboard.decompile import decompile_dashboard

    return decompile_dashboard(kbn_dashboard, context=context)


def decompile(
    path: Path,
    *,
    strict: bool = False,
) -> tuple[list[Dashboard], list[DecompileWarning]]:
    """Decompile a Kibana dashboard NDJSON file to Dashboard config models.

    Args:
        path: Path to the NDJSON file.
        strict: If True, raise errors instead of warnings for unsupported features.

    Returns:
        Tuple of (list of Dashboard models, list of warnings).

    """
    context = DecompileContext(strict=strict)
    dashboard_dicts = load_ndjson(path)

    dashboards: list[Dashboard] = []
    for dashboard_dict in dashboard_dicts:
        dashboard = decompile_dashboard_dict(dashboard_dict, context=context)
        dashboards.append(dashboard)

    return dashboards, context.warnings


def decompile_to_yaml(
    path: Path,
    *,
    strict: bool = False,
) -> tuple[str, list[DecompileWarning]]:
    """Decompile a Kibana dashboard NDJSON file to YAML string.

    Args:
        path: Path to the NDJSON file.
        strict: If True, raise errors instead of warnings for unsupported features.

    Returns:
        Tuple of (YAML string, list of warnings).

    """
    dashboards_list, warnings = decompile(path, strict=strict)

    yaml_dicts = [model_to_yaml_dict(d) for d in dashboards_list]
    yaml_str = dashboard_to_yaml(yaml_dicts[0]) if len(yaml_dicts) == 1 else dashboards_to_yaml(yaml_dicts)

    return yaml_str, warnings


def dashboards_to_yaml_wrapper(dashboards: Sequence[dict[str, Any]]) -> str:
    """Convert dashboard dicts to YAML.

    Args:
        dashboards: Sequence of dashboard configuration dictionaries.

    Returns:
        YAML string with 'dashboards:' wrapper.

    """
    return dashboards_to_yaml(list(dashboards))
