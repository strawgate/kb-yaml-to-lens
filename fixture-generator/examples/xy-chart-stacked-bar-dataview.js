#!/usr/bin/env node
/**
 * Example: Generate a stacked bar chart (using data view)
 *
 * Demonstrates creating a vertical stacked bar chart with multiple series
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateXYChartStackedBarDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

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

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'xy-chart-stacked-bar-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: xy-chart-stacked-bar-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateXYChartStackedBarDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
