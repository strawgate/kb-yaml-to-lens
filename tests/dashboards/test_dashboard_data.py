import json
from pathlib import Path

import yaml

scenario_basedir = Path(__file__).parent / 'scenarios'


def get_kb_json(scenario_name: str) -> dict:
    """Load a JSON scenario file from the scenarios directory."""
    with Path.open(scenario_basedir / f'{scenario_name}.json') as file:
        return json.load(file)


def get_db_yaml(scenario_name: str) -> dict:
    """Load a YAML scenario file from the scenarios directory."""
    with Path.open(scenario_basedir / f'{scenario_name}.yaml') as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


CASE_MARKDOWN_DASHBOARD = (get_db_yaml('case_markdown_dashboard'), get_kb_json('case_markdown_dashboard'), [])
CASE_PIE_DASHBOARD = (get_db_yaml('case_pie_dashboard'), get_kb_json('case_pie_dashboard'), [])
CASE_QUERY_DASHBOARD = (get_db_yaml('case_query_dashboard'), get_kb_json('case_query_dashboard'), [])
CASE_LINK_DASHBOARD = (get_db_yaml('case_link_dashboard'), get_kb_json('case_link_dashboard'), [])
CASE_FILTER_DASHBOARD = (
    get_db_yaml('case_filter_dashboard'),
    get_kb_json('case_filter_dashboard'),
    [
        r"root\['references'\]\[0\]",
        r"root\['references'\]\[1\]",
        r"root\[\'attributes\'\]\['kibanaSavedObjectMeta'\]\['searchSourceJSON'\]\['filter'\]\[\d*\]\['meta'\]\['indexRefName'\]",
    ],
)
CASE_XY_LINE_DASHBOARD = (get_db_yaml('case_xy_line_dashboard'), get_kb_json('case_xy_line_dashboard'), [])
CASE_YAML_REF_DASHBOARD = (get_db_yaml('case_yaml_ref_dashboard'), get_kb_json('case_yaml_ref_dashboard'), [])

TEST_CASES = [
    CASE_MARKDOWN_DASHBOARD,
    CASE_PIE_DASHBOARD,
    CASE_QUERY_DASHBOARD,
    CASE_LINK_DASHBOARD,
    CASE_FILTER_DASHBOARD,
    CASE_YAML_REF_DASHBOARD,
    CASE_XY_LINE_DASHBOARD,
]

TEST_CASE_IDS = [
    'Dashboard with One Markdown Panel',
    'Dashboard with One Pie Chart',
    'Dashboard with One Query',
    'Dashboard with One Link',
    'Dashboard with One Filter',
    'Dashboard with One YAML Ref',
    'Dashboard with One XY Line Chart',
]
