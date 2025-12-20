#!/usr/bin/env node
/**
 * Example: Generate a basic metric visualization using Kibana's LensConfigBuilder
 *
 * This script demonstrates how to use Kibana's config builder API to create
 * a simple count metric and export it as JSON for testing.
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateMetricBasic() {
  // Initialize the builder (dataViews API is available in Kibana context)
  const builder = new LensConfigBuilder();

  // Define a basic metric configuration
  const config = {
    chartType: 'metric',
    title: 'Basic Count Metric',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT()'
    },
    value: 'count',
    label: 'Total Events'
  };

  // Build the Lens attributes
  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  // Write to output directory
  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'metric-basic.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: metric-basic.json');
}

// Run if executed directly
if (require.main === module) {
  generateMetricBasic()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateMetricBasic };
