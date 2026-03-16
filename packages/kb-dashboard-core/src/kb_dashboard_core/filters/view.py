"""View models for filters in the Kibana JSON structure."""

from typing import Annotated, Any, Literal, cast

from pydantic import AliasChoices, ConfigDict, Field, model_validator

from kb_dashboard_core.shared.view import BaseVwModel, OmitIfNone

# The following is an example of the JSON structure that these models represent. Do not remove:
# {
#   "filter": [
#     {
#       "meta": {
#         "disabled": false,
#         "negate": false,
#         "alias": null,
#         "key": "aerospike.namespace",
#         "field": "aerospike.namespace",
#         "params": {
#           "query": "test"
#         },
#         "type": "phrase",
#         "indexRefName": "kibanaSavedObjectMeta.searchSourceJSON.filter[0].meta.index"
#       },
#       "query": {
#         "match_phrase": {
#           "aerospike.namespace": "test"
#         }
#       },
#       "$state": {
#         "store": "appState"
#       }
#     }
#   ]
# }


type FilterScalar = str | int | float | bool


class KbnBaseFilterMeta(BaseVwModel):
    disabled: bool
    """Indicates whether the filter is disabled."""

    negate: bool
    """Indicates whether the filter is negated (i.e., it filters out the specified values)."""

    alias: str | None = None
    """An optional alias for the filter, used for display purposes."""

    index: Annotated[str | None, OmitIfNone()] = Field(default=None)
    """The data view / index associated with the filter, if applicable."""


class KbnCombinedFilterMeta(KbnBaseFilterMeta):
    """Represents the meta information for a combined filter in the Kibana JSON structure."""

    type: Literal['combined'] = Field(default='combined')

    relation: Annotated[Literal['AND', 'OR'] | None, OmitIfNone()]
    """The relation of the 'combined' filter, if applicable. Can be 'AND' or 'OR'."""

    params: Annotated[list['KbnFilter'], 'KbnFilter', OmitIfNone()]
    """Parameters for the filter, which can include a list of other filters that are combined."""


class KbnFilterMeta(KbnBaseFilterMeta):
    """Represents the meta information of a filter in the Kibana JSON structure."""

    type: Literal['phrase', 'phrases', 'range', 'exists']
    """The type of filter, e.g., 'phrase', 'phrases', 'range', 'exists', etc."""

    key: str
    """The key of the filter, typically the field name being filtered on."""

    field: str | None = None
    """The field name being filtered on, same as `key` in most cases."""

    params: Annotated[dict[str, Any] | list[FilterScalar] | None, OmitIfNone()] = Field(default=None)
    """Parameters for the filter, such as the value to match against."""

    @model_validator(mode='before')
    @classmethod
    def _populate_field_from_key(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        typed_data = cast('dict[str, Any]', data)
        key = typed_data.get('key')
        if typed_data.get('field') is None and isinstance(key, str):
            normalized = dict(typed_data)
            normalized['field'] = key
            return normalized
        return typed_data


class KbnCustomFilterMeta(KbnBaseFilterMeta):
    """Represents the meta information for a custom filter in the Kibana JSON structure."""

    type: Literal['custom'] = Field(default='custom')
    """The type of filter, which is 'custom' for custom filters."""

    key: Literal['query'] = Field(default='query')
    """The key for the custom filter, which is always 'query'."""


type KbnFilterMetaTypes = KbnFilterMeta | KbnCombinedFilterMeta | KbnCustomFilterMeta


class KbnFilterState(BaseVwModel):
    """Represents the $state of a filter."""

    store: str = Field(default='appState')


class KbnFilter(BaseVwModel):
    """Represents a filter object within state.filters in the Kibana JSON structure."""

    model_config: ConfigDict = ConfigDict(serialize_by_alias=True)
    """Configuration for the model to serialize using aliases for the $state field."""

    state: Annotated[KbnFilterState | None, OmitIfNone()] = Field(
        default=None,
        validation_alias=AliasChoices('state', '$state'),
        serialization_alias='$state',
    )
    meta: KbnFilterMetaTypes
    query: Annotated[dict[str, Any] | None, OmitIfNone()]
