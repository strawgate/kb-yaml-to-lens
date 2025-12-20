"""Test data for control compilation tests."""

CASE_OPTIONS_LIST = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'medium',
        'explicitInput': {
            'id': 'edd2918a-ed98-4d74-820a-691a42afcc5d',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'searchTechnique': 'prefix',
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control."""

CASE_OPTIONS_LIST_CUSTOM_LABEL = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Custom Label',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'medium',
        'explicitInput': {
            'id': '29e62ae5-342d-4b40-b24b-2308aa8f60b8',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'Custom Label',
            'searchTechnique': 'prefix',
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with a custom label"""

CASE_OPTIONS_LARGE_WIDTH = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'label': 'Large Option',
        'field': 'aerospike.namespace',
        'width': 'large',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'large',
        'explicitInput': {
            'id': '02ce1e41-4e2e-40e6-b7f9-5f4ee1744548',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'Large Option',
            'searchTechnique': 'prefix',
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with large width"""

CASE_OPTIONS_LARGE_WITH_EXPAND = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Large Option with Expand',
        'width': 'large',
        'fill_width': True,
    },
    {
        'grow': True,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'large',
        'explicitInput': {
            'id': 'f843413c-1aa0-4125-92fb-da55929bdaab',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'Large Option with Expand',
            'searchTechnique': 'prefix',
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with large width and expand option"""

CASE_OPTIONS_SMALL_SINGLE_SELECT = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Small Option Single Select',
        'match_technique': 'prefix',
        'singular': True,
        'width': 'small',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'small',
        'explicitInput': {
            'id': '4c0b6200-f697-4314-9f9c-2eb1c7f1bc91',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'Small Option Single Select',
            'searchTechnique': 'prefix',
            'singleSelect': True,
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with small width and single select"""

CASE_OPTIONS_CONTAINS = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'label': 'Contains',
        'match_technique': 'contains',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'medium',
        'explicitInput': {
            'id': '1a573455-e71b-40d0-962c-74c8855aef18',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'Contains',
            'searchTechnique': 'wildcard',
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with contains search technique"""

CASE_OPTIONS_EXACT = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'match_technique': 'exact',
        'label': 'Exact',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'medium',
        'explicitInput': {
            'id': '4cf84585-03ff-4778-b925-d80efb959384',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'Exact',
            'searchTechnique': 'exact',
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with exact search technique"""

CASE_OPTIONS_IGNORE_TIMEOUT = (
    {
        'type': 'options',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace',
        'wait_for_results': True,
        'label': 'ignore-timeout',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'optionsListControl',
        'width': 'medium',
        'explicitInput': {
            'id': 'bbcbd7fa-7935-4f6c-84dc-21357a6b011f',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace',
            'title': 'ignore-timeout',
            'searchTechnique': 'prefix',
            'runPastTimeout': True,
            'selectedOptions': [],
            'sort': {'by': '_count', 'direction': 'desc'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for an optionsList control with ignore timeout"""

CASE_RANGE = (
    {
        'type': 'range',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'label': 'Default Range',
        'field': 'aerospike.namespace.geojson.region_query_cells',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'rangeSliderControl',
        'width': 'medium',
        'explicitInput': {
            'id': '7f70d568-faf8-4803-9eaa-d317433c6d07',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace.geojson.region_query_cells',
            'title': 'Default Range',
            'step': 1,
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a rangeSlider control with default step size of 1"""

CASE_RANGE_STEP_10 = (
    {
        'type': 'range',
        'data_view': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
        'field': 'aerospike.namespace.geojson.region_query_cells',
        'step': 10,
        'label': 'Range step 10',
    },
    {
        'grow': False,
        'order': 0,
        'type': 'rangeSliderControl',
        'width': 'medium',
        'explicitInput': {
            'id': '89325a91-90f9-4b9c-9271-64f1744c2a79',
            'dataViewId': '27a3148b-d1d4-4455-8acf-e63c94071a5b',
            'fieldName': 'aerospike.namespace.geojson.region_query_cells',
            'title': 'Range step 10',
            'step': 10,
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a rangeSlider control with step size of 10"""

CASE_TIME_SLIDER = (
    {
        'type': 'time',
        'start_offset': 0.5825778,
        'end_offset': 0.995556,
    },
    {
        'grow': True,
        'order': 0,
        'type': 'timeSlider',
        'width': 'medium',
        'explicitInput': {
            'id': '90d80170-eb3e-4a9e-9d78-f5e69e7a39ed',
            'timesliceStartAsPercentageOfTimeRange': 0.5825778,
            'timesliceEndAsPercentageOfTimeRange': 0.995556,
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a timeSlider control with default settings."""

CASE_SETTINGS = (
    {},
    {
        'chainingSystem': 'HIERARCHICAL',
        'controlStyle': 'oneLine',
        'ignoreParentSettingsJSON': {'ignoreFilters': False, 'ignoreQuery': False, 'ignoreTimerange': False, 'ignoreValidations': False},
        'panelsJSON': {},
        'showApplySelections': False,
    },
)

CASE_SETTINGS_CUSTOM = (
    {
        'label_position': 'above',
        'apply_global_filters': False,
        'apply_global_timerange': False,
        'ignore_zero_results': True,
        'chain_controls': False,
        'click_to_apply': True,
    },
    {
        'chainingSystem': 'NONE',
        'controlStyle': 'twoLine',
        'ignoreParentSettingsJSON': {'ignoreFilters': True, 'ignoreQuery': True, 'ignoreTimerange': True, 'ignoreValidations': True},
        'panelsJSON': {},
        'showApplySelections': True,
    },
)
"""Tuple[Config as Dict, View as Dict] for inverted control settings"""

SETTINGS_TEST_CASES = [
    CASE_SETTINGS,
    CASE_SETTINGS_CUSTOM,
]

SETTINGS_TEST_CASE_IDS = [
    'Default Control Settings',
    'Custom Control Settings',
]

CONTROLS_TEST_CASES = [
    CASE_OPTIONS_LIST,
    CASE_OPTIONS_LIST_CUSTOM_LABEL,
    CASE_OPTIONS_LARGE_WIDTH,
    CASE_OPTIONS_LARGE_WITH_EXPAND,
    CASE_OPTIONS_SMALL_SINGLE_SELECT,
    CASE_OPTIONS_CONTAINS,
    CASE_OPTIONS_EXACT,
    CASE_OPTIONS_IGNORE_TIMEOUT,
    CASE_RANGE,
    CASE_RANGE_STEP_10,
    CASE_TIME_SLIDER,
]

CONTROLS_TEST_CASE_IDS = [
    'Normal Options List',
    'Options List with Custom Label',
    'Options List with Large Width',
    'Options List with Large Width and Expand',
    'Options List with Small Width and Single Select',
    'Options List with Contains Search Technique',
    'Options List with Exact Search Technique',
    'Options List with Ignore Timeout',
    'Range Slider with Default Step Size',
    'Range Slider with Step Size 10',
    'Time Slider with Default Settings',
]
