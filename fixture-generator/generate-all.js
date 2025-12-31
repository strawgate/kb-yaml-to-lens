#!/usr/bin/env node
/**
 * Generate all test fixtures
 *
 * Automatically discovers and runs all example generator scripts in the examples/ directory
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readdir } from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Discover all example generator files in the examples/ directory
 */
async function discoverExamples() {
  const examplesDir = join(__dirname, 'examples');
  const files = await readdir(examplesDir);

  const exampleFiles = files
    .filter(file => file.endsWith('.js'))
    .sort();

  return exampleFiles;
}

/**
 * Load generator function from an example file
 */
async function loadGenerator(filename) {
  const modulePath = `./examples/${filename}`;
  const module = await import(modulePath);

  // Find the exported generator function (should start with 'generate')
  const generatorName = Object.keys(module).find(key => key.startsWith('generate'));

  if (!generatorName) {
    throw new Error(`No generator function found in ${filename}`);
  }

  return {
    fn: module[generatorName],
    name: generatorName,
    filename
  };
}

/**
 * Format a generator name for display
 */
function formatName(generatorName) {
  // Convert generateMetricBasic -> Metric (Basic)
  // Convert generateXYChartStackedBar -> XY Chart (Stacked Bar)
  return generatorName
    .replace(/^generate/, '')
    .replace(/([A-Z])/g, ' $1')
    .trim()
    .replace(/^(\w+)(.*)/, (_, first, rest) => {
      const formatted = first + rest;
      const parts = formatted.split(' ');
      if (parts.length > 1) {
        return `${parts[0]} (${parts.slice(1).join(' ')})`;
      }
      return formatted;
    });
}

async function generateAll() {
  console.log('Generating all test fixtures...\n');
  console.log('Discovering example generators...');

  const exampleFiles = await discoverExamples();
  console.log(`Found ${exampleFiles.length} example files\n`);

  for (const filename of exampleFiles) {
    try {
      const { fn, name } = await loadGenerator(filename);
      const displayName = formatName(name);

      await fn();

      // Check if the generator produced both variants by looking at its name or behavior
      // For now, we'll just log the successful generation
      console.log(`✓ Generated ${displayName}`);
    } catch (err) {
      console.error(`✗ Failed to generate ${filename}:`, err.message);
      process.exit(1);
    }
  }

  const kibanaVersion = process.env.KIBANA_VERSION || 'v9.2.0';
  console.log('\n✓ All fixtures generated successfully');
  console.log(`  Output directory: ./output/${kibanaVersion}/`);
}

if (fileURLToPath(import.meta.url) === process.argv[1]) {
  generateAll()
    .catch((err) => {
      console.error('Fatal error:', err);
      process.exit(1);
    });
}

export { generateAll };
