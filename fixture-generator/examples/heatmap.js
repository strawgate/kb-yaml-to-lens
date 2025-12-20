#!/usr/bin/env node
/**
 * Example: Generate a heatmap visualization using Kibana's LensConfigBuilder
 *
 * This script demonstrates how to create a heatmap showing geographic traffic patterns
 * with data aggregated by source and destination countries.
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmap() {
  // Initialize the builder
  const builder = new LensConfigBuilder();

  // Define heatmap configuration
  // Based on: https://github.com/elastic/kibana/blob/main/dev_docs/lens/heatmap.mdx
  const config = {
    chartType: 'heatmap',
    title: 'Traffic Heatmap by Geographic Location',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS bytes = SUM(bytes) BY geo.dest, geo.src'
    },
    breakdown: 'geo.dest',  // Y-axis: destination country
    xAxis: 'geo.src',       // X-axis: source country
    value: 'bytes',         // Metric: total bytes transferred
    legend: {
      show: true,
      position: 'right'
    }
  };

  // Build the Lens attributes
  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  // Write to output directory
  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'heatmap.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap.json');
}

// Run if executed directly
if (require.main === module) {
  generateHeatmap()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmap };
