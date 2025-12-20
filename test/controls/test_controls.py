"""Test the compilation of controls from config models to view models."""

from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff
from pydantic import BaseModel

from dashboard_compiler.controls.compile import compile_control, compile_control_group
from dashboard_compiler.controls.config import ControlSettings, ControlTypes
from test.conftest import DEEP_DIFF_DEFAULTS
from test.controls.test_controls_data import (
    CONTROLS_TEST_CASE_IDS,
    CONTROLS_TEST_CASES,
    SETTINGS_TEST_CASE_IDS,
    SETTINGS_TEST_CASES,
)

if TYPE_CHECKING:
    from dashboard_compiler.controls.view import KbnControlGroupInput, KbnControlTypes

EXCLUDE_REGEX_PATHS = [
    r"root\['explicitInput'\]\['id'\]",  # Exclude the id field in explicitInput "root['explicitInput']['id']"
]


class ControlHolder(BaseModel):
    """A holder for control configurations to be used in tests."""

    # Use the correct type from the existing config file
    control: ControlTypes


@pytest.mark.parametrize(('config', 'desired_output'), argvalues=CONTROLS_TEST_CASES, ids=CONTROLS_TEST_CASE_IDS)
async def test_compile_controls(config: dict, desired_output: dict) -> None:
    """Test the compilation of various control configurations to their Kibana view model."""
    control_holder: ControlHolder = ControlHolder.model_validate({'control': config})

    # The compile_controls function takes a list of controls and returns a KbnControlGroupInput
    kbn_control_group_input: KbnControlTypes = compile_control(order=0, control=control_holder.control)
    kbn_control_group_input_as_dict = kbn_control_group_input.model_dump(by_alias=True)  # Use by_alias for $state

    assert DeepDiff(desired_output, kbn_control_group_input_as_dict, **DEEP_DIFF_DEFAULTS, exclude_regex_paths=EXCLUDE_REGEX_PATHS) == {}  # type: ignore


@pytest.mark.parametrize(('config', 'desired_output'), argvalues=SETTINGS_TEST_CASES, ids=SETTINGS_TEST_CASE_IDS)
async def test_compile_control_settings(config: dict, desired_output: dict) -> None:
    """Test the compilation of control settings configurations to their Kibana view model."""
    control_settings = ControlSettings.model_validate(obj=config)

    # The compile_controls function takes a list of controls and returns a KbnControlGroupInput
    kbn_control_group_input: KbnControlGroupInput = compile_control_group(control_settings=control_settings, controls=[])
    kbn_control_group_input_as_dict = kbn_control_group_input.model_dump(by_alias=True)

    assert DeepDiff(desired_output, kbn_control_group_input_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
