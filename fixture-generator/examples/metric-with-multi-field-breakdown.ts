#!/usr/bin/env node
/**
 * Example: Generate metric with multi-field breakdown visualizations
 *
 * This fixture attempts to create a metric with multiple breakdown fields
 * to discover how Kibana's JSON schema handles multi-field breakdowns.
 *
 * Note: LensConfigBuilder may not fully support multi-field breakdowns via the API,
 * so we'll test single breakdown first, then investigate the JSON structure.
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricWithMultiFieldBreakdown(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensMetricConfig> = {
    label: 'Events by Service and Host'
  };

  // ES|QL variant - using two breakdown fields in the query
  const esqlConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Count by Service and Host',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY service.name, host.name | SORT count DESC | LIMIT 20'
    },
    value: 'count',
    // Note: LensConfigBuilder's 'breakdown' is typed as string, not string[]
    // We'll start with a single breakdown field to see the JSON structure
    breakdown: 'service.name'
  };

  // Data View variant
  const dataviewConfig: LensMetricConfig = {
    chartType: 'metric',
    ...sharedConfig,
    title: 'Count by Service and Host (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: 'service.name'
  };

  await generateDualFixture(
    'metric-with-multi-field-breakdown',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithMultiFieldBreakdown, import.meta.url);
