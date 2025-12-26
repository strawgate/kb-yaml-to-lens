#!/usr/bin/env node
/**
 * Example: Generate a donut chart visualization (using data view)
 *
 * Demonstrates creating a pie chart with donut display and label configuration
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generatePieChartDonutDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'pie',
    title: 'Log Level Distribution (Donut - Data View)',
    dataset: {
      index: 'logs-*'
    },
    breakdown: 'log.level',
    metric: 'count()',
    shape: 'donut',
    labels: {
      show: true,
      position: 'inside',
      values: true,
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

  const outputPath = path.join(outputDir, 'pie-chart-donut-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: pie-chart-donut-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generatePieChartDonutDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
