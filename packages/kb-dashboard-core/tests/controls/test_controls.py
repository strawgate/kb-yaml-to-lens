"""Test the compilation of controls from config models to view models."""

import json
from typing import Any

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot
from pydantic import BaseModel, ValidationError

from kb_dashboard_core.controls.compile import compile_control, compile_control_group
from kb_dashboard_core.controls.config import (
    ControlSettings,
    ControlTypes,
    ESQLStaticMultiSelectControl,
    ESQLStaticSingleSelectControl,
    TimeSliderControl,
)


class ControlHolder(BaseModel):
    """A holder for control configurations to be used in tests."""

    # Use the correct type from the existing config file
    control: ControlTypes


def compile_control_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile control config and return dict for snapshot testing."""
    control_holder: ControlHolder = ControlHolder.model_validate({'control': config})
    kbn_control, _ = compile_control(order=0, control=control_holder.control)
    return kbn_control.model_dump(by_alias=True)


def compile_control_settings_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile control settings config and return dict for snapshot testing."""
    control_settings = ControlSettings.model_validate(obj=config)
    kbn_control_group_input, _ = compile_control_group(control_settings=control_settings, controls=[])
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
        'multiple': False,
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


async def test_esql_multi_select_control() -> None:
    """Test ES|QL multi-select control with static values."""
    config = {
        'type': 'esql',
        'variable_name': 'environment',
        'variable_type': 'values',
        'choices': ['production', 'staging', 'development'],
        'label': 'Environment',
        'multiple': True,
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
                'singleSelect': False,
                'availableOptions': ['production', 'staging', 'development'],
            },
        }
    )


async def test_esql_single_select_control() -> None:
    """Test ES|QL single-select control with static values."""
    config = {
        'type': 'esql',
        'variable_name': 'status',
        'variable_type': 'values',
        'choices': ['200', '404', '500'],
        'label': 'HTTP Status',
        'width': 'small',
        'multiple': False,
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
        'type': 'esql',
        'variable_name': 'status_code',
        'variable_type': 'values',
        'query': 'FROM logs-* | STATS count BY http.response.status_code | KEEP http.response.status_code',
        'label': 'Status Code',
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
                'singleSelect': True,
            },
        }
    )


async def test_esql_query_control_with_single_select() -> None:
    """Test ES|QL control with query-driven values and single select."""
    config = {
        'type': 'esql',
        'variable_name': 'host_name',
        'variable_type': 'values',
        'query': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
        'label': 'Host Name',
        'multiple': False,
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


async def test_time_slider_control_validation_error() -> None:
    """Test TimeSliderControl raises validation error when start_offset is greater than end_offset."""
    with pytest.raises(ValidationError, match='start_offset must be less than end_offset'):
        _ = TimeSliderControl(
            type='time',
            start_offset=0.8,
            end_offset=0.2,
        )


async def test_options_list_with_multi_select() -> None:
    """Test options list control with multi-select (multiple: true)."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Multi Select Test',
        'multiple': True,
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
                'title': 'Multi Select Test',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'singleSelect': False,
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_without_wait_for_results() -> None:
    """Test options list control with wait_for_results: false."""
    config = {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'No Wait Test',
        'wait_for_results': False,
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
                'title': 'No Wait Test',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'runPastTimeout': False,
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_esql_single_select_control_with_default() -> None:
    """Test ES|QL single-select control with default value."""
    config = {
        'type': 'esql',
        'variable_name': 'project_id',
        'variable_type': 'values',
        'choices': ['e252fee1dd6f4ff08bc91532aa922182', 'aaca5cd9be82480fa821c3f8e64e3f41'],
        'label': 'Project ID',
        'default': 'e252fee1dd6f4ff08bc91532aa922182',
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
                'variableName': 'project_id',
                'variableType': 'values',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'Project ID',
                'selectedOptions': ['e252fee1dd6f4ff08bc91532aa922182'],
                'singleSelect': True,
                'availableOptions': ['e252fee1dd6f4ff08bc91532aa922182', 'aaca5cd9be82480fa821c3f8e64e3f41'],
            },
        }
    )


async def test_esql_multi_select_control_with_default() -> None:
    """Test ES|QL multi-select control with default values."""
    config = {
        'type': 'esql',
        'variable_name': 'status',
        'variable_type': 'values',
        'choices': ['200', '404', '500', '503'],
        'label': 'HTTP Status',
        'default': ['200', '404'],
        'multiple': True,
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
                'variableName': 'status',
                'variableType': 'values',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'HTTP Status',
                'selectedOptions': ['200', '404'],
                'singleSelect': False,
                'availableOptions': ['200', '404', '500', '503'],
            },
        }
    )


async def test_esql_single_select_control_default_validation() -> None:
    """Test that default value validation works for single-select controls."""
    with pytest.raises(ValidationError, match='default contains options not in choices'):
        ESQLStaticSingleSelectControl.model_validate(
            {
                'type': 'esql',
                'variable_name': 'project_id',
                'variable_type': 'values',
                'choices': ['option1', 'option2'],
                'label': 'Project',
                'default': 'option3',
            }
        )


async def test_esql_multi_select_control_default_validation() -> None:
    """Test that default value validation works for multi-select controls."""
    with pytest.raises(ValidationError, match='default contains options not in choices'):
        ESQLStaticMultiSelectControl.model_validate(
            {
                'type': 'esql',
                'variable_name': 'status',
                'variable_type': 'values',
                'choices': ['option1', 'option2'],
                'label': 'Status',
                'default': ['option1', 'option3'],
                'multiple': True,
            }
        )


async def test_esql_query_control_with_multi_select() -> None:
    """Test ES|QL query control with multi-select (single_select: false)."""
    config = {
        'type': 'esql',
        'variable_name': 'host',
        'variable_type': 'values',
        'query': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
        'label': 'Host Name',
        'multiple': True,
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
                'variableName': 'host',
                'variableType': 'values',
                'esqlQuery': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
                'controlType': 'VALUES_FROM_QUERY',
                'title': 'Host Name',
                'selectedOptions': [],
                'singleSelect': False,
            },
        }
    )


async def test_esql_field_control() -> None:
    """Test ES|QL field control (FIELDS variable type)."""
    config = {
        'type': 'esql',
        'variable_name': 'selected_field',
        'variable_type': 'fields',
        'choices': ['@timestamp', 'host.name', 'message'],
        'label': 'Select Field',
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
                'variableName': 'selected_field',
                'variableType': 'fields',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'Select Field',
                'selectedOptions': [],
                'singleSelect': True,
                'availableOptions': ['@timestamp', 'host.name', 'message'],
            },
        }
    )


async def test_esql_function_control() -> None:
    """Test ES|QL function control (FUNCTIONS variable type)."""
    config = {
        'type': 'esql',
        'variable_name': 'aggregate_fn',
        'variable_type': 'functions',
        'choices': ['COUNT', 'AVG', 'SUM'],
        'label': 'Aggregate Function',
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
                'variableName': 'aggregate_fn',
                'variableType': 'functions',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'Aggregate Function',
                'selectedOptions': [],
                'singleSelect': True,
                'availableOptions': ['COUNT', 'AVG', 'SUM'],
            },
        }
    )


async def test_esql_field_control_default_validation() -> None:
    """Test that default value validation works for field controls."""
    with pytest.raises(ValidationError, match='default contains options not in choices'):
        ControlHolder.model_validate(
            {
                'control': {
                    'type': 'esql',
                    'variable_name': 'selected_field',
                    'variable_type': 'fields',
                    'choices': ['@timestamp', 'host.name'],
                    'default': 'invalid_field',
                }
            }
        )


async def test_esql_field_control_with_default() -> None:
    """Test ES|QL field control with default value."""
    config = {
        'type': 'esql',
        'variable_name': 'selected_field',
        'variable_type': 'fields',
        'choices': ['@timestamp', 'host.name', 'message'],
        'label': 'Select Field',
        'default': '@timestamp',
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
                'variableName': 'selected_field',
                'variableType': 'fields',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'Select Field',
                'selectedOptions': ['@timestamp'],
                'singleSelect': True,
                'availableOptions': ['@timestamp', 'host.name', 'message'],
            },
        }
    )


async def test_esql_function_control_default_validation() -> None:
    """Test that default value validation works for function controls."""
    with pytest.raises(ValidationError, match='default contains options not in choices'):
        ControlHolder.model_validate(
            {
                'control': {
                    'type': 'esql',
                    'variable_name': 'aggregate_fn',
                    'variable_type': 'functions',
                    'choices': ['COUNT', 'AVG', 'SUM'],
                    'default': 'INVALID_FN',
                }
            }
        )


async def test_esql_function_control_with_default() -> None:
    """Test ES|QL function control with default value."""
    config = {
        'type': 'esql',
        'variable_name': 'aggregate_fn',
        'variable_type': 'functions',
        'choices': ['COUNT', 'AVG', 'SUM'],
        'label': 'Aggregate Function',
        'default': 'COUNT',
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
                'variableName': 'aggregate_fn',
                'variableType': 'functions',
                'esqlQuery': '',
                'controlType': 'STATIC_VALUES',
                'title': 'Aggregate Function',
                'selectedOptions': ['COUNT'],
                'singleSelect': True,
                'availableOptions': ['COUNT', 'AVG', 'SUM'],
            },
        }
    )


async def test_options_list_control_returns_reference() -> None:
    """Test that options list control returns a data view reference for dashboard."""
    from kb_dashboard_core.controls.compile import compile_options_list_control
    from kb_dashboard_core.controls.config import OptionsListControl

    control = OptionsListControl.model_validate(
        {
            'type': 'options',
            'data_view': 'metrics-*',
            'field': 'host.name',
            'label': 'Host Name',
        }
    )
    kbn_control, reference = compile_options_list_control(order=0, control=control)

    # Verify the control uses dataViewId
    assert kbn_control.explicitInput.dataViewId == 'metrics-*'

    # Verify a reference is returned
    assert reference.type == 'index-pattern'
    assert reference.id == 'metrics-*'
    assert reference.name == f'controlGroup_{kbn_control.explicitInput.id}:optionsListDataView'


async def test_range_slider_control_returns_reference() -> None:
    """Test that range slider control returns a data view reference for dashboard."""
    from kb_dashboard_core.controls.compile import compile_range_slider_control
    from kb_dashboard_core.controls.config import RangeSliderControl

    control = RangeSliderControl.model_validate(
        {
            'type': 'range',
            'data_view': 'logs-*',
            'field': 'response.time',
            'label': 'Response Time',
        }
    )
    kbn_control, reference = compile_range_slider_control(order=0, control=control)

    # Verify the control uses dataViewId
    assert kbn_control.explicitInput.dataViewId == 'logs-*'

    # Verify a reference is returned
    assert reference.type == 'index-pattern'
    assert reference.id == 'logs-*'
    assert reference.name == f'controlGroup_{kbn_control.explicitInput.id}:rangeSliderDataView'


async def test_time_slider_control_returns_no_reference() -> None:
    """Test that time slider control returns no reference (no data view needed)."""
    control = TimeSliderControl.model_validate(
        {
            'type': 'time',
            'start_offset': 0.0,
            'end_offset': 1.0,
        }
    )
    _, reference = compile_control(order=0, control=control)

    # Time slider has no data view, so no reference should be returned
    assert reference is None


async def test_control_group_returns_references() -> None:
    """Test that control group compilation returns references for bubble-up."""
    from kb_dashboard_core.controls.config import OptionsListControl, RangeSliderControl

    controls = [
        OptionsListControl.model_validate(
            {
                'type': 'options',
                'data_view': 'metrics-*',
                'field': 'host.name',
            }
        ),
        RangeSliderControl.model_validate(
            {
                'type': 'range',
                'data_view': 'logs-*',
                'field': 'response.time',
            }
        ),
        TimeSliderControl.model_validate(
            {
                'type': 'time',
                'start_offset': 0.0,
                'end_offset': 1.0,
            }
        ),
    ]
    control_settings = ControlSettings.model_validate({})
    _, references = compile_control_group(control_settings=control_settings, controls=controls)

    # Should have 2 references (options list + range slider), not 3 (time slider has none)
    assert len(references) == 2
    assert all(ref.type == 'index-pattern' for ref in references)
    data_view_ids = {ref.id for ref in references}
    assert data_view_ids == {'metrics-*', 'logs-*'}


async def test_esql_query_control_with_string_default() -> None:
    """Test ES|QL query control with string default value (single-select)."""
    config = {
        'type': 'esql',
        'variable_name': 'status_code',
        'variable_type': 'values',
        'query': 'FROM logs-* | STATS count BY http.response.status_code | KEEP http.response.status_code',
        'label': 'Status Code',
        'multiple': False,
        'default': '200',
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
                'selectedOptions': ['200'],
                'singleSelect': True,
            },
        }
    )


async def test_esql_query_control_with_list_default() -> None:
    """Test ES|QL query control with list default value (multi-select)."""
    config = {
        'type': 'esql',
        'variable_name': 'host_names',
        'variable_type': 'values',
        'query': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
        'label': 'Host Names',
        'multiple': True,
        'default': ['host1', 'host2'],
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
                'variableName': 'host_names',
                'variableType': 'values',
                'esqlQuery': 'FROM logs-* | STATS count BY host.name | KEEP host.name',
                'controlType': 'VALUES_FROM_QUERY',
                'title': 'Host Names',
                'selectedOptions': ['host1', 'host2'],
                'singleSelect': False,
            },
        }
    )
