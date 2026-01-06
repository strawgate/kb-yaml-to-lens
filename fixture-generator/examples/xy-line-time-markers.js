#!/usr/bin/env node
/**
 * Test fixture: Time marker and endzone options
 *
 * Tests: showCurrentTimeMarker, hideEndzones
 */

import { generateDualFixture, runIfMain } from '../generator-utils.js';

export async function generateLineTimeMarkers() {
  // ES|QL variant - testing time markers
  const esqlConfig = {
    chartType: 'xy',
    title: 'Line Chart - With Time Marker',
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
    showCurrentTimeMarker: true,
    hideEndzones: true
  };

  // Data View variant
  const dataviewConfig = {
    chartType: 'xy',
    title: 'Line Chart - With Time Marker (Data View)',
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
    showCurrentTimeMarker: true,
    hideEndzones: true
  };

  await generateDualFixture(
    'xy-line-time-markers',
    esqlConfig,
    dataviewConfig,
    { timeRange: { from: 'now-7d', to: 'now', type: 'relative' } },
    import.meta.url
  );
}

runIfMain(generateLineTimeMarkers, import.meta.url);
