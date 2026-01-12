#!/usr/bin/env node
/**
 * Example: Generate pie chart with legend statistics (Data View only)
 *
 * Demonstrates creating a pie chart with legend showing current/last value and average statistics.
 * Note: Legend statistics require Data View, not ES|QL.
 */

import type { LensPieConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartLegendStats(): Promise<void> {
  // Data View variant only - legend stats work best with Data View
  const dataviewConfig: LensPieConfig = {
    chartType: 'pie',
    title: 'Events by Status with Legend Stats',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: ['log.level'],
    legend: {
      show: true,
      position: 'right',
      legendStats: ['currentAndLastValue', 'average']
    }
  };

  await generateFixture(
    'pie-chart-legend-stats.json',
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChartLegendStats, import.meta.url);
