"""Tests for Pydantic models."""

from __future__ import annotations

from kb_dashboard_mcp.models import (
    DataStreamFieldSummary,
    DataStreamInfo,
    DataStreamRowExample,
    DataStreamSummary,
    DissectMatchResult,
    EsqlQueryResult,
    GrokMatchResult,
)


class TestDataStreamModels:
    """Tests for data stream models."""

    def test_data_stream_field_summary(self) -> None:
        """Test DataStreamFieldSummary creation."""
        summary = DataStreamFieldSummary(
            field='message',
            type='keyword',
            sample_values=['hello', 'world'],
        )
        assert summary.field == 'message'
        assert summary.type == 'keyword'
        assert summary.sample_values == ['hello', 'world']

    def test_data_stream_field_summary_no_samples(self) -> None:
        """Test DataStreamFieldSummary without sample values."""
        summary = DataStreamFieldSummary(
            field='count',
            type='long',
        )
        assert summary.field == 'count'
        assert summary.sample_values is None

    def test_data_stream_row_example(self) -> None:
        """Test DataStreamRowExample creation."""
        row = DataStreamRowExample(root={'message': 'test', 'level': 'info'})
        assert row.root == {'message': 'test', 'level': 'info'}

    def test_data_stream_summary(self) -> None:
        """Test DataStreamSummary creation."""
        summary = DataStreamSummary(
            data_stream='logs-test',
            fields=[
                DataStreamFieldSummary(field='message', type='keyword'),
            ],
            sample_rows=[
                DataStreamRowExample(root={'message': 'test'}),
            ],
        )
        assert summary.data_stream == 'logs-test'
        assert len(summary.fields) == 1
        assert len(summary.sample_rows) == 1

    def test_data_stream_info(self) -> None:
        """Test DataStreamInfo creation."""
        info = DataStreamInfo(
            name='logs-nginx-default',
            timestamp_field='@timestamp',
            backing_indices=['.ds-logs-nginx-default-000001'],
        )
        assert info.name == 'logs-nginx-default'
        assert info.timestamp_field == '@timestamp'
        assert len(info.backing_indices) == 1


class TestEsqlModels:
    """Tests for ES|QL models."""

    def test_esql_query_result(self) -> None:
        """Test EsqlQueryResult creation."""
        result = EsqlQueryResult(
            columns=[{'name': 'message', 'type': 'keyword'}],
            values=[['test']],
            is_columnar=False,
        )
        assert len(result.columns) == 1
        assert len(result.values) == 1
        assert result.is_columnar is False


class TestPatternModels:
    """Tests for pattern testing models."""

    def test_grok_match_result_matched(self) -> None:
        """Test GrokMatchResult when pattern matches."""
        result = GrokMatchResult(
            matched=True,
            fields={'ip': '192.168.1.1', 'method': 'GET'},
        )
        assert result.matched is True
        assert result.fields['ip'] == '192.168.1.1'

    def test_grok_match_result_not_matched(self) -> None:
        """Test GrokMatchResult when pattern does not match."""
        result = GrokMatchResult(matched=False, fields={})
        assert result.matched is False
        assert len(result.fields) == 0

    def test_dissect_match_result_success(self) -> None:
        """Test DissectMatchResult on success."""
        result = DissectMatchResult(
            document_index=0,
            success=True,
            fields={'ip': '192.168.1.1'},
        )
        assert result.document_index == 0
        assert result.success is True
        assert result.error is None

    def test_dissect_match_result_failure(self) -> None:
        """Test DissectMatchResult on failure."""
        result = DissectMatchResult(
            document_index=1,
            success=False,
            fields={},
            error='Pattern did not match',
        )
        assert result.success is False
        assert result.error == 'Pattern did not match'
