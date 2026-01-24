"""Grok and dissect pattern testing tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.tools import Tool

from kb_dashboard_mcp.models import DissectMatchResult, GrokMatchResult

if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch
    from fastmcp import FastMCP


def register_pattern_tools(mcp: FastMCP, es: AsyncElasticsearch) -> None:
    """Register pattern testing tools with the MCP server."""

    async def test_grok_pattern(
        pattern: Annotated[str, 'The grok pattern to test'],
        text: Annotated[str, 'Sample text to match against'],
        custom_patterns: Annotated[dict[str, str] | None, 'Custom pattern definitions'] = None,
    ) -> GrokMatchResult:
        """Test a grok pattern against sample text.

        Returns matched fields and values if the pattern matches.
        """
        if len(pattern.strip()) == 0:
            msg = 'Pattern cannot be empty'
            raise ValueError(msg)

        kwargs: dict[str, Any] = {
            'grok_pattern': pattern,
            'text': [text],
        }

        if custom_patterns is not None:
            kwargs['pattern_definitions'] = custom_patterns

        result = await es.text_structure.test_grok_pattern(**kwargs)

        matches: list[dict[str, Any]] = result.get('matches', [])

        if len(matches) == 0:
            return GrokMatchResult(matched=False, fields={})

        first_match = matches[0]
        return GrokMatchResult(
            matched=True,
            fields=first_match.get('match', {}),
        )

    async def test_dissect_pattern(
        pattern: Annotated[str, 'The dissect pattern to test'],
        documents: Annotated[list[str], 'Sample documents to match against'],
        field: Annotated[str, 'The field name containing the text to dissect'] = 'message',
    ) -> list[DissectMatchResult]:
        """Test a dissect pattern against sample documents.

        Uses pipeline simulation to test the dissect processor.
        Returns extracted fields and values for each document.
        """
        if len(pattern.strip()) == 0:
            msg = 'Pattern cannot be empty'
            raise ValueError(msg)

        if len(documents) == 0:
            return []

        pipeline = {
            'processors': [
                {
                    'dissect': {
                        'field': field,
                        'pattern': pattern,
                    }
                }
            ]
        }

        docs = [{'_source': {field: doc}} for doc in documents]

        result = await es.ingest.simulate(pipeline=pipeline, docs=docs)

        results: list[DissectMatchResult] = []
        response_docs: list[dict[str, Any]] = result.get('docs', [])

        for i, doc_result in enumerate(response_docs):
            doc: dict[str, Any] = doc_result.get('doc', {})
            source: dict[str, Any] = doc.get('_source', {})
            error: dict[str, Any] | None = doc_result.get('error')

            if error is not None:
                error_reason = error.get('reason', 'Unknown error')
                results.append(
                    DissectMatchResult(
                        document_index=i,
                        success=False,
                        fields={},
                        error=error_reason,
                    )
                )
            else:
                extracted_fields = {k: v for k, v in source.items() if k != field}
                results.append(
                    DissectMatchResult(
                        document_index=i,
                        success=True,
                        fields=extracted_fields,
                    )
                )

        return results

    mcp.add_tool(Tool.from_function(test_grok_pattern, tags={'patterns', 'grok'}))
    mcp.add_tool(Tool.from_function(test_dissect_pattern, tags={'patterns', 'dissect'}))
