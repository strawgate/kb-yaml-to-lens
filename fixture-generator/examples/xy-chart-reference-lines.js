#!/usr/bin/env node
/**
 * Example: Generate an XY chart with reference lines
 *
 * Demonstrates creating a time series line chart with static reference lines
 * for SLA thresholds and targets.
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateXYChartWithReferenceLines() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'xy',
    title: 'Events Over Time with SLA Thresholds',
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
      },
      {
        type: 'reference',
        yAxis: [
          {
            value: '500',
            seriesColor: '#FF0000',
            lineThickness: 2,
            fill: 'none'
          },
          {
            value: '200',
            seriesColor: '#00FF00',
            fill: 'none'
          }
        ]
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

  const outputPath = path.join(outputDir, 'xy-chart-reference-lines.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: xy-chart-reference-lines.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateXYChartWithReferenceLines()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
