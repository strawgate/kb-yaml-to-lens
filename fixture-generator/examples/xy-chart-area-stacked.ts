#!/usr/bin/env node
/**
 * Example: Generate XY stacked area chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a time series stacked area chart with multiple series
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartAreaStacked(): Promise<void> {
  const sharedConfig: Partial<LensXYConfig> = {
    legend: {
      show: true,
      position: 'right'
    }
  };

  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events by Status (Stacked Area)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY timestamp_bucket = BUCKET(@timestamp, 1 hour), log.level'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'area_stacked',
        xAxis: 'timestamp_bucket',
        breakdown: 'log.level',
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
    title: 'Events by Status (Stacked Area, Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'area_stacked',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        breakdown: 'log.level',
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
    'xy-chart-area-stacked',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartAreaStacked, import.meta.url);
