#!/usr/bin/env node
/**
 * Example: Generate a heatmap with custom palette configuration
 *
 * Demonstrates palette customization with different color schemes
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateHeatmapWithPalette() {
  const builder = new LensConfigBuilder();

  // Heatmap with custom palette configuration
  const config = {
    chartType: 'heatmap',
    title: 'Request Heatmap with Custom Palette',
    dataset: {
      esql: 'FROM kibana_sample_data_logs | STATS requests = COUNT() BY geo.dest, machine.os.keyword'
    },
    breakdown: 'geo.dest',      // Y-axis: destination country
    xAxis: 'machine.os.keyword', // X-axis: operating system
    value: 'requests',           // Metric: request count
    legend: {
      show: true,
      position: 'bottom'
    }
    // Note: LensConfigBuilder may have palette configuration options
    // that can be explored in the Kibana docs
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-30d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'heatmap-with-palette.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: heatmap-with-palette.json');
}

if (require.main === module) {
  generateHeatmapWithPalette()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateHeatmapWithPalette };
