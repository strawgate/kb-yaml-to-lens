#!/usr/bin/env node
/**
 * Example: Generate metric with breakdown visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a metric that breaks down by a field
 */

import type { LensMetricConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.ts';

export async function generateMetricWithBreakdown(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensMetricConfig> = {
    chartType: 'metric',
    label: 'Events per Agent'
  };

  // ES|QL variant
  const esqlConfig: LensMetricConfig = {
    ...sharedConfig,
    title: 'Count by Agent',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY agent.name | SORT count DESC | LIMIT 5'
    },
    value: 'count',
    breakdown: 'agent.name'
  };

  // Data View variant
  const dataviewConfig: LensMetricConfig = {
    ...sharedConfig,
    title: 'Count by Agent (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: 'agent.name'
  };

  await generateDualFixture(
    'metric-with-breakdown',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricWithBreakdown, import.meta.url);
