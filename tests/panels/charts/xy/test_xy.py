"""Test the compilation of Lens metrics from config models to view models."""

import re
from typing import Any

from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.xy.compile import compile_esql_xy_chart, compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import ESQLXYChartTypes, LensXYChartTypes


def _replace_layer_id(result: dict[str, Any]) -> dict[str, Any]:
    """Replace dynamic layerId with placeholder for consistent snapshots."""
    if 'layerId' in result and re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', result['layerId']):
        result['layerId'] = 'DYNAMIC_LAYER_ID'
    return result


async def test_bar_stacked_chart() -> None:
    """Test bar stacked chart."""
    lens_config = {
        'type': 'bar',
        'mode': 'stacked',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'bar',
        'mode': 'stacked',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensXYChartTypes(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()

    esql_chart = ESQLXYChartTypes(**esql_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()


async def test_bar_unstacked_chart() -> None:
    """Test bar unstacked chart."""
    lens_config = {
        'type': 'bar',
        'mode': 'unstacked',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'bar',
        'mode': 'unstacked',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensXYChartTypes(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()

    esql_chart = ESQLXYChartTypes(**esql_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()


async def test_line_chart() -> None:
    """Test line chart."""
    lens_config = {
        'type': 'line',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'line',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensXYChartTypes(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()

    esql_chart = ESQLXYChartTypes(**esql_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()


async def test_area_chart() -> None:
    """Test area chart."""
    lens_config = {
        'type': 'area',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'area',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensXYChartTypes(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()

    esql_chart = ESQLXYChartTypes(**esql_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()


async def test_area_percentage_chart() -> None:
    """Test area percentage chart."""
    lens_config = {
        'type': 'area',
        'mode': 'percentage',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'area',
        'mode': 'percentage',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensXYChartTypes(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()

    esql_chart = ESQLXYChartTypes(**esql_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()


async def test_scatter_chart() -> None:
    """Test scatter chart."""
    lens_config = {
        'type': 'scatter',
        'data_view': 'metrics-*',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'aggregation': 'count', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }
    esql_config = {
        'type': 'scatter',
        'dimensions': [{'field': '@timestamp', 'id': '451e4374-f869-4ee9-8569-3092cd16ac18'}],
        'metrics': [{'field': 'count(*)', 'id': 'f1c1076b-5312-4458-aa74-535c908194fe'}],
        'breakdown': {'field': 'aerospike.namespace.name', 'id': 'e47fb84a-149f-42d3-b68e-d0c29c27d1f9'},
    }

    lens_chart = LensXYChartTypes(**lens_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_lens_xy_chart(lens_xy_chart=lens_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()

    esql_chart = ESQLXYChartTypes(**esql_config)
    layer_id, kbn_columns, kbn_state_visualization = compile_esql_xy_chart(esql_xy_chart=esql_chart)
    assert kbn_state_visualization is not None
    layer = kbn_state_visualization.layers[0]
    result = _replace_layer_id(layer.model_dump())
    assert result == snapshot()
