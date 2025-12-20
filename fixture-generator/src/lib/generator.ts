/**
 * Helper library for generating Kibana dashboard fixtures
 *
 * This module provides utilities to:
 * 1. Use Kibana's LensConfigBuilder API
 * 2. Export generated dashboards as JSON fixtures
 * 3. Write fixtures to the output directory
 */

import * as fs from 'fs';
import * as path from 'path';

const OUTPUT_DIR = process.env.OUTPUT_DIR || '/tool/output';

/**
 * Generate a fixture and write it to the output directory
 *
 * @param filename - Output filename (e.g., 'metric-basic.json')
 * @param data - Dashboard/visualization configuration object
 */
export async function generateFixture(filename: string, data: any): Promise<void> {
  const outputPath = path.join(OUTPUT_DIR, filename);

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Write JSON with pretty formatting
  fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));

  console.log(`✓ Generated: ${filename}`);
}

/**
 * Generate multiple fixtures from an object of name -> config mappings
 *
 * @param fixtures - Object mapping filenames to configuration data
 */
export async function generateFixtures(fixtures: Record<string, any>): Promise<void> {
  for (const [filename, data] of Object.entries(fixtures)) {
    await generateFixture(filename, data);
  }
}

/**
 * Helper to create a standard data view reference
 */
export function createDataViewReference(dataViewId: string, layerId: string) {
  return {
    type: 'index-pattern',
    id: dataViewId,
    name: `indexpattern-datasource-layer-${layerId}`,
  };
}
