#!/usr/bin/env node
/**
 * Example: Generate a stacked bar chart (using data view)
 *
 * Demonstrates creating a vertical stacked bar chart with multiple series
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartStackedBarDataview() {
  const config = {
    chartType: 'xy',
    title: 'Stacked Events by Response Code (Data View)',
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
        ],
        breakdown: 'response.keyword',
        seriesOptions: {
          stacked: 'normal'
        }
      }
    ],
    legend: {
      show: true,
      position: 'right'
    }
  };

  await generateFixture(
    'xy-chart-stacked-bar-dataview.json',
    config,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartStackedBarDataview, import.meta.url);
