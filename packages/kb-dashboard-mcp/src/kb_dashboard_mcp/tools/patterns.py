"""Grok and dissect pattern testing tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.tools import Tool

from kb_dashboard_mcp.models import DissectMatchResult, GrokMatchResult

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from kb_dashboard_mcp.client import KibanaClient


async def run_grok_pattern_test(
    client: KibanaClient,
    pattern: str,
    text: str,
    custom_patterns: dict[str, str] | None = None,
) -> GrokMatchResult:
    """Test a grok pattern against sample text.

    Args:
        client: KibanaClient instance.
        pattern: The grok pattern to test.
        text: Sample text to match against.
        custom_patterns: Optional custom pattern definitions.

    Returns:
        Match result with extracted fields if successful.

    Raises:
        ValueError: If the pattern is empty.
    """
    if len(pattern.strip()) == 0:
        msg = 'Pattern cannot be empty'
        raise ValueError(msg)

    result = await client.test_grok_pattern(
        grok_pattern=pattern,
        text=[text],
        pattern_definitions=custom_patterns,
    )

    matches: list[dict[str, Any]] = result.get('matches', [])

    if len(matches) == 0:
        return GrokMatchResult(matched=False, fields={})

    first_match = matches[0]
    return GrokMatchResult(
        matched=True,
        fields=first_match.get('match', {}),
    )


async def run_dissect_pattern_test(
    client: KibanaClient,
    pattern: str,
    documents: list[str],
    field: str = 'message',
) -> list[DissectMatchResult]:
    """Test a dissect pattern against sample documents.

    Args:
        client: KibanaClient instance.
        pattern: The dissect pattern to test.
        documents: Sample documents to match against.
        field: The field name containing the text to dissect.

    Returns:
        Extracted fields and values for each document.

    Raises:
        ValueError: If the pattern is empty.
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

    result = await client.simulate_ingest(pipeline=pipeline, docs=docs)

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


def register_pattern_tools(mcp: FastMCP, client: KibanaClient) -> None:
    """Register pattern testing tools with the MCP server.

    Args:
        mcp: FastMCP server instance.
        client: KibanaClient instance.
    """

    async def _test_grok_pattern(
        pattern: Annotated[str, 'The grok pattern to test'],
        text: Annotated[str, 'Sample text to match against'],
        custom_patterns: Annotated[dict[str, str] | None, 'Custom pattern definitions'] = None,
    ) -> GrokMatchResult:
        """Test a grok pattern against sample text.

        Returns matched fields and values if the pattern matches.
        """
        return await run_grok_pattern_test(client, pattern, text, custom_patterns)

    async def _test_dissect_pattern(
        pattern: Annotated[str, 'The dissect pattern to test'],
        documents: Annotated[list[str], 'Sample documents to match against'],
        field: Annotated[str, 'The field name containing the text to dissect'] = 'message',
    ) -> list[DissectMatchResult]:
        """Test a dissect pattern against sample documents.

        Uses pipeline simulation to test the dissect processor.
        Returns extracted fields and values for each document.
        """
        return await run_dissect_pattern_test(client, pattern, documents, field)

    mcp.add_tool(Tool.from_function(_test_grok_pattern, name='test_grok_pattern', tags={'patterns', 'grok'}))
    mcp.add_tool(Tool.from_function(_test_dissect_pattern, name='test_dissect_pattern', tags={'patterns', 'dissect'}))
