#!/usr/bin/env node
/**
 * Example: Generate a metric with breakdown visualization
 *
 * Demonstrates creating a metric that breaks down by a field
 */

const { LensConfigBuilder } = require('@kbn/lens-embeddable-utils/config_builder');
const fs = require('fs');
const path = require('path');

async function generateMetricWithBreakdown() {
  const builder = new LensConfigBuilder();

  const config = {
    chartType: 'metric',
    title: 'Count by Agent',
    dataset: {
      esql: 'FROM logs-* | STATS count = COUNT() BY agent.name | SORT count DESC | LIMIT 5'
    },
    value: 'count',
    breakdown: 'agent.name',
    label: 'Events per Agent'
  };

  const lensAttributes = await builder.build(config, {
    timeRange: { from: 'now-24h', to: 'now', type: 'relative' }
  });

  const outputDir = path.join(__dirname, '..', 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, 'metric-with-breakdown.json');
  fs.writeFileSync(outputPath, JSON.stringify(lensAttributes, null, 2));

  console.log('✓ Generated: metric-with-breakdown.json');
}

if (require.main === module) {
  generateMetricWithBreakdown()
    .catch((err) => {
      console.error('Failed to generate fixture:', err);
      process.exit(1);
    });
}

module.exports = { generateMetricWithBreakdown };
