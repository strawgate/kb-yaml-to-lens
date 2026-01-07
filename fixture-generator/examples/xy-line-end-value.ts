#!/usr/bin/env node
/**
 * Test fixture: End value handling for line charts
 *
 * Tests: None, Zero, Nearest
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateLineEndValue(): Promise<void> {
  // ES|QL variant - testing Zero end value
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Line Chart - End Value Zero',
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
    endValue: 'Zero'
  };

  // Data View variant - testing Nearest end value
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Line Chart - End Value Nearest (Data View)',
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
    endValue: 'Nearest'
  };

  await generateDualFixture(
    'xy-line-end-value',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateLineEndValue, import.meta.url);
