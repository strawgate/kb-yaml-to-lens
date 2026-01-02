#!/usr/bin/env node
/**
 * Example: Generate a metric with simple arithmetic formula
 *
 * Demonstrates creating a formula metric: (count(kql='status:error') / count()) * 100
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateMetricFormulaSimpleArithmetic() {
  // Data View variant - formulas work with Data View
  const dataviewConfig = {
    chartType: 'metric',
    title: 'Error Rate % (Formula)',
    dataset: {
      index: 'logs-*'
    },
    value: "(count(kql='status:error') / count()) * 100",
    label: 'Error Rate %'
  };

  await generateFixture(
    'metric-formula-simple-arithmetic-dataview.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateMetricFormulaSimpleArithmetic, import.meta.url);
