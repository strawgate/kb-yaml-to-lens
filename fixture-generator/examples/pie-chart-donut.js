#!/usr/bin/env node
/**
 * Example: Generate a donut chart with labels
 *
 * Demonstrates creating a pie chart in donut mode with various label configurations
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartDonut() {
  const config = {
    chartType: 'pie',
    title: 'Response Codes Distribution (Donut)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY response.keyword'
    },
    breakdown: 'response.keyword',
    metric: 'count',
    shape: 'donut',
    labels: {
      show: true,
      position: 'inside',
      percentDecimals: 1
    },
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'pie-chart-donut.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChartDonut, import.meta.url);
