"""YAML output serialization utilities for decompiled dashboards."""

from typing import Any

import yaml
from pydantic import BaseModel


class YamlDumper(yaml.SafeDumper):
    """Custom YAML dumper with human-readable formatting."""


def _str_representer(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    """Represent strings, using literal block style for multiline.

    Args:
        dumper: The YAML dumper instance.
        data: The string data to represent.

    Returns:
        YAML scalar node with appropriate style.

    """
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')  # pyright: ignore[reportUnknownMemberType]
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)  # pyright: ignore[reportUnknownMemberType]


YamlDumper.add_representer(str, _str_representer)


def model_to_yaml_dict(model: BaseModel, exclude_none: bool = True) -> dict[str, Any]:
    """Convert a Pydantic model to a YAML-friendly dictionary.

    Args:
        model: The Pydantic model to convert.
        exclude_none: Whether to exclude None values.

    Returns:
        A dictionary suitable for YAML serialization.

    """
    return model.model_dump(
        mode='json',
        by_alias=True,
        exclude_none=exclude_none,
    )


def dashboards_to_yaml(dashboards: list[dict[str, Any]]) -> str:
    """Serialize a list of dashboard dicts to YAML format.

    Args:
        dashboards: List of dashboard configuration dictionaries.

    Returns:
        YAML string with 'dashboards:' wrapper.

    """
    data = {'dashboards': dashboards}
    return yaml.dump(
        data,
        Dumper=YamlDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )


def dashboard_to_yaml(dashboard: dict[str, Any]) -> str:
    """Serialize a single dashboard dict to YAML format.

    Args:
        dashboard: Dashboard configuration dictionary.

    Returns:
        YAML string with 'dashboards:' wrapper containing single dashboard.

    """
    return dashboards_to_yaml([dashboard])
