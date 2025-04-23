from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Dict, Any, Optional, Union
import json

class Grid(BaseModel):
    x: int
    y: int
    w: int
    h: int

class Panel(BaseModel):
    title: str
    type: str
    grid: Grid

    @model_validator(mode='before')
    @classmethod
    def set_model_type(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        panel_type = data.get('type')
        if panel_type == 'search':
            return SearchPanel(**data)
        elif panel_type == 'markdown':
            return MarkdownPanel(**data)
        elif panel_type == 'map':
            return MapPanel(**data)
        elif panel_type == 'lens':
            return LensPanel(**data)
        return data

    def to_json(self) -> Dict[str, Any]:
        # This will be overridden by subclasses
        return self.model_dump(exclude_none=True)

# Panel Subclasses
class SearchPanel(Panel):
    saved_search_id: str

    def to_json(self) -> Dict[str, Any]:
        # Basic structure for a search panel in JSON
        return {
            "type": "search",
            "panelIndex": "placeholder", # Need to handle index generation
            "gridData": self.grid.model_dump(exclude_none=True),
            "embeddableConfig": {
                "enhancements": {}
            },
            "version": "8.7.1" # Placeholder version
        }

class MarkdownPanel(Panel):
    content: str

    def to_json(self) -> Dict[str, Any]:
        # Structure for a markdown panel (visualization type in JSON)
        return {
            "type": "visualization",
            "panelIndex": "placeholder", # Need to handle index generation
            "gridData": self.grid.model_dump(exclude_none=True),
            "embeddableConfig": {
                "enhancements": {},
                "savedVis": {
                    "data": {
                        "aggs": [],
                        "searchSource": {
                            "filter": [],
                            "query": {
                                "language": "kuery",
                                "query": ""
                            }
                        }
                    },
                    "description": "",
                    "id": "", # Placeholder ID
                    "params": {
                        "fontSize": 12, # Default font size
                        "openLinksInNewTab": False, # Default
                        "markdown": self.content
                    },
                    "title": self.title,
                    "type": "markdown", # Kibana visualization type
                    "uiState": {}
                }
            }
        }

class MapLayerStyle(BaseModel):
    type: str
    size: Optional[int] = None
    color: Optional[str] = None

class MapLayer(BaseModel):
    type: str
    label: Optional[str] = None
    index_pattern: Optional[str] = None
    query: Optional[str] = None
    geo_field: Optional[str] = None
    style: Optional[MapLayerStyle] = None
    tooltip_fields: Optional[List[str]] = None

    def to_json(self) -> Dict[str, Any]:
        json_data = {
            "type": self.type,
            "label": self.label,
        }
        if self.index_pattern:
            json_data["sourceDescriptor"] = {
                "type": "ES_SEARCH", # Assuming ES_SEARCH for data layers
                "indexPatternRefName": "placeholder" # Need to handle reference names
            }
            json_data["index_pattern"] = self.index_pattern # This might be redundant depending on final JSON structure
        elif self.type == "vector_tile":
             json_data["sourceDescriptor"] = {
                "type": "EMS_TMS", # Assuming EMS_TMS for vector_tile
                "isAutoSelect": True # Common for base maps
            }

        if self.query:
            json_data["query"] = {"language": "kuery", "query": self.query}

        if self.geo_field:
            if "sourceDescriptor" not in json_data:
                 json_data["sourceDescriptor"] = {}
            json_data["sourceDescriptor"]["geoField"] = self.geo_field

        if self.style:
            json_data["style"] = self.style.model_dump(exclude_none=True)

        if self.tooltip_fields is not None:
             if "sourceDescriptor" not in json_data:
                 json_data["sourceDescriptor"] = {}
             json_data["sourceDescriptor"]["tooltipProperties"] = [{"field": field} for field in self.tooltip_fields] # Assuming this format

        # Remove None values and empty lists/dicts
        json_data = {k: v for k, v in json_data.items() if v is not None and v != {} and v != []}

        return json_data


class MapPanel(Panel):
    layers: List[MapLayer]

    def to_json(self) -> Dict[str, Any]:
        # Structure for a map panel in JSON
        return {
            "type": "map",
            "panelIndex": "placeholder", # Need to handle index generation
            "gridData": self.grid.model_dump(exclude_none=True),
            "embeddableConfig": {
                "attributes": {
                    "title": self.title,
                    "description": "", # Map panels in samples have empty description
                    "layerListJSON": json.dumps([layer.to_json() for layer in self.layers]),
                    "mapStateJSON": "{}", # Placeholder map state
                    "uiStateJSON": "{}" # Placeholder ui state
                },
                "enhancements": {},
                "hiddenLayers": [], # Assuming no hidden layers for now
                "isLayerTOCOpen": False, # Default
                "mapBuffer": {}, # Placeholder map buffer
                "mapCenter": {}, # Placeholder map center
                "openTOCDetails": [] # Default
            },
            "version": "8.7.1" # Placeholder version
        }

class Filter(BaseModel):
    field: str
    type: str
    value: Any
    negate: bool = False

    def to_json(self) -> Dict[str, Any]:
        # Structure for a filter in JSON
        json_data: Dict[str, Any] = {
            "$state": {"store": "appState"}, # Assuming appState for now
            "meta": {
                "alias": None, # No alias in samples
                "disabled": False, # Not disabled in samples
                "field": self.field,
                "index": "placeholder", # Need to handle index references
                "key": self.field,
                "negate": self.negate,
                "type": self.type,
                "value": self.value # Redundant with params for phrase, but present in samples
            },
            "query": {} # Placeholder query structure
        }
        if self.type == "phrase":
            json_data["meta"]["params"] = {"query": self.value}
        elif self.type == "phrases":
            json_data["meta"]["params"] = self.value # Value is already a list for phrases

        # Remove None values and empty lists/dicts
        json_data["meta"] = {k: v for k, v in json_data["meta"].items() if v is not None and v != {} and v != []}
        json_data = {k: v for k, v in json_data.items() if v is not None and v != {} and v != []}

        return json_data

class Dimension(BaseModel):
    field: str
    type: str
    label: Optional[str] = None
    interval: Optional[str] = None
    size: Optional[int] = None
    order_by_metric: Optional[str] = None
    order_direction: str = "desc"

    def to_json(self) -> Dict[str, Any]:
        # Structure for a dimension in JSON
        json_data: Dict[str, Any] = {
            "label": self.label if self.label is not None else self.field, # Use label if provided, otherwise field
            "dataType": "string", # Placeholder, need to infer or add to model
            "isBucketed": True, # Dimensions are usually bucketed
            "operationType": self.type,
            "scale": "ordinal", # Placeholder, need to infer or add to model
            "sourceField": self.field,
            "params": {}
        }
        if self.type == "date_histogram":
            json_data["dataType"] = "date"
            json_data["scale"] = "interval"
            json_data["params"]["interval"] = self.interval if self.interval is not None else "auto"
            json_data["params"]["dropPartials"] = False # Default from samples
            json_data["params"]["includeEmptyRows"] = False # Default from samples
        elif self.type == "terms":
            json_data["dataType"] = "string" # Assuming string for terms
            json_data["params"]["size"] = self.size
            if self.order_by_metric:
                 json_data["params"]["orderBy"] = {"type": "column", "columnId": "placeholder"} # Need to map order_by_metric to columnId
                 json_data["params"]["orderDirection"] = self.order_direction
            json_data["params"]["otherBucket"] = True # Default from samples
            json_data["params"]["missingBucket"] = False # Default from samples
            json_data["params"]["parentFormat"] = {"id": "terms"} # Default from samples
            json_data["params"]["exclude"] = [] # Default from samples
            json_data["params"]["excludeIsRegex"] = False # Default from samples
            json_data["params"]["include"] = [] # Default from samples
            json_data["params"]["includeIsRegex"] = False # Default from samples


        # Remove empty params
        if not json_data["params"]:
            del json_data["params"]

        return json_data

class Metric(BaseModel):
    type: str
    label: Optional[str] = None
    field: Optional[str] = None
    formula: Optional[str] = None
    sort_field: Optional[str] = None
    filter: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        # Structure for a metric in JSON
        json_data: Dict[str, Any] = {
            "label": self.label if self.label is not None else self.type, # Use label if provided, otherwise type
            "dataType": "number", # Metrics are usually numbers
            "isBucketed": False, # Metrics are usually not bucketed
            "operationType": self.type,
            "scale": "ratio", # Placeholder, need to infer or add to model
            "sourceField": self.field if self.field is not None else "___records___", # Use field if provided, otherwise count source
            "params": {}
        }
        if self.type == "count":
             json_data["sourceField"] = "___records___"
        elif self.type == "last_value":
             if self.sort_field:
                 json_data["params"]["sortField"] = self.sort_field
             if self.filter:
                 json_data["filter"] = {"language": "kuery", "query": self.filter}
        elif self.type == "formula":
             json_data["params"]["formula"] = self.formula
             json_data["params"]["isFormulaBroken"] = False # Assuming valid formula for now
             json_data["references"] = [] # Need to handle formula references

        # Remove empty params
        if not json_data["params"]:
            del json_data["params"]

        return json_data

class Column(BaseModel):
    field: Optional[str] = None # Field is not required for count type
    type: str
    label: Optional[str] = None
    size: Optional[int] = None
    order_by_metric: Optional[str] = None
    order_direction: str = "desc"
    sort_field: Optional[str] = None # For last_value
    filter: Optional[str] = None # For last_value

    def to_json(self) -> Dict[str, Any]:
        # Structure for a column in JSON (used in tables)
        json_data: Dict[str, Any] = {
            "columnId": "placeholder", # Need to generate column IDs
            "isTransposed": False, # Default from samples
            "alignment": "left", # Default alignment
        }

        if self.field:
             json_data["sourceField"] = self.field # This might be redundant depending on how columns are linked to dimensions/metrics

        # Columns can represent dimensions or metrics, need to map properties accordingly
        # This is a simplified mapping, may need refinement based on specific Lens JSON structures
        if self.type in ["terms"]: # Dimension-like properties
            json_data["operationType"] = self.type
            json_data["label"] = self.label if self.label is not None else self.field
            json_data["isBucketed"] = True
            json_data["scale"] = "ordinal"
            json_data["params"] = {}
            if self.size:
                json_data["params"]["size"] = self.size
            if self.order_by_metric:
                 json_data["params"]["orderBy"] = {"type": "column", "columnId": "placeholder"} # Need to map order_by_metric to columnId
                 json_data["params"]["orderDirection"] = self.order_direction
            json_data["params"]["otherBucket"] = True # Default from samples
            json_data["params"]["missingBucket"] = False # Default from samples
            json_data["params"]["parentFormat"] = {"id": "terms"} # Default from samples
            json_data["params"]["exclude"] = [] # Default from samples
            json_data["params"]["excludeIsRegex"] = False # Default from samples
            json_data["params"]["include"] = [] # Default from samples
            json_data["params"]["includeIsRegex"] = False # Default from samples

        elif self.type in ["count", "max", "average", "unique_count", "last_value", "formula"]: # Metric-like properties
            json_data["isMetric"] = True
            json_data["operationType"] = self.type
            json_data["label"] = self.label if self.label is not None else self.type
            json_data["isBucketed"] = False
            json_data["scale"] = "ratio"
            json_data["sourceField"] = self.field if self.field is not None else "___records___"
            json_data["params"] = {}
            if self.type == "last_value":
                 if self.sort_field:
                     json_data["params"]["sortField"] = self.sort_field
                 if self.filter:
                     json_data["filter"] = {"language": "kuery", "query": self.filter}
            elif self.type == "formula":
                 json_data["params"]["formula"] = self.formula
                 json_data["params"]["isFormulaBroken"] = False # Assuming valid formula for now
                 json_data["references"] = [] # Need to handle formula references


        # Remove empty params
        if "params" in json_data and not json_data["params"]:
            del json_data["params"]

        return json_data

class LensPanel(Panel):
    visualization: str
    index_pattern: str
    query: str = ""
    filters: List[Filter] = Field(default_factory=list)
    dimensions: List[Dimension] = Field(default_factory=list)
    metrics: List[Metric] = Field(default_factory=list)
    columns: List[Column] = Field(default_factory=list)
    palette: Optional[Dict[str, Any]] = None # Simplified for now, can create a Palette model later

    def to_json(self) -> Dict[str, Any]:
        # Structure for a Lens panel in JSON
        json_data: Dict[str, Any] = {
            "type": "lens",
            "panelIndex": "placeholder", # Need to handle index generation
            "gridData": self.grid.model_dump(exclude_none=True),
            "embeddableConfig": {
                "attributes": {
                    "title": self.title,
                    "visualizationType": f"lns{self.visualization.capitalize()}", # Map YAML viz to lnsVizType
                    "type": "lens",
                    "references": [], # Need to handle references
                    "state": {
                        "visualization": {},
                        "query": {"language": "kuery", "query": self.query},
                        "filters": [f.to_json() for f in self.filters],
                        "datasourceStates": {"formBased": {"layers": {"placeholder": {}}}}, # Placeholder layer structure
                        "internalReferences": [], # Need to handle internal references
                        "adHocDataViews": {} # Default
                    }
                },
                "enhancements": {} # Default
            },
            "version": "8.7.1" # Placeholder version
        }

        # Populate visualization state based on type
        if self.visualization in ["line", "bar_stacked", "area"]:
            json_data["embeddableConfig"]["attributes"]["state"]["visualization"] = {
                "layers": [{
                    "layerId": "placeholder", # Need to generate layer ID
                    "layerType": "data", # Assuming data layer
                    "accessors": ["placeholder"], # Need to map metrics to accessors
                    "xAccessor": "placeholder", # Need to map x dimension to accessor
                    "seriesType": self.visualization, # Use YAML visualization type
                    "position": "top", # Default position
                    "showGridlines": False, # Default from samples
                    "palette": {"name": "default", "type": "palette"}, # Default palette
                    "yConfig": [], # Need to populate yConfig
                    "splitAccessor": "placeholder" if len(self.dimensions) > 1 else None # Handle split dimension
                }],
                "legend": {"isVisible": True, "position": "right"}, # Default legend
                "preferredSeriesType": "bar_stacked", # Default preferred type
                "valueLabels": "hide", # Default
                "fittingFunction": "Linear", # Default
                "axisTitlesVisibilitySettings": {"x": True, "yLeft": True, "yRight": True}, # Default
                "tickLabelsVisibilitySettings": {"x": True, "yLeft": True, "yRight": True}, # Default
                "labelsOrientation": {"x": 0, "yLeft": 0, "yRight": -90 if self.visualization == "line" else 0}, # Adjust y-axis label orientation for line charts
                "gridlinesVisibilitySettings": {"x": False if self.visualization == "line" else True, "yLeft": False if self.visualization == "line" else True, "yRight": True}, # Adjust gridlines for line charts
                "showCurrentTimeMarker": False, # Default
                "yLeftExtent": {"enforce": True, "mode": "dataBounds"}, # Default
                "yLeftScale": "linear", # Default
                "yRightScale": "linear", # Default
                "yTitle": "Count" # Placeholder, need to derive from metrics
            }
            # Populate dimensions and metrics in datasourceStates
            json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"] = { # Use placeholder layer ID
                "columns": {}, # Need to populate columns
                "columnOrder": [], # Need to populate column order
                "incompleteColumns": {}, # Default
                "sampling": 1 # Default
            }
            # Populate columns in datasourceStates from dimensions and metrics
            column_id_map = {}
            for dim in self.dimensions:
                col_id = f"dim_{len(column_id_map)}" # Simple ID generation
                json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][col_id] = dim.to_json()
                json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columnOrder"].append(col_id)
                column_id_map[dim.label if dim.label is not None else dim.field] = col_id # Map label/field to ID

            for metric in self.metrics:
                 col_id = f"metric_{len(column_id_map)}" # Simple ID generation
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][col_id] = metric.to_json()
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columnOrder"].append(col_id)
                 column_id_map[metric.label if metric.label is not None else metric.type] = col_id # Map label/type to ID

            # Update accessors and xAccessor
            if self.dimensions:
                json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["layers"][0]["xAccessor"] = column_id_map.get(self.dimensions[0].label if self.dimensions[0].label is not None else self.dimensions[0].field)
            if self.metrics:
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["layers"][0]["accessors"] = [column_id_map.get(metric.label if metric.label is not None else metric.type) for metric in self.metrics]
                 # Populate yConfig
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["layers"][0]["yConfig"] = [{"axisMode": "left", "forAccessor": column_id_map.get(metric.label if metric.label is not None else metric.type)} for metric in self.metrics]
                 # Set yTitle
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["yTitle"] = ", ".join([metric.label if metric.label is not None else metric.type for metric in self.metrics])

            # Handle split dimension
            if len(self.dimensions) > 1:
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["layers"][0]["splitAccessor"] = column_id_map.get(self.dimensions[1].label if self.dimensions[1].label is not None else self.dimensions[1].field)
                 # Update order_by_metric in dimension JSON
                 for dim in self.dimensions:
                     if dim.order_by_metric and dim.order_by_metric in column_id_map:
                         dim_json = json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][column_id_map.get(dim.label if dim.label is not None else dim.field)]
                         dim_json["params"]["orderBy"]["columnId"] = column_id_map[dim.order_by_metric]


        elif self.visualization == "table":
            json_data["embeddableConfig"]["attributes"]["state"]["visualization"] = {
                "columns": [], # Will populate below
                "layerId": "placeholder", # Need to generate layer ID
                "layerType": "data", # Assuming data layer
                "paging": {"enabled": True, "size": 10}, # Default paging
                "rowHeight": "single" # Default row height
            }
            # Populate columns in datasourceStates
            json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"] = { # Use placeholder layer ID
                "columns": {}, # Need to populate columns
                "columnOrder": [], # Need to populate column order
                "incompleteColumns": {}, # Default
                "sampling": 1 # Default
            }
            # Populate columns in datasourceStates from columns
            column_id_map = {}
            for col in self.columns:
                 col_id = f"col_{len(column_id_map)}" # Simple ID generation
                 col_json = col.to_json()
                 col_json["columnId"] = col_id # Set the generated column ID
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][col_id] = col_json
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columnOrder"].append(col_id)
                 column_id_map[col.label if col.label is not None else col.field if col.field is not None else col.type] = col_id # Map label/field/type to ID

            # Update columnIds in visualization columns and order_by_metric in column JSON
            json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["columns"] = [{"columnId": column_id_map.get(col.label if col.label is not None else col.field if col.field is not None else col.type), "isTransposed": False, "alignment": "left"} for col in self.columns] # Assuming default alignment and not transposed
            for col in self.columns:
                 if col.order_by_metric and col.order_by_metric in column_id_map:
                     col_json = json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][column_id_map.get(col.label if col.label is not None else col.field if col.field is not None else col.type)]
                     if "params" not in col_json:
                         col_json["params"] = {}
                     col_json["params"]["orderBy"] = {"type": "column", "columnId": column_id_map[col.order_by_metric]}


        elif self.visualization == "pie":
            json_data["embeddableConfig"]["attributes"]["state"]["visualization"] = {
                "shape": "pie", # Pie shape
                "layers": [{
                    "layerId": "placeholder", # Need to generate layer ID
                    "layerType": "data", # Assuming data layer
                    "primaryGroups": ["placeholder"], # Need to map dimension to primaryGroup
                    "metrics": ["placeholder"], # Need to map metric to metric
                    "categoryDisplay": "default", # Default
                    "emptySizeRatio": 0.3, # Default
                    "legendDisplay": "show", # Default
                    "legendMaxLines": 1, # Default
                    "legendPosition": "right", # Default
                    "legendSize": "auto", # Default
                    "nestedLegend": False, # Default
                    "numberDisplay": "percent", # Default
                    "percentDecimals": 2, # Default
                    "showValuesInLegend": True, # Default
                    "truncateLegend": True # Default
                }],
                "palette": {"name": "kibana_palette", "type": "palette"} # Default palette
            }
            # Populate dimensions and metrics in datasourceStates
            json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"] = { # Use placeholder layer ID
                "columns": {}, # Need to populate columns
                "columnOrder": [], # Need to populate column order
                "incompleteColumns": {}, # Default
                "sampling": 1 # Default
            }
            # Populate columns in datasourceStates from dimensions and metrics
            column_id_map = {}
            if self.dimensions:
                 dim = self.dimensions[0] # Assuming only one dimension for pie chart
                 col_id = f"dim_{len(column_id_map)}" # Simple ID generation
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][col_id] = dim.to_json()
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columnOrder"].append(col_id)
                 column_id_map[dim.label if dim.label is not None else dim.field] = col_id # Map label/field to ID
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["layers"][0]["primaryGroups"] = [col_id] # Map dimension to primaryGroup

            if self.metrics:
                 metric = self.metrics[0] # Assuming only one metric for pie chart
                 col_id = f"metric_{len(column_id_map)}" # Simple ID generation
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][col_id] = metric.to_json()
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columnOrder"].append(col_id)
                 column_id_map[metric.label if metric.label is not None else metric.type] = col_id # Map label/type to ID
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["layers"][0]["metrics"] = [col_id] # Map metric to metrics

            # Update order_by_metric in dimension JSON
            if self.dimensions and self.dimensions[0].order_by_metric and self.dimensions[0].order_by_metric in column_id_map:
                 dim_json = json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][column_id_map.get(self.dimensions[0].label if self.dimensions[0].label is not None else self.dimensions[0].field)]
                 if "params" not in dim_json:
                     dim_json["params"] = {}
                 dim_json["params"]["orderBy"]["columnId"] = column_id_map[self.dimensions[0].order_by_metric]


        elif self.visualization == "metric":
            json_data["embeddableConfig"]["attributes"]["state"]["visualization"] = {
                "layerId": "placeholder", # Need to generate layer ID
                "layerType": "data", # Assuming data layer
                "metricAccessor": "placeholder", # Need to map metric to accessor
                "showBar": False # Default
            }
            # Populate metrics in datasourceStates
            json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"] = { # Use placeholder layer ID
                "columns": {}, # Need to populate columns
                "columnOrder": [], # Need to populate column order
                "incompleteColumns": {}, # Default
                "sampling": 1 # Default
            }
            # Populate columns in datasourceStates from metrics
            column_id_map = {}
            if self.metrics:
                 metric = self.metrics[0] # Assuming only one metric for metric visualization
                 col_id = f"metric_{len(column_id_map)}" # Simple ID generation
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columns"][col_id] = metric.to_json()
                 json_data["embeddableConfig"]["attributes"]["state"]["datasourceStates"]["formBased"]["layers"]["placeholder"]["columnOrder"].append(col_id)
                 column_id_map[metric.label if metric.label is not None else metric.type] = col_id # Map label/type to ID
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["metricAccessor"] = col_id # Map metric to accessor

            # Handle palette for metric visualization
            if self.palette:
                 json_data["embeddableConfig"]["attributes"]["state"]["visualization"]["palette"] = self.palette # Assuming palette structure is already correct


        # Remove empty lists/dicts from state
        if "state" in json_data["embeddableConfig"]["attributes"]:
            state = json_data["embeddableConfig"]["attributes"]["state"]
            if "filters" in state and not state["filters"]:
                del state["filters"]
            if "dimensions" in state and not state["dimensions"]:
                del state["dimensions"]
            if "metrics" in state and not state["metrics"]:
                del state["metrics"]
            if "columns" in state and not state["columns"]:
                del state["columns"]
            if "datasourceStates" in state and not state["datasourceStates"]["formBased"]["layers"]:
                 del state["datasourceStates"]


        return json_data

class Dashboard(BaseModel):
    title: str
    description: str = ""
    panels: List[Union[SearchPanel, MarkdownPanel, MapPanel, LensPanel]] = Field(default_factory=list)

    def to_json(self) -> str:
        # Basic dashboard structure in JSON
        dashboard_json: Dict[str, Any] = {
            "attributes": {
                "title": self.title,
                "description": self.description,
                "panelsJSON": json.dumps([panel.to_json() for panel in self.panels]),
                "optionsJSON": "{}", # Placeholder options
                "version": 1 # Placeholder version
            },
            "coreMigrationVersion": "8.8.0", # Placeholder version
            "created_at": "2025-01-01T00:00:00.000Z", # Placeholder date
            "id": self.title.lower().replace(" ", "-"), # Simple ID generation
            "migrationVersion": {
                "dashboard": "8.7.0" # Placeholder version
            },
            "references": [], # Need to handle references
            "type": "dashboard",
            "typeMigrationVersion": "10.2.0" # Placeholder version
        }
        return json.dumps(dashboard_json, indent=2)


class Dashboard(BaseModel):
    title: str
    description: str = ""
    panels: List[Union[SearchPanel, MarkdownPanel, MapPanel, LensPanel]] = Field(default_factory=list)

    def to_json(self) -> str:
        # Basic dashboard structure in JSON
        dashboard_json: Dict[str, Any] = {
            "attributes": {
                "title": self.title,
                "description": self.description,
                "panelsJSON": json.dumps([panel.to_json() for panel in self.panels]),
                "optionsJSON": "{}", # Placeholder options
                "version": 1 # Placeholder version
            },
            "coreMigrationVersion": "8.8.0", # Placeholder version
            "created_at": "2025-01-01T00:00:00.000Z", # Placeholder date
            "id": self.title.lower().replace(" ", "-"), # Simple ID generation
            "migrationVersion": {
                "dashboard": "8.7.0" # Placeholder version
            },
            "references": [], # Need to handle references
            "type": "dashboard",
            "typeMigrationVersion": "10.2.0" # Placeholder version
        }
        return json.dumps(dashboard_json, indent=2)