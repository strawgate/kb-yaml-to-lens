#!/usr/bin/env node
/**
 * Example: Generate pie chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a pie chart with slices
 */

import type { LensPieConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChart(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensPieConfig> = {
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig: LensPieConfig = {
    chartType: 'pie',
    ...sharedConfig,
    title: 'Events by Status',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'
    },
    value: 'count',
    breakdown: ['log.level']
  };

  // Data View variant
  const dataviewConfig: LensPieConfig = {
    chartType: 'pie',
    ...sharedConfig,
    title: 'Events by Status (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: ['log.level']
  };

  await generateDualFixture(
    'pie-chart',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChart, import.meta.url);
