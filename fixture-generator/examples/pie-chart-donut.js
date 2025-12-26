#!/usr/bin/env node
/**
 * Example: Generate a donut chart with labels
 *
 * Demonstrates creating a pie chart in donut mode with various label configurations
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generatePieChartDonut() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'pie',
    title: 'Response Codes Distribution (Donut)',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY response.keyword'
    },
    breakdown: 'response.keyword',
    metric: 'count',
    shape: 'donut',
    labels: {
      show: true,
      position: 'inside',
      percentDecimals: 1
    },
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

  const outputPath = path.join(outputDir, 'pie-chart-donut.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: pie-chart-donut.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generatePieChartDonut()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
