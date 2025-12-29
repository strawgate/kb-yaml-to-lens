#!/usr/bin/env node
/**
 * Example: Generate stacked bar chart visualizations (both ES|QL and Data View)
 *
 * Demonstrates creating a vertical stacked bar chart with multiple series
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartStackedBar() {
  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Stacked Events by Response Code',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp, response.keyword'
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

  // Data View variant
  const dataviewConfig = {
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

  await generateDualFixture(
    'xy-chart-stacked-bar',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartStackedBar, import.meta.url);
