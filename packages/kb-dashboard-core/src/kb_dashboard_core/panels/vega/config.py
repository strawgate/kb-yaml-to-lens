"""Configuration for a Vega Panel in a dashboard."""

from typing import Any

from pydantic import Field

from kb_dashboard_core.panels.base import BasePanel
from kb_dashboard_core.shared.config import BaseCfgModel


class VegaPanelConfig(BaseCfgModel):
    """Configuration specific to Vega panels."""

    spec: dict[str, Any] = Field(...)
    """The Vega specification as a structured YAML/JSON object."""


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
