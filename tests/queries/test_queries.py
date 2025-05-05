"""Test the compilation of filters from config models to view models."""

from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff
from pydantic import BaseModel

from dashboard_compiler.queries.compile import compile_query
from dashboard_compiler.queries.config import (
    QueryTypes,
)
from tests.conftest import DEEP_DIFF_DEFAULTS
from tests.queries.test_queries_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

if TYPE_CHECKING:
    from dashboard_compiler.queries.view import KbnQuery

EXCLUDE_REGEX_PATHS = []


class QueryHolder(BaseModel):
    """A holder for query configurations to be used in tests."""

    query: QueryTypes


@pytest.mark.parametrize(('config', 'desired_output'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_queries(config: dict, desired_output: dict) -> None:
    """Test the compilation of various query configurations to their Kibana view model."""
    query_holder = QueryHolder.model_validate({'query': config})

    kbn_query: KbnQuery = compile_query(query=query_holder.query)
    kbn_query_as_dict = kbn_query.model_dump()

    assert DeepDiff(desired_output, kbn_query_as_dict, exclude_regex_paths=EXCLUDE_REGEX_PATHS, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
