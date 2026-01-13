#!/usr/bin/env node
/**
 * Example: Generate XY area chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a time series area chart
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartArea(): Promise<void> {
  const sharedConfig: Partial<LensXYConfig> = {
    legend: {
      show: true,
      position: 'right'
    }
  };

  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events Over Time (Area)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'area',
        xAxis: '@timestamp',
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
    title: 'Events Over Time (Area, Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'area',
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
    ]
  };

  await generateDualFixture(
    'xy-chart-area',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartArea, import.meta.url);
