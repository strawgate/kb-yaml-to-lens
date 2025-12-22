#!/usr/bin/env node
/**
 * Example: Generate a basic metric visualization using Kibana's LensConfigBuilder
 *
 * This script demonstrates how to use Kibana's config builder API to create
 * a simple count metric and export it as JSON for testing.
 */

const { LensAttributesBuilder, MetricChart, MetricLayer, FormulaColumn } = require('@kbn/lens-embeddable-utils');
const fs = require('fs');
const path = require('path');

async function generateMetricBasic() {
  // Create a metric layer with a formula column for count
  const layer = new MetricLayer({
    options: {},
    columns: [
      new FormulaColumn({
        value: 'count()',
        label: 'Total Events'
      })
    ]
  });

  // Create a metric chart
  const chart = new MetricChart({
    title: 'Basic Count Metric',
    layers: [layer]
  });

  // Build the Lens attributes
  const builder = new LensAttributesBuilder({ visualization: chart });
  const lensAttributes = builder.build();

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
