#!/usr/bin/env node
/**
 * Example: Generate XY bar chart with value labels (both ES|QL and Data View)
 *
 * Demonstrates creating a bar chart with value labels displayed on bars
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartValueLabels(): Promise<void> {
  const sharedConfig: Partial<LensXYConfig> = {
    legend: {
      show: true,
      position: 'right'
    },
    valueLabels: 'show'
  };

  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events with Value Labels',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: 'log.level',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ]
      }
    ]
  };

  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events with Value Labels (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: 'log.level',
        yAxis: [
          {
            label: 'Count',
            value: 'count()'
          }
        ]
      }
    ]
  };

  await generateDualFixture(
    'xy-chart-value-labels',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartValueLabels, import.meta.url);
