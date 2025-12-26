#!/usr/bin/env node
/**
 * Example: Generate an advanced datatable visualization (using data view)
 *
 * Demonstrates creating a table with multiple rows, sorting, and formatting
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from '../dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function generateDatatableAdvancedDataview() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'datatable',
    title: 'Top Agents by System Load (Data View)',
    dataset: {
      index: 'metrics-*'
    },
    columns: [
      {
        columnId: 'agent.name',
        width: 200
      },
      {
        columnId: 'agent.id',
        width: 150
      },
      {
        columnId: 'median_load',
        width: 120,
        value: 'median(beat.stats.system.load.1)'
      }
    ],
    sortingColumnId: 'median_load',
    sortingDirection: 'desc'
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'datatable-advanced-dataview.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: datatable-advanced-dataview.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateDatatableAdvancedDataview()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
