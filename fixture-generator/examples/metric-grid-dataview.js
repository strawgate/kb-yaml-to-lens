#!/usr/bin/env node
/**
 * Example: Generate a metric grid layout (using data view)
 *
 * Demonstrates creating multiple metrics in a grid layout using a data view
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateMetricGridDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'metric',
    title: 'System Metrics Grid (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    metrics: [
      { label: 'Total Events', value: 'count()' },
      { label: 'Avg Bytes', value: 'average(bytes)' },
      { label: 'Max Price', value: 'max(price)' }
    ],
    maxCols: 3
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-15m', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'metric-grid-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: metric-grid-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateMetricGridDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
