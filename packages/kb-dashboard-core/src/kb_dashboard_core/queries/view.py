"""Kibana models for the query object in the dashboard."""

from typing import Literal

from kb_dashboard_core.shared.view import BaseVwModel

# The following is an example of the JSON structure that these models represent. Do not remove:
# "query": {                               <-- KbnQuery
#     "query": "",
#     "language": "kuery"
# }


class KbnQuery(BaseVwModel):
    """Represents the query object within state.query in the Kibana JSON structure."""

    query: str
    language: Literal['kuery', 'lucene']


class KbnESQLQuery(BaseVwModel):
    """Represents the query object within state.query in the Kibana JSON structure."""

    esql: str
