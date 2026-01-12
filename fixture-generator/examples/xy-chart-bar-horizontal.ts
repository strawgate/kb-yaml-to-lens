#!/usr/bin/env node
/**
 * Example: Generate XY horizontal bar chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a horizontal bar chart with categorical breakdown
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartBarHorizontal(): Promise<void> {
  const sharedConfig: Partial<LensXYConfig> = {
    legend: {
      show: true,
      position: 'right'
    }
  };

  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events by Log Level (Horizontal Bar)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar_horizontal',
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
    title: 'Events by Log Level (Horizontal Bar, Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar_horizontal',
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
    'xy-chart-bar-horizontal',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartBarHorizontal, import.meta.url);
