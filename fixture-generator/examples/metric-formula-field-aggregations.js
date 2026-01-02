#!/usr/bin/env node
/**
 * Example: Generate a metric with field-based formula aggregations
 *
 * Demonstrates creating a formula metric: (max(field='response.time') - min(field='response.time')) / average(field='response.time')
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricFormulaFieldAggregations() {
  // Data View variant - formulas work with Data View
  const dataviewConfig = {
    chartType: 'metric',
    title: 'Response Time Range (Formula)',
    dataset: {
      index: 'metrics-*'
    },
    value: "(max(field='response.time') - min(field='response.time')) / average(field='response.time')",
    label: 'Response Time Variability'
  };

  await generateFixture(
    'metric-formula-field-aggregations-dataview.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricFormulaFieldAggregations, import.meta.url);
