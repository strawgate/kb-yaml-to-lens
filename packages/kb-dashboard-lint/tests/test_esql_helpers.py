"""Tests for ES|QL query parsing helpers."""

from dashboard_lint.esql_helpers import (
    find_fixed_time_buckets,
    find_single_equals,
    find_sql_like_wildcards,
    find_sql_order_by,
    find_sql_select,
    find_unescaped_numeric_fields,
)


class TestFindSqlOrderBy:
    """Tests for find_sql_order_by."""

    def test_detects_order_by(self) -> None:
        """Should detect ORDER BY in query."""
        query = 'FROM logs-* | ORDER BY @timestamp DESC'
        matches = find_sql_order_by(query)
        assert len(matches) == 1

    def test_detects_order_by_case_insensitive(self) -> None:
        """Should detect order by in any case."""
        query = 'FROM logs-* | order by @timestamp'
        matches = find_sql_order_by(query)
        assert len(matches) == 1

    def test_no_match_for_sort(self) -> None:
        """Should not match SORT keyword."""
        query = 'FROM logs-* | SORT @timestamp DESC'
        matches = find_sql_order_by(query)
        assert len(matches) == 0


class TestFindSqlSelect:
    """Tests for find_sql_select."""

    def test_detects_select_at_start(self) -> None:
        """Should detect SELECT at start of query."""
        query = 'SELECT * FROM logs-*'
        matches = find_sql_select(query)
        assert len(matches) == 1

    def test_detects_select_with_whitespace(self) -> None:
        """Should detect SELECT with leading whitespace."""
        query = '  SELECT count(*) FROM logs-*'
        matches = find_sql_select(query)
        assert len(matches) == 1

    def test_no_match_for_from(self) -> None:
        """Should not match queries starting with FROM."""
        query = 'FROM logs-* | STATS count = COUNT(*)'
        matches = find_sql_select(query)
        assert len(matches) == 0


class TestFindSingleEquals:
    """Tests for find_single_equals."""

    def test_detects_single_equals_with_number(self) -> None:
        """Should detect single = in WHERE comparison with number."""
        query = 'FROM logs-* | WHERE status = 200'
        matches = find_single_equals(query)
        assert len(matches) == 1

    def test_detects_single_equals_with_string(self) -> None:
        """Should detect single = in WHERE comparison with string."""
        query = "FROM logs-* | WHERE host = 'server1'"
        matches = find_single_equals(query)
        assert len(matches) == 1

    def test_no_match_for_double_equals(self) -> None:
        """Should not match == comparison."""
        query = 'FROM logs-* | WHERE status == 200'
        matches = find_single_equals(query)
        assert len(matches) == 0

    def test_no_match_for_stats_assignment(self) -> None:
        """Should not match = assignment in STATS."""
        query = 'FROM logs-* | STATS count = COUNT(*)'
        matches = find_single_equals(query)
        assert len(matches) == 0

    def test_no_match_for_eval_assignment(self) -> None:
        """Should not match = assignment in EVAL."""
        query = 'FROM logs-* | EVAL doubled = value * 2'
        matches = find_single_equals(query)
        assert len(matches) == 0

    def test_no_match_for_less_than_equals(self) -> None:
        """Should not match <= comparison."""
        query = 'FROM logs-* | WHERE count <= 100'
        matches = find_single_equals(query)
        assert len(matches) == 0

    def test_no_match_for_greater_than_equals(self) -> None:
        """Should not match >= comparison."""
        query = 'FROM logs-* | WHERE count >= 10'
        matches = find_single_equals(query)
        assert len(matches) == 0


class TestFindSqlLikeWildcards:
    """Tests for find_sql_like_wildcards."""

    def test_detects_percent_wildcard(self) -> None:
        """Should detect % wildcard in LIKE."""
        query = "FROM logs-* | WHERE message LIKE '%error%'"
        matches = find_sql_like_wildcards(query)
        assert len(matches) == 1

    def test_detects_double_quote_wildcard(self) -> None:
        """Should detect % wildcard in double-quoted LIKE."""
        query = 'FROM logs-* | WHERE message LIKE "%error%"'
        matches = find_sql_like_wildcards(query)
        assert len(matches) == 1

    def test_no_match_for_asterisk_wildcard(self) -> None:
        """Should not match * wildcard (correct ES|QL syntax)."""
        query = "FROM logs-* | WHERE message LIKE '*error*'"
        matches = find_sql_like_wildcards(query)
        assert len(matches) == 0


class TestFindFixedTimeBuckets:
    """Tests for find_fixed_time_buckets."""

    def test_detects_fixed_bucket_minutes(self) -> None:
        """Should detect fixed minute bucket."""
        query = 'FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(@timestamp, 1 minute)'
        matches = find_fixed_time_buckets(query)
        assert len(matches) == 1

    def test_detects_fixed_bucket_hours(self) -> None:
        """Should detect fixed hour bucket."""
        query = 'FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(@timestamp, 1 hour)'
        matches = find_fixed_time_buckets(query)
        assert len(matches) == 1

    def test_detects_fixed_bucket_with_backticks(self) -> None:
        """Should detect fixed bucket with backtick-escaped timestamp."""
        query = 'FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(`@timestamp`, 5 minutes)'
        matches = find_fixed_time_buckets(query)
        assert len(matches) == 1

    def test_detects_tbucket_fixed(self) -> None:
        """Should detect fixed TBUCKET interval."""
        query = 'TS metrics-* | STATS rate = SUM(RATE(requests)) BY TBUCKET(5 minutes)'
        matches = find_fixed_time_buckets(query)
        assert len(matches) == 1

    def test_no_match_for_dynamic_bucket(self) -> None:
        """Should not match dynamic bucket sizing."""
        query = 'FROM logs-* | STATS count = COUNT(*) BY time_bucket = BUCKET(`@timestamp`, 20, ?_tstart, ?_tend)'
        matches = find_fixed_time_buckets(query)
        assert len(matches) == 0


class TestFindUnescapedNumericFields:
    """Tests for find_unescaped_numeric_fields."""

    def test_detects_unescaped_numeric_suffix(self) -> None:
        """Should detect field ending with number."""
        query = 'FROM metrics-* | WHERE apache.load.1 IS NOT NULL'
        matches = find_unescaped_numeric_fields(query)
        assert len(matches) == 1
        assert matches[0].group(1) == 'apache.load.1'

    def test_detects_multiple_unescaped_fields(self) -> None:
        """Should detect multiple unescaped numeric fields."""
        query = 'FROM metrics-* | WHERE apache.load.1 IS NOT NULL AND apache.load.5 IS NOT NULL'
        matches = find_unescaped_numeric_fields(query)
        assert len(matches) == 2

    def test_no_match_for_escaped_field(self) -> None:
        """Should not match backtick-escaped fields."""
        query = 'FROM metrics-* | WHERE `apache.load.1` IS NOT NULL'
        matches = find_unescaped_numeric_fields(query)
        assert len(matches) == 0

    def test_no_match_for_regular_field(self) -> None:
        """Should not match fields without numeric suffix."""
        query = 'FROM logs-* | WHERE host.name IS NOT NULL'
        matches = find_unescaped_numeric_fields(query)
        assert len(matches) == 0
