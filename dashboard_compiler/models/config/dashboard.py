import uuid
from pydantic import BaseModel, Field
from typing import List, Union

from dashboard_compiler.models.config.panels import MarkdownPanel, SearchPanel, LinksPanel
from dashboard_compiler.models.config.panels import LensPanel
from dashboard_compiler.models.config.controls import OptionsListControl, RangeSliderControl


class Dashboard(BaseModel):
    """Represents the top-level dashboard object in the YAML schema."""

    id: str = Field(default=str(uuid.uuid4()), description="Unique identifier for the dashboard.")
    title: str = Field(..., description="(Required) The title of the dashboard.")
    description: str = Field("", description="(Optional) A description for the dashboard. Defaults to ''.")

    controls: List[Union[RangeSliderControl, OptionsListControl]] = Field(
        default_factory=list, description="(Optional) A list of controls panels for the dashboard. Can be empty."
    )

    panels: List[Union[MarkdownPanel, SearchPanel, LinksPanel, LensPanel]] = Field(
        default_factory=list, description="(Required) A list of panel objects defining the dashboard content. Can be empty."
    )
