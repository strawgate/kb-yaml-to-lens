#!/usr/bin/env node
/**
 * Example: Generate an XY chart with multiple layers (using data view)
 *
 * Demonstrates creating a chart with bar and line layers combined
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateXYChartMultiLayerDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'xy',
    title: 'Events with Success Rate Overlay (Data View)',
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
            label: 'Total Events',
            value: 'count()'
          }
        ]
      },
      {
        type: 'series',
        seriesType: 'line',
        xAxis: {
          type: 'dateHistogram',
          field: '@timestamp'
        },
        yAxis: [
          {
            label: 'Avg Bytes',
            value: 'average(bytes)'
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
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'xy-chart-multi-layer-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: xy-chart-multi-layer-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateXYChartMultiLayerDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
