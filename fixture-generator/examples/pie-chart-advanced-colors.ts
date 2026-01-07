#!/usr/bin/env node
/**
 * Example: Generate donut chart with legend (both ES|QL and Data View)
 *
 * Demonstrates donut chart visualization with legend positioning
 */

import type { LensPieConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartAdvancedColors(): Promise<void> {
  // ES|QL variant
  const esqlConfig: LensPieConfig = {
    chartType: 'donut',
    title: 'Request Methods Distribution',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY request.method'
    },
    value: 'count',
    breakdown: ['request.method'],
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  // Data View variant
  const dataviewConfig: LensPieConfig = {
    chartType: 'donut',
    title: 'Request Methods Distribution (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    value: 'count()',
    breakdown: ['request.method'],
    legend: {
      show: true,
      position: 'bottom'
    }
  };

  await generateDualFixture(
    'pie-chart-advanced-colors',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-24h', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generatePieChartAdvancedColors, import.meta.url);
