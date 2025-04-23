import yaml
from .models.dashboard.base import Dashboard

from typing import Dict, Any  # Add typing import


def loads(yaml_path: str) -> Dict[str, Any]:  # Changed return type hint
    """
    Loads a dashboard YAML file and returns its content as a Python dictionary.
    """
    with open(yaml_path, "r") as f:
        yaml_data = yaml.safe_load(f)

    return yaml_data["dashboard"]


def compile_dashboard_to_testable_dict(
    yaml_path: str,
) -> Dict[str, Any]:  # Changed return type hint
    """
    Loads a dashboard YAML file, parses it into a Dashboard model,
    and compiles it into a Python dictionary matching the Kibana JSON structure.
    """
    with open(yaml_path, "r") as f:
        yaml_data = yaml.safe_load(f)

    # Use the Dashboard model to parse and validate the YAML data
    dashboard = Dashboard.model_validate(yaml_data["dashboard"])

    # Use the to_dict method of the Dashboard model to generate the dictionary
    return dashboard.to_dict()


def compile_dashboard(yaml_path: str) -> Dict[str, Any]:  # Changed return type hint
    """
    Loads a dashboard YAML file, parses it into a Dashboard model,
    and compiles it into a Python dictionary matching the Kibana JSON structure.
    """
    with open(yaml_path, "r") as f:
        yaml_data = yaml.safe_load(f)

    # Use the Dashboard model to parse and validate the YAML data
    dashboard = Dashboard.model_validate(yaml_data["dashboard"])

    # Use the to_dict method of the Dashboard model to generate the dictionary
    return dashboard.to_dict()


if __name__ == "__main__":
    # Example usage with one of the provided YAML files
    # Example usage needs json.dumps if we want to print the final JSON
    import json

    print(
        json.dumps(
            compile_dashboard_to_testable_dict("configs/complex/audit-events-summary.yaml"),
            indent=2,
        )
    )
