#!/usr/bin/env node
/**
 * Example: Generate a metric with filtered aggregations in formula
 *
 * Demonstrates creating a formula metric: sum(field='bytes', kql='status:200') + sum(field='bytes', kql='status:404')
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricFormulaFilteredAggregations() {
  // Data View variant - formulas work with Data View
  const dataviewConfig = {
    chartType: 'metric',
    title: 'Bytes by Status (Formula)',
    dataset: {
      index: 'logs-*'
    },
    value: "sum(field='bytes', kql='status:200') + sum(field='bytes', kql='status:404')",
    label: 'Total Bytes (200 + 404)'
  };

  await generateFixture(
    'metric-formula-filtered-aggregations-dataview.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricFormulaFilteredAggregations, import.meta.url);
