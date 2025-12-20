"""Provides functions to load, render, and dump YAML-to-Lens Dashboards."""

from pathlib import Path

import yaml

from dashboard_compiler.dashboard.compile import compile_dashboard
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard.view import KbnDashboard


def load(path: str) -> list[Dashboard]:
    """Load dashboard configurations from a YAML file.

    Args:
        path (str): The path to the YAML file containing the dashboard configuration.

    Returns:
        list[Dashboard]: The loaded Dashboard objects.

    """
    load_path = Path(path)

    with load_path.open() as file:
        config = yaml.safe_load(file)

    dashboards_data = config.get('dashboards', [])
    if not isinstance(dashboards_data, list):
        msg = f"'dashboards' must be a list in YAML file: {path}"
        raise TypeError(msg)

    return [Dashboard(**dashboard_data) for dashboard_data in dashboards_data]


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
