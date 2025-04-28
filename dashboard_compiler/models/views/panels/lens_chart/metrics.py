from typing import Literal

from pydantic import Field, model_serializer

from dashboard_compiler.models.views.panels.lens import KbnBaseStateVisualization, KbnBaseStateVisualizationLayer


class KbnMetricsStateVisualizationLayer(KbnBaseStateVisualizationLayer):
    """Represents a layer within a Metric visualization state in the Kibana JSON structure."""

    layerType: Literal["data"] = "data"
    metricAccessor: str = Field(..., description="The ID of the metric column.")


class KbnLensMetricsVisualizationState(KbnBaseStateVisualization):
    """Represents the 'visualization' object for a Metric chart in the Kibana JSON structure."""

    pass

    @model_serializer()
    def serialize_model(self):
        return self.layers[0].model_dump(serialize_as_any=True, exclude_none=True) if self.layers else None
