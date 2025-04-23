from pydantic import BaseModel, Field
from typing import List, Self, Union, Dict, Any
import json
import uuid
from datetime import datetime, timezone

import yaml
from .panels import Panel, SearchPanel, MarkdownPanel, MapPanel, LensPanel # Import panel types

type AnyPanelType = SearchPanel | MarkdownPanel | MapPanel | LensPanel

# Default Kibana options structure (as dict)
DEFAULT_OPTIONS_DICT = {
    "useMargins": True,
    "syncColors": False,
    "syncCursor": True,
    "syncTooltips": False,
    "hidePanelTitles": False
}

# Default Kibana control group input structure (as dict)
DEFAULT_CONTROL_GROUP_INPUT_DICT = {
    "chainingSystem": "HIERARCHICAL",
    "controlStyle": "oneLine",
    "ignoreParentSettingsJSON": json.dumps({ # Inner JSON string is expected by Kibana
        "ignoreFilters": False,
        "ignoreQuery": False,
        "ignoreTimerange": False,
        "ignoreValidations": False
    }),
    "panelsJSON": "{}", # Inner JSON string is expected by Kibana
    "showApplySelections": False
}

# Default Kibana saved object meta structure (as dict)
DEFAULT_KIBANA_SAVED_OBJECT_META_DICT = {
    "searchSourceJSON": json.dumps({ # Inner JSON string is expected by Kibana
        "filter": [],
        "query": {
            "query": "",
            "language": "kuery"
        }
    })
}


class Dashboard(BaseModel):
    title: str
    description: str = ""
    # Use Field(..., discriminator='type') for Pydantic v2 to handle different panel types
    # For now, keeping the Union, assuming validation happens correctly elsewhere or needs refinement
    panels: List[SearchPanel | MarkdownPanel | MapPanel | LensPanel] = Field(default_factory=list)

    def add_panel(self, panel: AnyPanelType) -> Self:
        """
        Adds a panel to the dashboard.
        
        Args:
            panel: An instance of Panel or its subclasses (SearchPanel, MarkdownPanel, MapPanel, LensPanel, etc).
        
        Returns:
            The updated Dashboard instance.
        """
        if not isinstance(panel, Panel):
            raise TypeError("panel must be an instance of Panel or its subclasses")
        
        self.panels.append(panel)

        return self
    
    def remove_panel(self, panel: AnyPanelType) -> Self:
        """
        Removes a panel from the dashboard.
        
        Args:
            panel: An instance of Panel or its subclasses to be removed.
        
        Returns:
            The updated Dashboard instance.
        """
        if panel in self.panels:
            self.panels.remove(panel)
        else:
            raise ValueError("Panel not found in the dashboard")

        return self

    @classmethod
    def load(cls, yaml_path: str) -> 'Dashboard':
        """
        Load a dashboard YAML file and returns a Dashboard model instance.
        
        Args:
            yaml_path: Path to the dashboard YAML configuration file.
        
        Returns:
            An instance of the Dashboard model.
        """
        with open(yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        return cls.loads(yaml_data)

    @classmethod
    def loads(cls, yaml_content: str) -> 'Dashboard':
        """
        Load a dashboard YAML content string and returns a Dashboard model instance.
        
        Args:
            yaml_content: YAML content as a string.
        
        Returns:
            An instance of the Dashboard model.
        """
        yaml_data = yaml.safe_load(yaml_content)
        return cls.model_validate(yaml_data["dashboard"], strict=True)

    def to_dict(self, panels_as_json = True) -> Dict[str, Any]: # Renamed to to_dict for clarity
        """Generates a dictionary representing the dashboard in Kibana format."""
        now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        dashboard_id = str(uuid.uuid4()) # Generate a unique ID

        dashboard_dict: Dict[str, Any] = {
            "attributes": {
                # Using dicts directly where possible, keeping inner JSON strings where Kibana expects them
                "controlGroupInput": DEFAULT_CONTROL_GROUP_INPUT_DICT,
                "description": self.description,
                "kibanaSavedObjectMeta": DEFAULT_KIBANA_SAVED_OBJECT_META_DICT,
                "optionsJSON": json.dumps(DEFAULT_OPTIONS_DICT), # Kibana expects this as a string
                # panelsJSON should contain the list of panel dicts directly for matching
                "panelsJSON": [], # To be populated in a moment
                "timeRestore": False, # Default value from sample
                "title": self.title,
                "version": 3 # Version from sample
            },
            "coreMigrationVersion": "8.8.0", # From sample
            "created_at": now_iso,
            "created_by": "compiler", # Placeholder user
            "id": dashboard_id,
            "managed": False, # Default value from sample
            "references": [], # Assuming no references for now
            "type": "dashboard",
            "typeMigrationVersion": "10.2.0", # From sample
            "updated_at": now_iso,
            "updated_by": "compiler", # Placeholder user
            "version": "WzEsMV0=" # Placeholder Kibana internal version string
        }

        # Populate panelsJSON with the serialized panel data
        panels = [panel.to_dict() for panel in self.panels]
        if panels_as_json:
            dashboard_dict["attributes"]["panelsJSON"] = json.dumps(panels)
        else:
            dashboard_dict["attributes"]["panelsJSON"] = panels

        return dashboard_dict

    def to_json(self) -> str:
        """Generates the final JSON string for the dashboard."""
        return json.dumps(self.to_dict(), indent=2)

    # def to_dict(self) -> Dict[str, Any]:
    #     """Generates a dictionary representation of the dashboard."""
    #     dashboard_dict = self.to_testable_dict()

    #     dashboard_dict["attributes"]["panelsJSON"] = json.dumps(dashboard_dict["attributes"]["panelsJSON"])
        
    #     return dashboard_dict

    # def to_dict(self) -> str:
    #     """Generates the final JSON string for the dashboard."""
        
    #     return json.dumps(self.to_dict(), indent=2)