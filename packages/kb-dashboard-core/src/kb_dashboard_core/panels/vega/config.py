"""Configuration for a Vega Panel in a dashboard."""

from typing import Any

from pydantic import Field, model_validator

from kb_dashboard_core.panels.base import BasePanel
from kb_dashboard_core.shared.config import BaseCfgModel


class VegaPanelConfig(BaseCfgModel):
    """Configuration specific to Vega panels."""

    spec: dict[str, Any] = Field(...)
    """The Vega specification as a structured YAML/JSON object."""

    @model_validator(mode='before')
    @classmethod
    def validate_spec_is_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Validate that spec is a dictionary, not a string."""
        spec: object = data.get('spec')
        if isinstance(spec, str):
            msg = 'Vega spec must be provided as a YAML/JSON object, not a string'
            raise TypeError(msg)
        if spec is not None and not isinstance(spec, dict):
            msg = f'Vega spec must be a dictionary, got {type(spec).__name__}'
            raise TypeError(msg)
        return data


class VegaPanel(BasePanel):
    """Represents a Vega panel configuration.

    Vega panels are used to create custom visualizations using the Vega grammar.

    Examples:
        Minimal Vega panel:
        ```yaml
        dashboards:
          - name: "Dashboard with Vega"
            panels:
              - title: "Hello Vega"
                size: { w: 24, h: 15 }
                vega:
                  spec:
                    $schema: https://vega.github.io/schema/vega/v3.json
                    width: 100
                    height: 30
                    marks:
                      - type: text
                        encode:
                          update:
                            text:
                              value: "Hello Vega!"
        ```

        Vega panel with Elasticsearch data:
        ```yaml
        dashboards:
          - name: "Vega Data Dashboard"
            panels:
              - title: "Custom Chart"
                size: { w: 48, h: 20 }
                vega:
                  spec:
                    $schema: https://vega.github.io/schema/vega-lite/v5.json
                    data:
                      url:
                        index: logs-*
                        body:
                          size: 0
                          aggs:
                            time_buckets:
                              date_histogram:
                                field: "@timestamp"
                                fixed_interval: 1h
                    mark: line
                    encoding:
                      x:
                        field: key
                        type: temporal
                      y:
                        field: doc_count
                        type: quantitative
        ```
    """

    vega: VegaPanelConfig = Field(...)
    """Vega panel configuration."""
