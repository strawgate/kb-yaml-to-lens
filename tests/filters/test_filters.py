"""Test the compilation of filters from config models to view models."""

from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff
from pydantic import BaseModel

from dashboard_compiler.filters.compile import compile_filters
from dashboard_compiler.filters.config import FilterTypes
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.filters.test_filters_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

if TYPE_CHECKING:
    from dashboard_compiler.filters.view import KbnFilter

EXCLUDE_REGEX_PATHS = [
    r"\['\$state'\]",  # We don't care about differences in the $state field
]


class FilterHolder(BaseModel):
    """A holder for filter configurations to be used in tests."""

    filter: FilterTypes


@pytest.mark.parametrize(('config', 'desired_output'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_filters(config: dict, desired_output: dict) -> None:
    """Test the compilation of various filter configurations to their Kibana view model."""
    filter_holder = FilterHolder.model_validate({'filter': config})

    kbn_filter: KbnFilter = compile_filters(filters=[filter_holder.filter])[0]
    kbn_filter_as_dict = kbn_filter.model_dump()

    assert DeepDiff(desired_output, kbn_filter_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
