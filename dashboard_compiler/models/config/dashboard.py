from pydantic import BaseModel, Field

from dashboard_compiler.models.config.controls import OptionsListControl, RangeSliderControl
from dashboard_compiler.models.config.panels import LensPanel, LinksPanel, MarkdownPanel, SearchPanel
from dashboard_compiler.models.config.shared import ExistsFilter, KqlQuery, LuceneQuery, PhraseFilter, PhrasesFilter, RangeFilter


class Dashboard(BaseModel):
    """Represents the top-level dashboard object in the YAML schema."""

    id: str | None = Field(default=None, description="Unique identifier for the dashboard.")
    title: str = Field(..., description="(Required) The title of the dashboard.")
    description: str = Field("", description="(Optional) A description for the dashboard. Defaults to ''.")

    query: KqlQuery | LuceneQuery = Field(
        default_factory=KqlQuery, description="(Optional) A query string to filter the dashboard data. Defaults to an empty string."
    )

    filters: list[ExistsFilter | PhraseFilter | PhrasesFilter | RangeFilter] = Field(
        default_factory=list, description="(Optional) A list of filters to apply to the dashboard. Can be empty."
    )

    controls: list[RangeSliderControl | OptionsListControl] = Field(
        default_factory=list, description="(Optional) A list of controls panels for the dashboard. Can be empty."
    )

    panels: list[MarkdownPanel | SearchPanel | LinksPanel | LensPanel] = Field(
        default_factory=list, description="(Required) A list of panel objects defining the dashboard content. Can be empty."
    )
