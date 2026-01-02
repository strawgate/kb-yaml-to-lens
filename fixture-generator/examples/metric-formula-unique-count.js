#!/usr/bin/env node
/**
 * Example: Generate a metric with unique_count formula
 *
 * Demonstrates creating a formula metric: unique_count(field='user.id') * 2
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricFormulaUniqueCount() {
  // Data View variant - formulas work with Data View
  const dataviewConfig = {
    chartType: 'metric',
    title: 'Unique Users x2 (Formula)',
    dataset: {
      index: 'logs-*'
    },
    value: "unique_count(field='user.id') * 2",
    label: 'Unique Users (Doubled)'
  };

  await generateFixture(
    'metric-formula-unique-count-dataview.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricFormulaUniqueCount, import.meta.url);
