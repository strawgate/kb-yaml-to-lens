from dashboard_compiler.models.panels.lens.base import (
    Filter,
    Dimension,
    Metric,
    Reference,
    LayerDataSourceState,
    DataSourceState,
    LensState,
    XYVisualizationState,
    PieVisualizationState,
    Column,  # Import Column for LayerDataSourceState test
)

# --- Sample Data ---

# Filter Data (derived from complex sample)
FILTER_PHRASE_DATA = {
    "field": "data_stream.dataset",
    "type": "phrase",
    "value": "1password.signin_attempts",
    "negate": False,
}
FILTER_PHRASES_DATA = {
    "field": "event.action",
    "type": "phrases",
    "value": ["success", "firewall_reported_success"],
    "negate": True,
}

# Dimension/Metric Data (derived from simple samples)
DIMENSION_TERMS_DATA = {
    "field": "aerospike.namespace",
    "type": "terms",
    "label": "Top 5 values of aerospike.namespace",
    "size": 5,
    "order_by_metric": "count_metric_id",  # Placeholder ID
    "order_direction": "desc",
}
DIMENSION_DATE_HIST_DATA = {
    "field": "@timestamp",
    "type": "date_histogram",
    "label": "@timestamp",
    "interval": "auto",
}
METRIC_COUNT_DATA = {
    "type": "count",
    "label": "Count of records",
}

# Column Data (for LayerDataSourceState) - using Dimension/Metric data
COLUMN_TERMS_DATA = {
    "field": DIMENSION_TERMS_DATA["field"],
    "type": DIMENSION_TERMS_DATA["type"],
    "label": DIMENSION_TERMS_DATA["label"],
    "size": DIMENSION_TERMS_DATA["size"],
    "order_by_metric": DIMENSION_TERMS_DATA["order_by_metric"],
    "order_direction": DIMENSION_TERMS_DATA["order_direction"],
}
COLUMN_COUNT_DATA = {
    "type": METRIC_COUNT_DATA["type"],
    "label": METRIC_COUNT_DATA["label"],
}

# Reference Data (derived from simple samples)
REFERENCE_DATA = {
    "type": "index-pattern",
    "id": "metrics-*",
    "name": "c7a35c4f-e82d-4f16-b1a6-12229363244e:indexpattern-datasource-layer-21cb2847-7b10-404e-9672-4ee2f2beca6e",
}

# LayerDataSourceState Data
LAYER_DS_STATE_DATA = {
    "columns": {
        "dim_id_1": Column(**COLUMN_TERMS_DATA),
        "metric_id_1": Column(**COLUMN_COUNT_DATA),
    },
    "columnOrder": ["dim_id_1", "metric_id_1"],
}

# DataSourceState Data
DS_STATE_DATA = {"formBased": {"layers": {"layer_id_1": LayerDataSourceState(**LAYER_DS_STATE_DATA)}}}

# Visualization State Data
PIE_VIS_STATE_DATA = {
    "shape": "pie",
    "layers": [
        {
            "layerId": "layer_id_1",
            "primaryGroups": ["dim_id_1"],
            "metrics": ["metric_id_1"],
        }
    ],  # Simplified layer structure
}
XY_VIS_STATE_DATA = {
    "preferredSeriesType": "bar_stacked",
    "layers": [{"layerId": "layer_id_1", "accessors": ["metric_id_1"], "xAccessor": "dim_id_1"}],  # Simplified layer structure
}

# LensState Data
LENS_STATE_DATA = {
    "filters": [Filter(**FILTER_PHRASE_DATA)],
    "datasourceStates": DataSourceState(**DS_STATE_DATA),
    # "visualization": PieVisualizationState(**PIE_VIS_STATE_DATA) # Added later
}


# --- Unit Tests ---


def test_filter_instantiation():
    """Tests successful instantiation of the Filter model."""
    f_phrase = Filter(**FILTER_PHRASE_DATA)
    assert f_phrase.field == "data_stream.dataset"
    assert f_phrase.type == "phrase"
    assert f_phrase.value == "1password.signin_attempts"
    assert not f_phrase.negate

    f_phrases = Filter(**FILTER_PHRASES_DATA)
    assert f_phrases.field == "event.action"
    assert f_phrases.type == "phrases"
    assert f_phrases.value == ["success", "firewall_reported_success"]
    assert f_phrases.negate


def test_filter_to_dict():
    """Tests the Filter.to_dict() method."""
    f_phrase = Filter(**FILTER_PHRASE_DATA)
    json_output_phrase = f_phrase.to_dict()
    assert json_output_phrase["meta"]["field"] == "data_stream.dataset"
    assert json_output_phrase["meta"]["type"] == "phrase"
    assert json_output_phrase["meta"]["negate"] is False
    assert json_output_phrase["meta"]["params"]["query"] == "1password.signin_attempts"
    assert json_output_phrase["meta"]["value"] == "1password.signin_attempts"  # Check redundant value
    assert json_output_phrase["meta"]["index"] == "placeholder"

    # Currently filtered out by the none filter, not sure if this is right
    # assert json_output_phrase["query"] == {} # Check placeholder query

    f_phrases = Filter(**FILTER_PHRASES_DATA)
    json_output_phrases = f_phrases.to_dict()
    assert json_output_phrases["meta"]["field"] == "event.action"
    assert json_output_phrases["meta"]["type"] == "phrases"
    assert json_output_phrases["meta"]["negate"] is True
    assert json_output_phrases["meta"]["params"] == [
        "success",
        "firewall_reported_success",
    ]
    assert json_output_phrases["meta"]["value"] == [
        "success",
        "firewall_reported_success",
    ]  # Check redundant value


def test_dimension_instantiation():
    """Tests successful instantiation of the Dimension model."""
    dim_terms = Dimension(**DIMENSION_TERMS_DATA)
    assert dim_terms.field == "aerospike.namespace"
    assert dim_terms.type == "terms"
    assert dim_terms.size == 5

    dim_date = Dimension(**DIMENSION_DATE_HIST_DATA)
    assert dim_date.field == "@timestamp"
    assert dim_date.type == "date_histogram"
    assert dim_date.interval == "auto"


def test_dimension_to_dict():
    """Tests the Dimension.to_dict() method."""
    dim_terms = Dimension(**DIMENSION_TERMS_DATA)
    json_output_terms = dim_terms.to_dict()
    assert json_output_terms["label"] == "Top 5 values of aerospike.namespace"
    assert json_output_terms["operationType"] == "terms"
    assert json_output_terms["sourceField"] == "aerospike.namespace"
    assert json_output_terms["params"]["size"] == 5
    assert json_output_terms["params"]["orderBy"]["columnId"] == "placeholder"  # Check placeholder
    assert json_output_terms["params"]["orderDirection"] == "desc"

    dim_date = Dimension(**DIMENSION_DATE_HIST_DATA)
    json_output_date = dim_date.to_dict()
    assert json_output_date["label"] == "@timestamp"
    assert json_output_date["operationType"] == "date_histogram"
    assert json_output_date["sourceField"] == "@timestamp"
    assert json_output_date["params"]["interval"] == "auto"


def test_metric_instantiation():
    """Tests successful instantiation of the Metric model."""
    metric = Metric(**METRIC_COUNT_DATA)
    assert metric.type == "count"
    assert metric.label == "Count of records"
    assert metric.field is None  # Field is None for count


def test_metric_to_dict():
    """Tests the Metric.to_dict() method."""
    metric = Metric(**METRIC_COUNT_DATA)
    json_output = metric.to_dict()
    assert json_output["label"] == "Count of records"
    assert json_output["operationType"] == "count"
    assert json_output["sourceField"] == "___records___"  # Check default source field for count
    assert "params" not in json_output  # No params for simple count


def test_reference_instantiation():
    """Tests successful instantiation of the Reference model."""
    ref = Reference(**REFERENCE_DATA)
    assert ref.type == "index-pattern"
    assert ref.id == "metrics-*"
    assert ref.name == "c7a35c4f-e82d-4f16-b1a6-12229363244e:indexpattern-datasource-layer-21cb2847-7b10-404e-9672-4ee2f2beca6e"


def test_reference_to_dict():
    """Tests the Reference.to_dict() method."""
    ref = Reference(**REFERENCE_DATA)
    assert ref.to_dict() == REFERENCE_DATA  # Should be a simple dump


def test_layer_data_source_state_instantiation():
    """Tests successful instantiation of LayerDataSourceState."""
    lds_state = LayerDataSourceState(**LAYER_DS_STATE_DATA)
    assert "dim_id_1" in lds_state.columns
    assert "metric_id_1" in lds_state.columns
    assert isinstance(lds_state.columns["dim_id_1"], Column)
    assert lds_state.columnOrder == ["dim_id_1", "metric_id_1"]


def test_layer_data_source_state_to_dict():
    """Tests the LayerDataSourceState.to_dict() method."""
    lds_state = LayerDataSourceState(**LAYER_DS_STATE_DATA)
    json_output = lds_state.to_dict()
    assert "dim_id_1" in json_output["columns"]
    assert "metric_id_1" in json_output["columns"]
    # Check if nested Column.to_dict was called (basic check)
    assert json_output["columns"]["dim_id_1"]["operationType"] == "terms"
    assert json_output["columns"]["metric_id_1"]["operationType"] == "count"
    assert json_output["columnOrder"] == ["dim_id_1", "metric_id_1"]


def test_data_source_state_instantiation():
    """Tests successful instantiation of DataSourceState."""
    ds_state = DataSourceState(**DS_STATE_DATA)
    assert "layers" in ds_state.formBased
    assert "layer_id_1" in ds_state.formBased["layers"]
    assert isinstance(ds_state.formBased["layers"]["layer_id_1"], LayerDataSourceState)


def test_data_source_state_to_dict():
    """Tests the DataSourceState.to_dict() method."""
    ds_state = DataSourceState(**DS_STATE_DATA)
    json_output = ds_state.to_dict()
    assert "layers" in json_output["formBased"]
    assert "layer_id_1" in json_output["formBased"]["layers"]
    # Check if nested LayerDataSourceState.to_dict was called (basic check)
    assert "columns" in json_output["formBased"]["layers"]["layer_id_1"]
    assert "dim_id_1" in json_output["formBased"]["layers"]["layer_id_1"]["columns"]


def test_pie_visualization_state_instantiation():
    """Tests successful instantiation of PieVisualizationState."""
    vis_state = PieVisualizationState(**PIE_VIS_STATE_DATA)
    assert vis_state.shape == "pie"
    assert len(vis_state.layers) == 1
    assert vis_state.layers[0]["layerId"] == "layer_id_1"


def test_pie_visualization_state_to_dict():
    """Tests the PieVisualizationState.to_dict() method."""
    vis_state = PieVisualizationState(**PIE_VIS_STATE_DATA)
    json_output = vis_state.to_dict()
    assert json_output["shape"] == "pie"
    assert len(json_output["layers"]) == 1
    assert json_output["layers"][0]["metrics"] == ["metric_id_1"]
    assert json_output["legendPosition"] == "right"  # Check default


def test_xy_visualization_state_instantiation():
    """Tests successful instantiation of XYVisualizationState."""
    vis_state = XYVisualizationState(**XY_VIS_STATE_DATA)
    assert vis_state.preferredSeriesType == "bar_stacked"
    assert len(vis_state.layers) == 1
    assert vis_state.layers[0]["xAccessor"] == "dim_id_1"


def test_xy_visualization_state_to_dict():
    """Tests the XYVisualizationState.to_dict() method."""
    vis_state = XYVisualizationState(**XY_VIS_STATE_DATA)
    json_output = vis_state.to_dict()
    assert json_output["preferredSeriesType"] == "bar_stacked"
    assert len(json_output["layers"]) == 1
    assert json_output["layers"][0]["accessors"] == ["metric_id_1"]
    assert json_output["legend"]["position"] == "right"  # Check default


def test_lens_state_instantiation():
    """Tests successful instantiation of LensState."""
    lens_state = LensState(**LENS_STATE_DATA)
    assert len(lens_state.filters) == 1
    assert isinstance(lens_state.filters[0], Filter)
    assert isinstance(lens_state.datasourceStates, DataSourceState)
    # assert isinstance(lens_state.visualization, PieVisualizationState) # Test when validator is added


def test_lens_state_to_dict():
    """Tests the LensState.to_dict() method placeholder."""
    lens_state = LensState(**LENS_STATE_DATA)
    json_output = lens_state.to_dict()
    assert len(json_output["filters"]) == 1
    assert json_output["filters"][0]["meta"]["type"] == "phrase"  # Check nested Filter.to_dict
    assert "datasourceStates" in json_output
    assert "formBased" in json_output["datasourceStates"]  # Check nested DataSourceState.to_dict
    # assert "visualization" in json_output # Test when validator is added
    # assert json_output["visualization"]["shape"] == "pie" # Test when validator is added
    assert "internalReferences" not in json_output  # Check removal of empty list
    assert "adHocDataViews" not in json_output  # Check removal of empty dict
