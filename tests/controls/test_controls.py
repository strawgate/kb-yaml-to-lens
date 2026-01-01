"""Test the compilation of controls from config models to view models."""

import json
from typing import TYPE_CHECKING, Any

from dirty_equals import IsUUID
from inline_snapshot import snapshot
from pydantic import BaseModel

from dashboard_compiler.controls.compile import compile_control, compile_control_group
from dashboard_compiler.controls.config import ControlSettings, ControlTypes

if TYPE_CHECKING:
    from dashboard_compiler.controls.view import KbnControlGroupInput, KbnControlTypes


class ControlHolder(BaseModel):
    """A holder for control configurations to be used in tests."""

    # Use the correct type from the existing config file
    control: ControlTypes


def compile_control_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile control config and return dict for snapshot testing."""
    control_holder: ControlHolder = ControlHolder.model_validate({'control': config})
    kbn_control_group_input: KbnControlTypes = compile_control(order=0, control=control_holder.control)
    return kbn_control_group_input.model_dump(by_alias=True)


def compile_control_settings_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile control settings config and return dict for snapshot testing."""
    control_settings = ControlSettings.model_validate(obj=config)
    kbn_control_group_input: KbnControlGroupInput = compile_control_group(control_settings=control_settings, controls=[])
    result = kbn_control_group_input.model_dump(by_alias=True)

    if 'ignoreParentSettingsJSON' in result and isinstance(result['ignoreParentSettingsJSON'], str):
        result['ignoreParentSettingsJSON'] = json.loads(result['ignoreParentSettingsJSON'])

    if 'panelsJSON' in result and isinstance(result['panelsJSON'], str):
        result['panelsJSON'] = json.loads(result['panelsJSON'])

    return result


async def test_normal_options_list() -> None:
    """Test normal options list control."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_custom_label() -> None:
    """Test options list control with custom label."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Custom Label',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Custom Label',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_large_width() -> None:
    """Test options list control with large width."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'label': 'Large Option',
        'field': 'aerospike.namespace',
        'width': 'large',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'large',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Large Option',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_large_width_and_expand() -> None:
    """Test options list control with large width and expand option."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Large Option with Expand',
        'width': 'large',
        'fill_width': True,
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': True,
            'order': 0,
            'width': 'large',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Large Option with Expand',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_small_width_and_single_select() -> None:
    """Test options list control with small width and single select."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Small Option Single Select',
        'match_technique': 'prefix',
        'singular': True,
        'width': 'small',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'small',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Small Option Single Select',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'singleSelect': True,
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_contains_search_technique() -> None:
    """Test options list control with contains search technique."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Contains',
        'match_technique': 'contains',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Contains',
                'searchTechnique': 'wildcard',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_exact_search_technique() -> None:
    """Test options list control with exact search technique."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'match_technique': 'exact',
        'label': 'Exact',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Exact',
                'searchTechnique': 'exact',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_ignore_timeout() -> None:
    """Test options list control with ignore timeout."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'wait_for_results': True,
        'label': 'ignore-timeout',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'optionsListControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'ignore-timeout',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
                'runPastTimeout': True,
            },
        }
    )


async def test_range_slider_with_default_step_size() -> None:
    """Test range slider control with default step size."""
    config = {
        'type': 'range',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'label': 'Default Range',
        'field': 'aerospike.namespace.geojson.region_query_cells',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'rangeSliderControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace.geojson.region_query_cells',
                'title': 'Default Range',
                'step': 1,
            },
        }
    )


async def test_range_slider_with_step_size_10() -> None:
    """Test range slider control with step size 10."""
    config = {
        'type': 'range',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace.geojson.region_query_cells',
        'step': 10,
        'label': 'Range step 10',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'rangeSliderControl',
            'explicitInput': {
                'id': IsUUID,
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace.geojson.region_query_cells',
                'title': 'Range step 10',
                'step': 10,
            },
        }
    )


async def test_time_slider_with_default_settings() -> None:
    """Test time slider control with default settings."""
    config = {
        'type': 'time',
        'start_offset': 0.5825778,
        'end_offset': 0.995556,
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': True,
            'order': 0,
            'width': 'medium',
            'type': 'timeSlider',
            'explicitInput': {
                'id': IsUUID,
                'timesliceStartAsPercentageOfTimeRange': 0.5825778,
                'timesliceEndAsPercentageOfTimeRange': 0.995556,
            },
        }
    )


async def test_default_control_settings() -> None:
    """Test default control settings."""
    config = {}
    result = compile_control_settings_snapshot(config)
    assert result == snapshot(
        {
            'chainingSystem': 'HIERARCHICAL',
            'controlStyle': 'oneLine',
            'ignoreParentSettingsJSON': {
                'ignoreFilters': False,
                'ignoreQuery': False,
                'ignoreTimerange': False,
                'ignoreValidations': False,
            },
            'panelsJSON': {},
            'showApplySelections': False,
        }
    )


async def test_custom_control_settings() -> None:
    """Test custom control settings."""
    config = {
        'label_position': 'above',
        'apply_global_filters': False,
        'apply_global_timerange': False,
        'ignore_zero_results': True,
        'chain_controls': False,
        'click_to_apply': True,
    }
    result = compile_control_settings_snapshot(config)
    assert result == snapshot(
        {
            'chainingSystem': 'NONE',
            'controlStyle': 'twoLine',
            'ignoreParentSettingsJSON': {'ignoreFilters': True, 'ignoreQuery': True, 'ignoreTimerange': True, 'ignoreValidations': True},
            'panelsJSON': {},
            'showApplySelections': True,
        }
    )


async def test_esql_static_values_control() -> None:
    """Test ES|QL control with static values."""
    config = {
        'type': 'esql_static',
        'variable_name': 'environment',
        'variable_type': 'values',
        'available_options': ['production', 'staging', 'development'],
        'title': 'Environment',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'esqlControl',
            'explicitInput': {
                'id': IsUUID,
                'variableName': 'environment',
                'variableType': 'values',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'Environment',
                'selectedOptions': [],
                'availableOptions': ['production', 'staging', 'development'],
            },
        }
    )


async def test_esql_static_values_control_with_single_select() -> None:
    """Test ES|QL control with static values and single select."""
    config = {
        'type': 'esql_static',
        'variable_name': 'status',
        'variable_type': 'values',
        'available_options': ['200', '404', '500'],
        'title': 'HTTP Status',
        'single_select': True,
        'width': 'small',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'small',
            'type': 'esqlControl',
            'explicitInput': {
                'id': IsUUID,
                'variableName': 'status',
                'variableType': 'values',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'HTTP Status',
                'selectedOptions': [],
                'singleSelect': True,
                'availableOptions': ['200', '404', '500'],
            },
        }
    )


async def test_esql_query_control() -> None:
    """Test ES|QL control with query-driven values."""
    config = {
        'type': 'esql_query',
        'variable_name': 'status_code',
        'variable_type': 'values',
        'esql_query': 'FROM logs-* | STATS count BY http.response.status_code | KEEP http.response.status_code',
        'title': 'Status Code',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'medium',
            'type': 'esqlControl',
            'explicitInput': {
                'id': IsUUID,
                'variableName': 'status_code',
                'variableType': 'values',
                'esqlQuery': 'FROM logs-* | STATS count BY http.response.status_code | KEEP http.response.status_code',
                'controlType': 'VALUES_FROM_QUERY',
                'title': 'Status Code',
                'selectedOptions': [],
            },
        }
    )


async def test_esql_query_control_with_single_select() -> None:
    """Test ES|QL control with query-driven values and single select."""
    config = {
        'type': 'esql_query',
        'variable_name': 'host_name',
        'variable_type': 'values',
        'esql_query': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
        'title': 'Host Name',
        'single_select': True,
        'width': 'large',
    }
    result = compile_control_snapshot(config)
    assert result == snapshot(
        {
            'grow': False,
            'order': 0,
            'width': 'large',
            'type': 'esqlControl',
            'explicitInput': {
                'id': IsUUID,
                'variableName': 'host_name',
                'variableType': 'values',
                'esqlQuery': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
                'controlType': 'VALUES_FROM_QUERY',
                'title': 'Host Name',
                'selectedOptions': [],
                'singleSelect': True,
            },
        }
    )
