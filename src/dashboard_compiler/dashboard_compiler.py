"""Provides functions to load, render, and dump YAML-to-Lens Dashboards."""

from pathlib import Path
from typing import Any

import yaml

from dashboard_compiler.dashboard.compile import compile_dashboard
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard.view import KbnDashboard
from dashboard_compiler.shared import ensure_dict, ensure_list


def load(path: str) -> list[Dashboard]:
    """Load dashboard configurations from a YAML file.

    Args:
        path (str): The path to the YAML file containing the dashboard configuration.

    Returns:
        list[Dashboard]: The loaded Dashboard objects.

    """
    load_path = Path(path)

    with load_path.open() as file:
        config: Any = yaml.safe_load(file)  # pyright: ignore[reportAny]

    config_dict = ensure_dict(config, f'YAML file {path}')
    dashboards_data: Any = config_dict.get('dashboards', [])
    dashboards_list = ensure_list(dashboards_data, f"'dashboards' key in {path}")

    dashboards: list[Dashboard] = []
    for i, dashboard_data in enumerate(dashboards_list):
        dashboard_dict = ensure_dict(dashboard_data, f'Dashboard entry {i} in {path}')
        dashboards.append(Dashboard(**dashboard_dict))  # pyright: ignore[reportUnknownArgumentType]

    return dashboards


def render(dashboard: Dashboard) -> KbnDashboard:
    """Render a Dashboard object into its Kibana JSON representation.

    Args:
        dashboard (Dashboard): The Dashboard object to render.

    Returns:
        KbnDashboard: The rendered Kibana dashboard view model.

    """
    return compile_dashboard(dashboard)


def dump(dashboards: list[Dashboard], path: str) -> None:
    """Dump Dashboard objects to a YAML file.

    Args:
        dashboards (list[Dashboard]): The Dashboard objects to dump.
        path (str): The path where the YAML file will be saved.

    """
    dashboard_path = Path(path)

    with dashboard_path.open(mode='w', encoding='utf-8') as file:
        dashboards_as_list = [dashboard.model_dump(serialize_as_any=True, exclude_none=True) for dashboard in dashboards]
        config = {'dashboards': dashboards_as_list}
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)
