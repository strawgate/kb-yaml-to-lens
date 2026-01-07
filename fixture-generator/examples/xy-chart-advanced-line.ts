#!/usr/bin/env node
/**
 * Example: Generate line chart with advanced fitting options
 *
 * Demonstrates advanced line chart features:
 * - Fitting functions (Linear, Average, Carry, etc.)
 * - Emphasize fitting option
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartAdvancedLine(): Promise<void> {
  // ES|QL variant
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Advanced Line Chart with Fitting Functions',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ]
      }
    ],
    fittingFunction: 'Average',
    emphasizeFitting: true,
    legend: {
      show: true,
      position: 'right'
    }
  };

  // Data View variant
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Advanced Line Chart (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'line',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        yAxis: [
          {
            label: 'Count',
            value: 'count()'
          }
        ]
      }
    ],
    fittingFunction: 'Average',
    emphasizeFitting: true,
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateDualFixture(
    'xy-chart-advanced-line',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartAdvancedLine, import.meta.url);
