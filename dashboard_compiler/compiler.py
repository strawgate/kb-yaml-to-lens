import yaml
from .models import Dashboard

def compile_dashboard(yaml_path: str) -> str:
    """
    Loads a dashboard YAML file, parses it into a Dashboard model,
    and compiles it into a JSON string.
    """
    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)
    
    # Use the Dashboard model to parse and validate the YAML data
    dashboard = Dashboard.model_validate(yaml_data)
    
    # Use the to_json method of the Dashboard model to generate the JSON string
    return dashboard.to_json()

if __name__ == "__main__":
    # Example usage with one of the provided YAML files
    print(compile_dashboard("configs/audit-events-summary.yaml"))