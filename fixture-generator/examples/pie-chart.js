#!/usr/bin/env node
/**
 * Example: Generate a pie chart visualization
 *
 * Demonstrates creating a pie chart with slices
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generatePieChart() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'pie',
    title: 'Events by Status',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY log.level | SORT count DESC | LIMIT 10'
    },
    value: 'count',
    breakdown: 'log.level',
    legend: {
      show: true,
      position: 'right'
    }
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'pie-chart.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: pie-chart.json');
}

if (require.main === module) {
  generatePieChart()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generatePieChart };
