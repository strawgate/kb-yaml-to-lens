#!/usr/bin/env node
/**
 * Example: Generate an XY (line) chart visualization
 *
 * Demonstrates creating a time series line chart
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateXYChart() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'xy',
    title: 'Events Over Time',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY @timestamp'
    },
    value: 'count',
    xAxis: '@timestamp',
    legend: {
      show: true,
      position: 'right'
    }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-7d', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'xy-chart.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: xy-chart.json');
}

if (require.main === module) {
  generateXYChart()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateXYChart };
