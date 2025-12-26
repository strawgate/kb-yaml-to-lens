#!/usr/bin/env node
/**
 * Example: Generate a gauge chart visualization
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

export async function generateGauge() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'gauge',
    title: 'CPU Usage Gauge',
    dataset: {
      esql: 'FROM metrics-* | STATS avg_cpu = AVG(system.cpu.total.pct)'
    },
    metric: 'avg_cpu',
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

  const outputPath = path.join(outputDir, 'gauge.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: gauge.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateGauge()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
