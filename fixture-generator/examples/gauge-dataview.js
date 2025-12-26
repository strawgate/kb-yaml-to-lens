#!/usr/bin/env node
/**
 * Example: Generate a gauge chart visualization (using data view)
 *
 * Demonstrates creating a gauge showing a single metric value with min/max ranges
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateGaugeDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'gauge',
    title: 'CPU Usage Gauge (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    metric: 'average(system.cpu.total.pct)',
    min: 0,
    max: 1,
    goal: 0.8,
    shape: 'arc',
    colorMode: 'palette'
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-15m', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'gauge-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: gauge-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateGaugeDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
