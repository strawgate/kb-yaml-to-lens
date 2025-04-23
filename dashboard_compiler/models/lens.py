import uuid
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import json
# No relative imports needed yet, as these models don't depend on others in this package initially

class Filter(BaseModel):
    field: str
    type: str
    value: Any
    negate: bool = False

    def to_dict(self) -> Dict[str, Any]:
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

    def to_dict(self) -> Dict[str, Any]:
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
            json_data["params"]["dropPartials"] = False
            json_data["params"]["includeEmptyRows"] = False
        elif self.type == "terms":
            json_data["dataType"] = "string" # Assuming string for terms
            json_data["params"]["size"] = self.size
            if self.order_by_metric:
                 json_data["params"]["orderBy"] = {"type": "column", "columnId": "placeholder"} # Need to map order_by_metric to columnId
                 json_data["params"]["orderDirection"] = self.order_direction
            json_data["params"]["otherBucket"] = True
            json_data["params"]["missingBucket"] = False
            json_data["params"]["parentFormat"] = {"id": "terms"}
            json_data["params"]["exclude"] = []
            json_data["params"]["excludeIsRegex"] = False
            json_data["params"]["include"] = []
            json_data["params"]["includeIsRegex"] = False


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

    def to_dict(self) -> Dict[str, Any]:
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

    def to_dict(self) -> Dict[str, Any]:
        # Structure for a column in JSON (used in tables)
        json_data: Dict[str, Any] = {
            "columnId": uuid.uuid4(), # Need to generate column IDs
            "isTransposed": False,
            "alignment": "left",
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
            json_data["params"]["otherBucket"] = True
            json_data["params"]["missingBucket"] = False
            json_data["params"]["parentFormat"] = {"id": "terms"}
            json_data["params"]["exclude"] = []
            json_data["params"]["excludeIsRegex"] = False
            json_data["params"]["include"] = []
            json_data["params"]["includeIsRegex"] = False

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

class Reference(BaseModel):
    type: str
    id: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

class LayerDataSourceState(BaseModel):
    columns: Dict[str, Column] = Field(default_factory=dict)
    columnOrder: List[str] = Field(default_factory=list)
    incompleteColumns: Dict[str, Any] = Field(default_factory=dict) # Based on samples, seems to be empty
    sampling: int = 1

    def add_column(self, column: Column) -> None:
        """
        Adds a column to the layer's columns.
        
        Args:
            column: An instance of Column to add.
        """
        col_id = uuid.uuid4()  # Generate a unique column ID
        self.columns[col_id] = column
        self.columnOrder.append(col_id)

    def to_dict(self) -> Dict[str, Any]:
        # Convert Column models to their JSON representation
        columns_json: Dict[str, Dict[str, Any]] = {}
        for col_id, col in self.columns.items():
            result = col.to_dict()
            columns_json[col_id] = result
        #columns_json = {col_id: col.to_dict() for col_id, col in self.columns.items()}
        return {
            "columns": columns_json,
            "columnOrder": self.columnOrder,
            "incompleteColumns": self.incompleteColumns,
            "sampling": self.sampling
        }

class DataSourceState(BaseModel):
    formBased: Dict[str, Dict[str, LayerDataSourceState]] = Field(default_factory=dict) # Structure: formBased -> layers -> {layerId: LayerDataSourceState}
    indexpattern: Dict[str, Any] = Field(default_factory=dict) # Based on samples, seems to be empty
    textBased: Dict[str, Any] = Field(default_factory=dict) # Based on samples, seems to be empty

    def to_dict(self) -> Dict[str, Any]:
        # Convert nested LayerDataSourceState models to their JSON representation
        form_based_json = {}
        for key, layers in self.formBased.items():
            form_based_json[key] = {layer_id: layer_state.to_dict() for layer_id, layer_state in layers.items()}

        return {
            "formBased": form_based_json,
            "indexpattern": self.indexpattern,
            "textBased": self.textBased
        }

# Base class for Lens visualization state
class LensVisualizationState(BaseModel):
    # This will be overridden by subclasses
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

# Subclass for XY visualizations (line, bar, area)
class XYVisualizationState(LensVisualizationState):
    legend: Dict[str, Any] = Field(default_factory=lambda: {"isVisible": True, "position": "right"})
    valueLabels: str = "hide"
    fittingFunction: str = "Linear"
    axisTitlesVisibilitySettings: Dict[str, bool] = Field(default_factory=lambda: {"x": True, "yLeft": True, "yRight": True})
    tickLabelsVisibilitySettings: Dict[str, bool] = Field(default_factory=lambda: {"x": True, "yLeft": True, "yRight": True})
    labelsOrientation: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "yLeft": 0, "yRight": 0}) # yRight needs adjustment for line
    gridlinesVisibilitySettings: Dict[str, bool] = Field(default_factory=lambda: {"x": True, "yLeft": True, "yRight": True}) # Needs adjustment for line
    preferredSeriesType: str = "bar_stacked"
    layers: List[Dict[str, Any]] = Field(default_factory=list) # List of visualization layer configs
    showCurrentTimeMarker: bool = False
    yLeftExtent: Dict[str, Any] = Field(default_factory=lambda: {"enforce": True, "mode": "dataBounds"})
    yLeftScale: str = "linear"
    yRightScale: str = "linear"
    yTitle: str = "Count" # Placeholder, need to derive from metrics

    def to_dict(self) -> Dict[str, Any]:
        json_data = self.model_dump(exclude_none=True)
        # Adjustments based on visualization type (will need to be handled during instantiation)
        # For now, just return the basic structure
        return json_data

# Subclass for Pie visualizations
class PieVisualizationState(LensVisualizationState):
    shape: str = "pie"
    layers: List[Dict[str, Any]] = Field(default_factory=list) # List of visualization layer configs
    palette: Dict[str, Any] = Field(default_factory=lambda: {"name": "kibana_palette", "type": "palette"})
    categoryDisplay: str = "default"
    emptySizeRatio: float = 0.3
    legendDisplay: str = "show"
    legendMaxLines: int = 1
    legendPosition: str = "right"
    legendSize: str = "auto"
    nestedLegend: bool = False
    numberDisplay: str = "percent"
    percentDecimals: int = 2
    showValuesInLegend: bool = True
    truncateLegend: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

class LensState(BaseModel):
    # This model will hold the visualization-specific state later
    # visualization: LensVisualizationState # This will be populated by the validator
    query: Dict[str, str] = Field(default_factory=lambda: {"language": "kuery", "query": ""})
    filters: List[Filter] = Field(default_factory=list)
    datasourceStates: DataSourceState = Field(default_factory=DataSourceState)
    internalReferences: List[Any] = Field(default_factory=list) # Based on samples, seems to be empty
    adHocDataViews: Dict[str, Any] = Field(default_factory=dict) # Based on samples, seems to be empty

    # Need a validator here to set the correct visualization state subclass

    def to_dict(self) -> Dict[str, Any]:
        # Convert nested models to their JSON representation
        filters_json = [f.to_dict() for f in self.filters]
        datasource_states_json = self.datasourceStates.to_dict()
        # visualization_json = self.visualization.to_dict() # Call to_dict on the visualization state instance

        json_data: Dict[str, Any] = {
            # "visualization": visualization_json, # This will be populated by the validator
            "query": self.query,
            "filters": filters_json,
            "datasourceStates": datasource_states_json,
            "internalReferences": self.internalReferences,
            "adHocDataViews": self.adHocDataViews
        }

        # Remove empty lists/dicts
        if not json_data["filters"]:
            del json_data["filters"]
        if not json_data["internalReferences"]:
            del json_data["internalReferences"]
        if not json_data["adHocDataViews"]:
            del json_data["adHocDataViews"]
        # Check if datasourceStates.formBased.layers is empty
        if not self.datasourceStates.formBased.get("layers"):
             del json_data["datasourceStates"]

        return json_data

# Placeholder for LensPanel - will be moved here later
class LensPanel(BaseModel):
    # This will be populated in a later step
    pass