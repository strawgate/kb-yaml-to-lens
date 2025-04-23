from pydantic import BaseModel, Field, model_serializer
from typing import List, Self, Dict, Any
import json
import uuid
from datetime import datetime, timezone

import yaml
from ..panels import (
    Panel,
    SearchPanel,
    MarkdownPanel,
    MapPanel,
    LensPanel,
)

type AnyPanelType = SearchPanel | MarkdownPanel | MapPanel | LensPanel


DEFAULT_OPTIONS_DICT = {
    "useMargins": True,
    "syncColors": False,
    "syncCursor": True,
    "syncTooltips": False,
    "hidePanelTitles": False,
}


DEFAULT_CONTROL_GROUP_INPUT_DICT = {
    "chainingSystem": "HIERARCHICAL",
    "controlStyle": "oneLine",
    "ignoreParentSettingsJSON": json.dumps(
        {
            "ignoreFilters": False,
            "ignoreQuery": False,
            "ignoreTimerange": False,
            "ignoreValidations": False,
        }
    ),
    "panelsJSON": "{}",
    "showApplySelections": False,
}


DEFAULT_KIBANA_SAVED_OBJECT_META_DICT = {
    "searchSourceJSON": json.dumps(
        {
            "filter": [],
            "query": {"query": "", "language": "kuery"},
        }
    )
}


class Dashboard(BaseModel):
    title: str
    description: str = ""

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
    def load(cls, yaml_path: str) -> "Dashboard":
        """
        Load a dashboard YAML file and returns a Dashboard model instance.

        Args:
            yaml_path: Path to the dashboard YAML configuration file.

        Returns:
            An instance of the Dashboard model.
        """
        with open(yaml_path, "r") as f:
            yaml_data = yaml.safe_load(f)

        return cls.model_validate(yaml_data["dashboard"], strict=True)

    @classmethod
    def loads(cls, yaml_content: str) -> "Dashboard":
        """
        Load a dashboard YAML content string and returns a Dashboard model instance.

        Args:
            yaml_content: YAML content as a string.

        Returns:
            An instance of the Dashboard model.
        """
        yaml_data = yaml.safe_load(yaml_content)
        return cls.model_validate(yaml_data["dashboard"], strict=True)

    @model_serializer
    def to_dict(self) -> Dict[str, Any]:
        """Generates a dictionary representing the dashboard in Kibana format."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        dashboard_id = str(uuid.uuid4())

        dashboard_dict: Dict[str, Any] = {
            "attributes": {
                "controlGroupInput": DEFAULT_CONTROL_GROUP_INPUT_DICT,
                "description": self.description,
                "kibanaSavedObjectMeta": DEFAULT_KIBANA_SAVED_OBJECT_META_DICT,
                "optionsJSON": json.dumps(DEFAULT_OPTIONS_DICT),
                "panelsJSON": self.panels,
                "timeRestore": False,
                "title": self.title,
                "version": 3,
            },
            "coreMigrationVersion": "8.8.0",
            "created_at": now_iso,
            "created_by": "compiler",
            "id": dashboard_id,
            "managed": False,
            "references": [],
            "type": "dashboard",
            "typeMigrationVersion": "10.2.0",
            "updated_at": now_iso,
            "updated_by": "compiler",
            "version": "WzEsMV0=",
        }

        return dashboard_dict

    def to_json(self) -> str:
        """Generates the final JSON string for the dashboard."""
        return json.dumps(self.to_dict(), indent=2)
