"""Test the compilation of controls from config models to view models."""

import json
import re
from typing import TYPE_CHECKING, Any

import pytest
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


@pytest.fixture
def compile_control_snapshot():
    """Fixture that returns a function to compile control and return dict for snapshot."""

    def _compile(config: dict[str, Any]) -> dict[str, Any]:
        control_holder: ControlHolder = ControlHolder.model_validate({'control': config})
        kbn_control_group_input: KbnControlTypes = compile_control(order=0, control=control_holder.control)
        result = kbn_control_group_input.model_dump(by_alias=True)
        # Replace dynamic ID with placeholder
        if 'explicitInput' in result and 'id' in result['explicitInput']:
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if re.match(pattern, result['explicitInput']['id']):
                result['explicitInput']['id'] = 'DYNAMIC_ID'
        return result

    return _compile


@pytest.fixture
def compile_control_settings_snapshot():
    """Fixture that returns a function to compile control settings and return dict for snapshot."""

    def _compile(config: dict[str, Any]) -> dict[str, Any]:
        control_settings = ControlSettings.model_validate(obj=config)
        kbn_control_group_input: KbnControlGroupInput = compile_control_group(control_settings=control_settings, controls=[])
        result = kbn_control_group_input.model_dump(by_alias=True)

        if 'ignoreParentSettingsJSON' in result and isinstance(result['ignoreParentSettingsJSON'], str):
            result['ignoreParentSettingsJSON'] = json.loads(result['ignoreParentSettingsJSON'])

        if 'panelsJSON' in result and isinstance(result['panelsJSON'], str):
            result['panelsJSON'] = json.loads(result['panelsJSON'])

        return result

    return _compile


async def test_normal_options_list(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_custom_label(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Custom Label',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_large_width(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Large Option',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_large_width_and_expand(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Large Option with Expand',
                'searchTechnique': 'prefix',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_small_width_and_single_select(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
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


async def test_options_list_with_contains_search_technique(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Contains',
                'searchTechnique': 'wildcard',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_exact_search_technique(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace',
                'title': 'Exact',
                'searchTechnique': 'exact',
                'selectedOptions': [],
                'sort': {'by': '_count', 'direction': 'desc'},
            },
        }
    )


async def test_options_list_with_ignore_timeout(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
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


async def test_range_slider_with_default_step_size(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace.geojson.region_query_cells',
                'title': 'Default Range',
                'step': 1,
            },
        }
    )


async def test_range_slider_with_step_size_10(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
                'fieldName': 'aerospike.namespace.geojson.region_query_cells',
                'title': 'Range step 10',
                'step': 10,
            },
        }
    )


async def test_time_slider_with_default_settings(compile_control_snapshot) -> None:
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
                'id': 'DYNAMIC_ID',
                'timesliceStartAsPercentageOfTimeRange': 0.5825778,
                'timesliceEndAsPercentageOfTimeRange': 0.995556,
            },
        }
    )


async def test_default_control_settings(compile_control_settings_snapshot) -> None:
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


async def test_custom_control_settings(compile_control_settings_snapshot) -> None:
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
