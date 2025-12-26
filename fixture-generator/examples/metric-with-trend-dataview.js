#!/usr/bin/env node
/**
 * Example: Generate a metric with trend indicator (using data view)
 *
 * Demonstrates creating a metric showing trend arrow/change using a data view
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateMetricWithTrendDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'metric',
    title: 'Event Count with Trend (Data View)',
    dataset: {
      index: 'logs-*'
    },
    value: 'count()',
    label: 'Total Events',
    trendline: true,
    progressDirection: 'vertical'
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'metric-with-trend-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: metric-with-trend-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateMetricWithTrendDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
