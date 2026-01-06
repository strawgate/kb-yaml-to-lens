#!/usr/bin/env node
/**
 * Test fixture: All fitting function options for line charts
 *
 * Tests: None, Linear, Carry, Lookahead, Average, Nearest
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateLineFittingFunctions() {
  // ES|QL variant - testing Linear fitting
  const esqlConfig = {
    chartType: 'xy',
    title: 'Line Chart - Linear Fitting',
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
    fittingFunction: 'Linear',
    emphasizeFitting: true
  };

  // Data View variant - testing Average fitting
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Line Chart - Average Fitting (Data View)',
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
    emphasizeFitting: true
  };

  await generateDualFixture(
    'xy-line-fitting-functions',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateLineFittingFunctions, import.meta.url);
