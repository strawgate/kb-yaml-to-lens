#!/usr/bin/env node
/**
 * Test fixture: Fill opacity for area charts
 *
 * Tests: fillOpacity property
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateAreaFillOpacity() {
  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Area Chart - Fill Opacity 0.7',
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
    ],
    fillOpacity: 0.7
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Area Chart - Fill Opacity 0.7 (Data View)',
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
    ],
    fillOpacity: 0.7
  };

  await generateDualFixture(
    'xy-area-fill-opacity',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateAreaFillOpacity, import.meta.url);
