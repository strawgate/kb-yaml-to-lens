#!/usr/bin/env node

/**
 * CLI tool for Lens Fixture Generator
 * Generates Kibana Lens test fixtures from YAML configurations
 */

import { program } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import { YamlDashboardParser } from './parser/yaml-parser';

const VERSION = '1.0.0';

program
  .name('lens-fixture-generator')
  .description('Generate Kibana Lens test fixtures from YAML configuration')
  .version(VERSION);

// Generate command
program
  .command('generate')
  .description('Generate dashboard JSON from YAML')
  .argument('<input>', 'Input YAML file path')
  .option('-o, --output <path>', 'Output file path', './fixture.json')
  .option('--pretty', 'Pretty print JSON output', true)
  .option('--validate', 'Validate without generating', false)
  .action(async (input: string, options) => {
    try {
      const inputPath = path.resolve(input);

      if (!fs.existsSync(inputPath)) {
        console.error(`Error: Input file not found: ${inputPath}`);
        process.exit(1);
      }

      const parser = new YamlDashboardParser();

      if (options.validate) {
        console.log('Validating YAML configuration...');
        parser.parse(inputPath);
        console.log('✓ Configuration is valid');
        return;
      }

      console.log(`Generating fixture from: ${inputPath}`);
      const json = parser.parse(inputPath);

      const outputPath = path.resolve(options.output);
      const output = options.pretty
        ? JSON.stringify(JSON.parse(json), null, 2)
        : json;

      fs.writeFileSync(outputPath, output);
      console.log(`✓ Fixture generated: ${outputPath}`);
    } catch (error: any) {
      console.error(`Error: ${error.message}`);
      if (process.env.DEBUG) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  });

// Validate command
program
  .command('validate')
  .description('Validate YAML configuration')
  .argument('<input>', 'Input YAML file path')
  .action((input: string) => {
    try {
      const parser = new YamlDashboardParser();
      parser.parse(path.resolve(input));
      console.log('✓ Configuration is valid');
    } catch (error: any) {
      console.error(`✗ Validation failed: ${error.message}`);
      process.exit(1);
    }
  });

// Example command
program
  .command('example')
  .description('Generate example YAML configuration')
  .option('-o, --output <path>', 'Output file path', './example.yaml')
  .action((options) => {
    const example = getExampleYaml();
    fs.writeFileSync(options.output, example);
    console.log(`Example configuration written to: ${options.output}`);
  });

program.parse();

function getExampleYaml(): string {
  return `# Example Lens Fixture Configuration
version: "1.0"

settings:
  dataView: "logs-*"
  timeFrom: "now-24h"
  timeTo: "now"

dashboard:
  title: "Example Test Fixtures"
  description: "Generated using lens-fixture-generator"

panels:
  - type: metric
    title: "Total Requests"
    layout: quarter
    config:
      metric:
        operation: count
        label: "Total"
      trendLine: true

  - type: xy
    title: "Requests Over Time"
    layout: half
    config:
      seriesType: line
      xAxis:
        field: "@timestamp"
        type: date_histogram
        interval: auto
      yAxis:
        operation: count
        label: "Requests"

  - type: pie
    title: "Status Distribution"
    layout: quarter
    config:
      shape: donut
      sliceBy:
        - field: "response.status_code"
          size: 5
      metric:
        operation: count
`;
}
