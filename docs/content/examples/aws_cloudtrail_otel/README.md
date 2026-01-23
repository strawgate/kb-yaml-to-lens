# AWS CloudTrail OTEL Dashboard

This directory contains a YAML dashboard for the AWS CloudTrail OpenTelemetry integration, based on the dashboard from the [Elastic integrations repository](https://github.com/elastic/integrations/tree/main/packages/aws_cloudtrail_otel).

## Dashboard

**cloudtrail-logs-overview.yaml** - CloudTrail Logs Overview dashboard

This dashboard provides visualization of AWS CloudTrail activity logs to identify patterns in API calls, monitor account activity, detect unauthorized behavior, track resource changes, and troubleshoot operational issues.

## Data Requirements

This dashboard expects data from AWS CloudTrail via OpenTelemetry with the following fields:

### Core Fields

- `@timestamp` - Event timestamp
- `data_stream.dataset` - Should equal `aws.cloudtrail.otel`

### AWS CloudTrail Fields

- `aws.access_key.id` - AWS access key ID used for the API call
- `aws.error.code` - Error code if the operation failed
- `rpc.service` - AWS service name (e.g., s3, ec2)
- `rpc.system` - Event type/system
- `rpc.method` - AWS API method/action called
- `source.address` - Source IP address of the request
- `user_agent.original` - User agent string of the client

## Dashboard Features

### Panels

1. **Overview markdown** - Introduction and use cases
2. **Event outcome over time** (ES|QL area chart) - Success vs. failure trends
3. **Logs by service and action** (ES|QL donut chart) - Nested breakdown by service and method
4. **Logs by user agent** (ES|QL donut chart) - Distribution of client types
5. **Logs by event type** (ES|QL donut chart) - Event type distribution
6. **Failed operations by error code** (ES|QL donut chart) - Error code breakdown
7. **Recent Events** (ES|QL datatable) - Latest CloudTrail events with key fields
8. **Top User IDs** (ES|QL datatable) - Most active access keys by event count

### ES|QL Features

All visualizations in this dashboard use ES|QL (Elasticsearch Query Language) for data processing:

- **Dynamic field evaluation** - The outcome field is calculated using CASE expressions
- **String manipulation** - User agent parsing with REPLACE function
- **Aggregations** - COUNT, time bucketing with BUCKET function
- **Filtering** - WHERE clauses to exclude null values
- **Sorting and limiting** - Optimized queries with SORT and implicit limits

## Notes

This dashboard demonstrates several advanced ES|QL features:

- **Nested pie chart dimensions** - Service and method breakdown in a single donut chart
- **Calculated fields** - Outcome derived from error code presence
- **Time bucketing** - Automatic time interval calculation for area charts
- **Custom labels** - Field names displayed as human-readable labels where supported

## Known Limitations

- **Column labels in ES|QL datatables**: The Recent Events datatable panel does not have custom column labels because ES|QL dimensions don't support the `label` field (only metrics support labels in ES|QL panels)
- **User agent parsing**: The regex-based parsing may not handle all user agent formats perfectly
