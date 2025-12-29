#!/usr/bin/env node
/**
 * Example: Generate XY chart with advanced legend configuration (both ES|QL and Data View)
 *
 * Demonstrates various legend options: positioning, sizing, scrolling, and labels
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartAdvancedLegend() {
  // ES|QL variant
  const esqlConfig = {
    chartType: 'xy',
    title: 'Events by Response Code (Advanced Legend)',
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
      position: 'top',
      maxLines: 3,
      shouldTruncate: true,
      legendSize: 'large',
      showSingleSeries: false
    }
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Events by Response Code (Advanced Legend - Data View)',
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
      position: 'top',
      maxLines: 3,
      shouldTruncate: true,
      legendSize: 'large',
      showSingleSeries: false
    }
  };

  await generateDualFixture(
    'xy-chart-advanced-legend',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateXYChartAdvancedLegend, import.meta.url);
