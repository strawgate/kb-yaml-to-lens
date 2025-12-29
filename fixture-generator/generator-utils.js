/**
 * Shared utility functions for fixture generators
 *
 * This module provides common functionality to reduce boilerplate across
 * all fixture generator scripts.
 */

import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder';
import { createDataViewsMock } from './dataviews-mock.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

/**
 * Generate a Lens fixture from a configuration object
 *
 * @param {string} outputFilename - Name of the output JSON file (e.g., 'gauge.json')
 * @param {Object} config - Lens configuration object
 * @param {Object} options - Builder options (timeRange, etc.)
 * @param {string} callerFilePath - The __filename of the calling module (import.meta.url)
 * @returns {Promise<void>}
 */
export async function generateFixture(outputFilename, config, options = {}, callerFilePath) {
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
    const callerDir = path.dirname(fileURLToPath(callerFilePath));
    const outputDir = path.join(callerDir, '..', 'output');

    // Ensure output directory exists
    fs.mkdirSync(outputDir, { recursive: true });

    // Write the fixture
    const outputPath = path.join(outputDir, outputFilename);
    fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

    console.log(`✓ Generated: ${outputFilename}`);
  } catch (error) {
    throw new Error(`Failed to generate ${outputFilename}: ${error.message}`);
  }
}

/**
 * Generate both ES|QL and Data View variants of a fixture
 *
 * @param {string} baseName - Base name for output files (e.g., 'gauge')
 * @param {Object} esqlConfig - ES|QL configuration object
 * @param {Object} dataviewConfig - Data View configuration object
 * @param {Object} options - Builder options (timeRange, etc.)
 * @param {string} callerFilePath - The __filename of the calling module (import.meta.url)
 * @returns {Promise<void>}
 */
export async function generateDualFixture(baseName, esqlConfig, dataviewConfig, options = {}, callerFilePath) {
  const errors = [];

  // Generate ES|QL variant
  try {
    await generateFixture(`${baseName}.json`, esqlConfig, options, callerFilePath);
  } catch (err) {
    errors.push(`ES|QL variant: ${err.message}`);
  }

  // Generate Data View variant
  try {
    await generateFixture(`${baseName}-dataview.json`, dataviewConfig, options, callerFilePath);
  } catch (err) {
    errors.push(`Data View variant: ${err.message}`);
  }

  if (errors.length > 0) {
    throw new Error(`Failed to generate ${baseName}: ${errors.join('; ')}`);
  }
}

/**
 * Wrapper to run a generator function if the script is executed directly
 *
 * @param {Function} generatorFn - Async function to execute
 * @param {string} callerFilePath - The import.meta.url of the calling module
 */
export function runIfMain(generatorFn, callerFilePath) {
  if (fileURLToPath(callerFilePath) === process.argv[1]) {
    const scriptName = path.basename(fileURLToPath(callerFilePath));
    generatorFn()
      .catch((err) => {
        console.error(`Failed to generate fixture in ${scriptName}:`, err);
        process.exit(1);
      });
  }
}
