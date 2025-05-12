import pytest
from deepdiff import DeepDiff

from dashboard_compiler.dashboard.view import KbnDashboard
from dashboard_compiler.dashboard_compiler import render
from tests.conftest import DEEP_DIFF_DEFAULTS, de_json_kbn_dashboard
from tests.dashboards.test_dashboard_data import (
    TEST_CASE_IDS,
    TEST_CASES,
)

# Define fields to exclude from DeepDiff comparison
EXCLUDE_REGEX_PATHS = [
    'created_at',
    'created_by',
    'updated_at',
    'updated_by',
    'version',
    'id',
    # "root['attributes']['panelsJSON'][0]['panelIndex']"
    r'root\[\'attributes\'\]\[\'panelsJSON\'\]\[\d*]\[\'panelIndex\'\]',
    # r"root\['panelIndex'\]",  # Exclude the panelIndex field
    # r"root\['gridData'\]\['i'\]",  # Exclude the gridData.i field
]


@pytest.mark.parametrize(('db_input_dict', 'kb_desired_dict', 'exclusions'), TEST_CASES, ids=TEST_CASE_IDS)
async def test_compile_dashboard(db_input_dict: dict, kb_desired_dict: dict, exclusions: list[str]) -> None:
    """Test the compilation of various ImagePanel configurations to their Kibana view model."""
    # Compile the dashboard

    kbn_dashboard: KbnDashboard = render(dashboard=db_input_dict)

    compiled_kbn_dashboard_dict = kbn_dashboard.model_dump(by_alias=True)

    must_existin_compiled = [
        'updated_at',
        'updated_by',
        'version',
        'id',
        'created_at',
        'created_by',
    ]

    for key in must_existin_compiled:
        assert key in compiled_kbn_dashboard_dict, f'Key {key} must exist in compiled Kibana dashboard'

    kbn_dashboard_desired: dict = de_json_kbn_dashboard(kb_desired_dict)
    kbn_dashboard_compiled: dict = de_json_kbn_dashboard(compiled_kbn_dashboard_dict)

    exclude_regex_paths = [*EXCLUDE_REGEX_PATHS, *exclusions]

    assert DeepDiff(kbn_dashboard_desired, kbn_dashboard_compiled, exclude_regex_paths=exclude_regex_paths, **DEEP_DIFF_DEFAULTS) == {}  # type: ignore
