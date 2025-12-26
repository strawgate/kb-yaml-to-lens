#!/usr/bin/env node
/**
 * Example: Generate an advanced datatable visualization
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

export async function generateDatatableAdvanced() {
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  const config = {
    chartType: 'datatable',
    title: 'Top Agents by System Load',
    dataset: {
      esql: 'FROM metrics-* | STATS median_load = MEDIAN(beat.stats.system.load.1) BY agent.name, agent.id | SORT median_load DESC | LIMIT 100'
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
        width: 120
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

  const outputPath = path.join(outputDir, 'datatable-advanced.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: datatable-advanced.json');
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateDatatableAdvanced()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}
