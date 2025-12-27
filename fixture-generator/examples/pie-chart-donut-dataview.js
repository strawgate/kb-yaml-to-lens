#!/usr/bin/env node
/**
 * Example: Generate a donut chart visualization (using data view)
 *
 * Demonstrates creating a pie chart with donut display and label configuration
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartDonutDataview() {
  const config = {
    chartType: 'pie',
    title: 'Log Level Distribution (Donut - Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: ['log.level'],
    shape: 'donut',
    labels: {
      show: true,
      position: 'inside',
      values: true,
      percentDecimals: 1
    },
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'pie-chart-donut-dataview.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChartDonutDataview, import.meta.url);
