#!/usr/bin/env node
/**
 * Test fixture: Minimum bar height for bar charts
 *
 * Tests: minBarHeight property
 */

import type { LensXYConfig } from '@kbn/lens-embeddable-utils/config_builder';
import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateBarMinHeight(): Promise<void> {
  // ES|QL variant
  const esqlConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Bar Chart - Min Bar Height 5px',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
        xAxis: '@timestamp',
        yAxis: [
          {
            label: 'Count',
            value: 'count'
          }
        ]
      }
    ],
    minBarHeight: 5
  };

  // Data View variant
  const dataviewConfig: LensXYConfig = {
    chartType: 'xy',
    title: 'Bar Chart - Min Bar Height 5px (Data View)',
    dataset: {
      index: 'logs-*',
      timeFieldName: '@timestamp'
    },
    layers: [
      {
        type: 'series',
        seriesType: 'bar',
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
    minBarHeight: 5
  };

  await generateDualFixture(
    'xy-bar-min-height',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateBarMinHeight, import.meta.url);
