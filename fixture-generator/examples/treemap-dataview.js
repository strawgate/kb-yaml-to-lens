#!/usr/bin/env node
/**
 * Example: Generate a treemap visualization (using data view)
 *
 * Demonstrates creating a hierarchical treemap showing nested breakdowns
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateTreemapDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'treemap',
    title: 'Traffic by Source and Destination (Data View)',
    dataset: {
      index: 'logs-*'
    },
    primaryGroup: 'geo.src',
    secondaryGroup: 'geo.dest',
    metric: 'sum(bytes)',
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

  const outputPath = path.join(outputDir, 'treemap-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: treemap-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateTreemapDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
