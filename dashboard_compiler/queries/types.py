from dashboard_compiler.queries.config import ESQLQuery, KqlQuery, LuceneQuery

type LegacyQueryTypes = KqlQuery | LuceneQuery

type ESQLQueryTypes = ESQLQuery

type QueryTypes = LegacyQueryTypes | ESQLQueryTypes
