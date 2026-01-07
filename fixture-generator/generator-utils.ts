/**
 * Shared utility functions for fixture generators
 *
 * This module provides common functionality to reduce boilerplate across
 * all fixture generator scripts.
 */

import type { LensConfig, LensConfigOptions } from '@kbn/lens-embeddable-utils/config_builder';
import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from './dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

/**
 * Generate a Lens fixture from a configuration object
 *
 * @param outputFilename - Name of the output JSON file (e.g., 'gauge.json')
 * @param config - Lens configuration object
 * @param options - Builder options (timeRange, etc.)
 * @param callerFilePath - The __filename of the calling module (import.meta.url)
 * @returns Promise that resolves when fixture is written
 */
export async function generateFixture(
  outputFilename: string,
  config: LensConfig,
  options: LensConfigOptions = {},
  callerFilePath: string
): Promise<void> {
  // Validate outputFilename
  if (!outputFilename || typeof outputFilename !== 'string') {
    throw new Error('outputFilename must be a non-empty string');
  }
  if (outputFilename.includes('..') || outputFilename.includes('\0') || path.isAbsolute(outputFilename)) {
    throw new Error(`Invalid outputFilename: ${outputFilename}`);
  }

  // Initialize the builder with mock DataViews service
  const mockDataViews = createDataViewsMock();
  const builder = new LensConfigBuilder(mockDataViews);

  try {
    // Build the Lens attributes
    const lensAttributes = await builder.build(config, options);

    // Determine output directory relative to caller
    // Use version-specific subdirectory if KIBANA_VERSION is set
    const callerDir = path.dirname(fileURLToPath(callerFilePath));
    const kibanaVersion = process.env.KIBANA_VERSION || 'v9.2.0';
    const outputDir = path.join(callerDir, '..', 'output', kibanaVersion);

    // Ensure output directory exists
    fs.mkdirSync(outputDir, { recursive: true });

    // Write the fixture
    const outputPath = path.join(outputDir, outputFilename);
    fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

    console.log(`✓ Generated: ${outputFilename}`);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to generate ${outputFilename}: ${errorMessage}`);
  }
}

/**
 * Generate both ES|QL and Data View variants of a fixture
 *
 * @param baseName - Base name for output files (e.g., 'gauge')
 * @param esqlConfig - ES|QL configuration object
 * @param dataviewConfig - Data View configuration object
 * @param options - Builder options (timeRange, etc.)
 * @param callerFilePath - The __filename of the calling module (import.meta.url)
 * @returns Promise that resolves when both fixtures are written
 */
export async function generateDualFixture(
  baseName: string,
  esqlConfig: LensConfig,
  dataviewConfig: LensConfig,
  options: LensConfigOptions = {},
  callerFilePath: string
): Promise<void> {
  const errors: string[] = [];

  // Generate ES|QL variant
  try {
    await generateFixture(`${baseName}-esql.json`, esqlConfig, options, callerFilePath);
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    errors.push(`ES|QL variant: ${errorMessage}`);
  }

  // Generate Data View variant
  try {
    await generateFixture(`${baseName}-dataview.json`, dataviewConfig, options, callerFilePath);
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    errors.push(`Data View variant: ${errorMessage}`);
  }

  if (errors.length > 0) {
    throw new Error(`Failed to generate ${baseName}: ${errors.join('; ')}`);
  }
}

/**
 * Wrapper to run a generator function if the script is executed directly
 *
 * @param generatorFn - Async function to execute
 * @param callerFilePath - The import.meta.url of the calling module
 */
export function runIfMain(generatorFn: () => Promise<void>, callerFilePath: string): void {
  if (fileURLToPath(callerFilePath) === process.argv[1]) {
    const scriptName = path.basename(fileURLToPath(callerFilePath));
    generatorFn()
      .catch((err) => {
        console.error(`Failed to generate fixture in ${scriptName}:`, err);
        process.exit(1);
      });
  }
}
