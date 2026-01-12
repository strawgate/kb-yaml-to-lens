#!/usr/bin/env node
/**
 * Example: Generate XY stacked bar chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a time series stacked bar chart with multiple series
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartBarStacked(): Promise<void> {
  // Shared configuration between both variants
  const sharedConfig: Partial<LensXYConfig> = {
    legend: {
      show: true,
      position: 'right'
    }
  };

  // ES|QL variant
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events by Status (Stacked Bar)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp, log.level'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar_stacked',
        xAxis: '@timestamp',
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

  // Data View variant
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events by Status (Stacked Bar, Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar_stacked',
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
    'xy-chart-bar-stacked',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartBarStacked, import.meta.url);
