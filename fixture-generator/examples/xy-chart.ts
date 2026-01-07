#!/usr/bin/env node
/**
 * Example: Generate XY (line) chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a time series line chart
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChart(): Promise<void> {
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
    title: 'Events Over Time',
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
    ]
  };

  // Data View variant
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    ...sharedConfig,
    title: 'Events Over Time (Data View)',
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
    ]
  };

  await generateDualFixture(
    'xy-chart',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChart, import.meta.url);
