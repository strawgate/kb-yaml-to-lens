#!/usr/bin/env node
/**
 * Example: Generate pie chart with advanced color palette (both ES|QL and Data View)
 *
 * Demonstrates custom color mapping for pie/donut charts
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generatePieChartAdvancedColors() {
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
  const esqlConfig = {
    chartType: 'pie',
    title: 'Request Methods with Custom Palette',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY request.method'
    },
    value: 'count',
    breakdown: ['request.method'],
    shape: 'donut',
    palette: customPalette,
    labels: {
      show: true,
      position: 'inside',
      values: true,
      percentDecimals: 2
    },
    legend: {
      show: true,
      position: 'bottom',
      legendSize: 'medium'
    }
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'pie',
    title: 'Request Methods with Custom Palette (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    breakdown: ['request.method'],
    shape: 'donut',
    palette: customPalette,
    labels: {
      show: true,
      position: 'inside',
      values: true,
      percentDecimals: 2
    },
    legend: {
      show: true,
      position: 'bottom',
      legendSize: 'medium'
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
