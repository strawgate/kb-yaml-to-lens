#!/usr/bin/env node
/**
 * Example: Generate a basic metric visualization (both ES|QL and Data View)
 *
 * Demonstrates creating a simple count metric
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricBasic() {
  // Shared configuration between both variants
  const sharedConfig = {
    chartType: 'metric',
    label: 'Total Events'
  };

  // ES|QL variant
  const esqlConfig = {
    ...sharedConfig,
    title: 'Basic Count Metric',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count'
  };

  // Data View variant
  const dataviewConfig = {
    ...sharedConfig,
    title: 'Basic Count Metric (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()'
  };

  await generateDualFixture(
    'metric-basic',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricBasic, import.meta.url);
