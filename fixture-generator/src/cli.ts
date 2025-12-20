#!/usr/bin/env node
/**
 * Main CLI entry point for fixture generator
 *
 * This script runs all dashboard generators to create test fixtures
 */

import * as path from 'path';
import * as fs from 'fs';

async function main() {
  console.log('Kibana Dashboard Fixture Generator');
  console.log('===================================\n');

  const dashboardsDir = path.join(__dirname, 'dashboards');

  // Check if dashboards directory exists
  if (!fs.existsSync(dashboardsDir)) {
    console.error('Error: dashboards directory not found');
    process.exit(1);
  }

  // Find all dashboard generator files
  const files = fs.readdirSync(dashboardsDir)
    .filter(f => f.endsWith('.js') && f.includes('-examples'));

  if (files.length === 0) {
    console.log('No dashboard generators found in src/dashboards/');
    console.log('Create files like metric-examples.ts to define dashboard fixtures');
    return;
  }

  console.log(`Found ${files.length} generator(s):\n`);

  // Run each generator
  for (const file of files) {
    const filePath = path.join(dashboardsDir, file);
    console.log(`Running: ${file}`);

    try {
      // Dynamic import and execute
      await import(filePath);
    } catch (err) {
      console.error(`  ✗ Failed: ${err.message}`);
      if (process.env.DEBUG) {
        console.error(err.stack);
      }
    }
  }

  console.log('\n✓ Fixture generation complete');
  console.log(`Output directory: ${process.env.OUTPUT_DIR || '/tool/output'}`);
}

// Run if executed directly
if (require.main === module) {
  main().catch((err) => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}
