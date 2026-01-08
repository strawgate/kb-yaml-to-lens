from typing import Annotated

from pydantic import Discriminator, Field, Tag

from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.charts.datatable import ESQLDatatableChart, LensDatatableChart
from dashboard_compiler.panels.charts.gauge import ESQLGaugeChart, LensGaugeChart
from dashboard_compiler.panels.charts.heatmap import ESQLHeatmapChart, LensHeatmapChart
from dashboard_compiler.panels.charts.metric import ESQLMetricChart, LensMetricChart
from dashboard_compiler.panels.charts.pie import ESQLPieChart, LensPieChart
from dashboard_compiler.panels.charts.tagcloud import ESQLTagcloudChart, LensTagcloudChart
from dashboard_compiler.panels.charts.xy.config import (
    ESQLAreaChart,
    ESQLBarChart,
    ESQLLineChart,
    LensAreaChart,
    LensBarChart,
    LensLineChart,
    LensReferenceLineLayer,
)
from dashboard_compiler.queries.types import ESQLQueryTypes, LegacyQueryTypes
from dashboard_compiler.shared.config import BaseCfgModel

type AllChartTypes = LensChartTypes | ESQLChartTypes

type LensChartTypes = MultiLayerChartTypes | SingleLayerChartTypes

type MultiLayerChartTypes = LensPieChart | LensLineChart | LensBarChart | LensAreaChart | LensTagcloudChart | LensReferenceLineLayer

type SingleLayerChartTypes = LensMetricChart | LensDatatableChart | LensGaugeChart | LensHeatmapChart

type ESQLChartTypes = (
    ESQLMetricChart
    | ESQLGaugeChart
    | ESQLHeatmapChart
    | ESQLPieChart
    | ESQLBarChart
    | ESQLAreaChart
    | ESQLLineChart
    | ESQLDatatableChart
    | ESQLTagcloudChart
)


class LensPanelFieldsMixin(BaseCfgModel):
    """Panel-level fields for Lens chart panels."""

    filters: list['FilterTypes'] | None = Field(default=None)
    """A list of filters to apply to the panel."""

    query: 'LegacyQueryTypes | None' = Field(default=None)
    """The query to be executed."""


class LensXYPanelFieldsMixin(LensPanelFieldsMixin):
    """Panel-level fields for XY chart panels (line, bar, area)."""

    layers: list['MultiLayerChartTypes'] | None = Field(default=None)
    """Optional additional layers for multi-layer XY charts (including reference lines)."""


class LensMetricPanelConfig(LensMetricChart, LensPanelFieldsMixin):
    """Configuration for a Lens metric panel."""


class LensGaugePanelConfig(LensGaugeChart, LensPanelFieldsMixin):
    """Configuration for a Lens gauge panel."""


class LensHeatmapPanelConfig(LensHeatmapChart, LensPanelFieldsMixin):
    """Configuration for a Lens heatmap panel."""


class LensPiePanelConfig(LensPieChart, LensPanelFieldsMixin):
    """Configuration for a Lens pie panel."""


class LensLinePanelConfig(LensLineChart, LensXYPanelFieldsMixin):
    """Configuration for a Lens line panel."""


class LensBarPanelConfig(LensBarChart, LensXYPanelFieldsMixin):
    """Configuration for a Lens bar panel."""


class LensAreaPanelConfig(LensAreaChart, LensXYPanelFieldsMixin):
    """Configuration for a Lens area panel."""


class LensTagcloudPanelConfig(LensTagcloudChart, LensPanelFieldsMixin):
    """Configuration for a Lens tagcloud panel."""


class LensDatatablePanelConfig(LensDatatableChart, LensPanelFieldsMixin):
    """Configuration for a Lens datatable panel."""


type LensPanelConfig = Annotated[
    Annotated[LensMetricPanelConfig, Tag('metric')]
    | Annotated[LensGaugePanelConfig, Tag('gauge')]
    | Annotated[LensHeatmapPanelConfig, Tag('heatmap')]
    | Annotated[LensPiePanelConfig, Tag('pie')]
    | Annotated[LensLinePanelConfig, Tag('line')]
    | Annotated[LensBarPanelConfig, Tag('bar')]
    | Annotated[LensAreaPanelConfig, Tag('area')]
    | Annotated[LensTagcloudPanelConfig, Tag('tagcloud')]
    | Annotated[LensDatatablePanelConfig, Tag('datatable')],
    Discriminator('type'),
]


class ESQLPanelFieldsMixin(BaseCfgModel):
    """Panel-level fields for ES|QL chart panels."""

    query: 'ESQLQueryTypes' = Field(...)
    """The ES|QL query to execute."""

    time_field: str = Field(default='@timestamp')
    """The time field to use for the dashboard time picker. Defaults to '@timestamp'."""


class ESQLMetricPanelConfig(ESQLMetricChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL metric panel."""


class ESQLGaugePanelConfig(ESQLGaugeChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL gauge panel."""


class ESQLHeatmapPanelConfig(ESQLHeatmapChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL heatmap panel."""


class ESQLPiePanelConfig(ESQLPieChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL pie panel."""


class ESQLLinePanelConfig(ESQLLineChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL line panel."""


class ESQLBarPanelConfig(ESQLBarChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL bar panel."""


class ESQLAreaPanelConfig(ESQLAreaChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL area panel."""


class ESQLTagcloudPanelConfig(ESQLTagcloudChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL tagcloud panel."""


class ESQLDatatablePanelConfig(ESQLDatatableChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL datatable panel."""


type ESQLPanelConfig = Annotated[
    Annotated[ESQLMetricPanelConfig, Tag('metric')]
    | Annotated[ESQLGaugePanelConfig, Tag('gauge')]
    | Annotated[ESQLHeatmapPanelConfig, Tag('heatmap')]
    | Annotated[ESQLPiePanelConfig, Tag('pie')]
    | Annotated[ESQLLinePanelConfig, Tag('line')]
    | Annotated[ESQLBarPanelConfig, Tag('bar')]
    | Annotated[ESQLAreaPanelConfig, Tag('area')]
    | Annotated[ESQLTagcloudPanelConfig, Tag('tagcloud')]
    | Annotated[ESQLDatatablePanelConfig, Tag('datatable')],
    Discriminator('type'),
]


class LensPanel(BasePanel):
    """Represents a Lens chart panel (single or multi-layer).

    The lens field contains a discriminated union of chart panel configurations.
    The chart type is determined by the 'type' field.
    """

    lens: LensPanelConfig = Field(...)
    """Lens panel configuration."""


class ESQLPanel(BasePanel):
    """Represents an ES|QL chart panel.

    The esql field contains a discriminated union of ES|QL chart panel configurations.
    The chart type is determined by the 'type' field.
    """

    esql: ESQLPanelConfig = Field(...)
    """ES|QL panel configuration."""
