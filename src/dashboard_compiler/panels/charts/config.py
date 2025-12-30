from typing import Annotated

from pydantic import Discriminator, Field, Tag
from pydantic.functional_validators import field_validator

from dashboard_compiler.filters.config import FilterTypes
from dashboard_compiler.panels.base import BasePanel
from dashboard_compiler.panels.charts.gauge import ESQLGaugeChart, LensGaugeChart
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

type SingleLayerChartTypes = LensMetricChart | LensGaugeChart

type ESQLChartTypes = ESQLMetricChart | ESQLGaugeChart | ESQLPieChart | ESQLBarChart | ESQLAreaChart | ESQLLineChart | ESQLTagcloudChart


class LensPanelFieldsMixin(BaseCfgModel):
    """Panel-level fields for Lens chart panels."""

    filters: list['FilterTypes'] | None = Field(default=None)
    """A list of filters to apply to the panel."""

    query: 'LegacyQueryTypes | None' = Field(default=None)
    """The query to be executed."""

    layers: list['MultiLayerChartTypes'] | None = Field(default=None)
    """Optional additional layers for multi-layer charts."""

    @field_validator('layers', mode='after')
    @classmethod
    def validate_layers(cls, layers: list['MultiLayerChartTypes'] | None) -> list['MultiLayerChartTypes'] | None:
        """Validate that reference line layers are only used with XY charts.

        Args:
            layers: The list of layers to validate.

        Returns:
            The list of layers.
        """
        if layers is None:
            return layers

        # Check if reference lines are used with compatible charts
        has_ref_line = any(isinstance(layer, LensReferenceLineLayer) for layer in layers)
        if has_ref_line:
            # Reference lines can only be used as additional layers on XY charts
            # The base chart type is not available in this validator, but we can check
            # that reference lines are not the only layers
            if all(isinstance(layer, LensReferenceLineLayer) for layer in layers):
                msg = 'Reference line layers cannot be used alone, they must be combined with an XY chart'
                raise ValueError(msg)

        return layers


class LensMetricPanelConfig(LensMetricChart, LensPanelFieldsMixin):
    """Configuration for a Lens metric panel."""


class LensGaugePanelConfig(LensGaugeChart, LensPanelFieldsMixin):
    """Configuration for a Lens gauge panel."""


class LensPiePanelConfig(LensPieChart, LensPanelFieldsMixin):
    """Configuration for a Lens pie panel."""


class LensLinePanelConfig(LensLineChart, LensPanelFieldsMixin):
    """Configuration for a Lens line panel."""


class LensBarPanelConfig(LensBarChart, LensPanelFieldsMixin):
    """Configuration for a Lens bar panel."""


class LensAreaPanelConfig(LensAreaChart, LensPanelFieldsMixin):
    """Configuration for a Lens area panel."""


class LensTagcloudPanelConfig(LensTagcloudChart, LensPanelFieldsMixin):
    """Configuration for a Lens tagcloud panel."""


type LensPanelConfig = Annotated[
    Annotated[LensMetricPanelConfig, Tag('metric')]
    | Annotated[LensGaugePanelConfig, Tag('gauge')]
    | Annotated[LensPiePanelConfig, Tag('pie')]
    | Annotated[LensLinePanelConfig, Tag('line')]
    | Annotated[LensBarPanelConfig, Tag('bar')]
    | Annotated[LensAreaPanelConfig, Tag('area')]
    | Annotated[LensTagcloudPanelConfig, Tag('tagcloud')],
    Discriminator('type'),
]


class ESQLPanelFieldsMixin(BaseCfgModel):
    """Panel-level fields for ES|QL chart panels."""

    query: 'ESQLQueryTypes' = Field(...)
    """The ES|QL query to execute."""


class ESQLMetricPanelConfig(ESQLMetricChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL metric panel."""


class ESQLGaugePanelConfig(ESQLGaugeChart, ESQLPanelFieldsMixin):
    """Configuration for an ES|QL gauge panel."""


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


type ESQLPanelConfig = Annotated[
    Annotated[ESQLMetricPanelConfig, Tag('metric')]
    | Annotated[ESQLGaugePanelConfig, Tag('gauge')]
    | Annotated[ESQLPiePanelConfig, Tag('pie')]
    | Annotated[ESQLLinePanelConfig, Tag('line')]
    | Annotated[ESQLBarPanelConfig, Tag('bar')]
    | Annotated[ESQLAreaPanelConfig, Tag('area')]
    | Annotated[ESQLTagcloudPanelConfig, Tag('tagcloud')],
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
