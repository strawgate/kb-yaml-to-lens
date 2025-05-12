"""Provides functions to load, render, and dump YAML-to-Lens Dashboards."""

from pathlib import Path

import yaml

from dashboard_compiler.dashboard.compile import compile_dashboard
from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard.view import KbnDashboard


def load(path: str) -> Dashboard:
    """Load a dashboard configuration from a YAML file.

    Args:
        path (str): The path to the YAML file containing the dashboard configuration.

    Returns:
        Dashboard: The loaded Dashboard object.

    """
    load_path = Path(path)

    with load_path.open(path) as file:
        dashboard_dict = yaml.safe_load(file)

    return Dashboard(**dashboard_dict['dashboard'])


def render(dashboard: Dashboard | dict) -> KbnDashboard:
    """Render a Dashboard object into its Kibana JSON representation.

    Args:
        dashboard (Dashboard | dict): The Dashboard object to render.

    Returns:
        KbnDashboard: The rendered Kibana dashboard view model.

    """
    if isinstance(dashboard, dict):
        dashboard = Dashboard(**dashboard['dashboard'])

    return compile_dashboard(dashboard)


def dump(dashboard: Dashboard, path: str) -> None:
    """Dump a Dashboard object to a YAML file.

    Args:
        dashboard (Dashboard): The Dashboard object to dump.
        path (str): The path where the YAML file will be saved.

    """
    dashboard_path = Path(path)

    with dashboard_path.open(mode='w', encoding='utf-8') as file:
        dashboard_as_dict = dashboard.model_dump(serialize_as_any=True, exclude_none=True)
        yaml.dump(dashboard_as_dict, file, default_flow_style=False, sort_keys=False)
