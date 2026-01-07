#!/usr/bin/env node
/**
 * Example: Generate pie chart with advanced color palette (both ES|QL and Data View)
 *
 * Demonstrates custom color mapping for pie/donut charts
 */

import type { LensPieConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartAdvancedColors(): Promise<void> {
  // Shared palette configuration
  const customPalette = {
    type: 'palette',
    name: 'custom',
    params: {
      colors: ['#E7664C', '#57C17B', '#6F87D8', '#F9D66A', '#DA8B45', '#AA6556'],
      gradient: false,
      stops: [],
      rangeType: 'number'
    }
  };

  // ES|QL variant
  const esqlConfig: LensPieConfig = {
    chartType: 'donut',
    title: 'Request Methods with Custom Palette',
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
    title: 'Request Methods with Custom Palette (Data View)',
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
