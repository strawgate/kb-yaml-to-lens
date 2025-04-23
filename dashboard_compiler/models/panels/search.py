from typing import Dict, Any, Literal
import uuid  # Import uuid


from dashboard_compiler.models.panels.base import Panel


class SearchPanel(Panel):
    saved_search_id: str
    type: Literal["search"] = "search"

    def to_dict(self) -> Dict[str, Any]:
        panel_id = str(uuid.uuid4())
        grid_data = self.grid.model_dump(exclude_none=True)
        grid_data["i"] = panel_id

        return {
            "type": "search",
            "panelIndex": panel_id,
            "gridData": grid_data,
            "embeddableConfig": {"enhancements": {}},
            "version": "8.7.1",
        }
