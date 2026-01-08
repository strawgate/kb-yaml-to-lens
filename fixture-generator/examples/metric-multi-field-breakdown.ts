#!/usr/bin/env node
/**
 * Example: Generate Metric chart with multi-field breakdown (Data View only)
 *
 * Demonstrates the compiled structure for metric charts with multi-field breakdown.
 * Note: Kibana's Metric visualization only supports ONE breakdown field,
 * so even when breakdown specifies multiple fields, only the first is used.
 *
 * This validates that the compiler correctly:
 * 1. Accepts multiple fields in breakdown
 * 2. Uses only the first field for metric charts
 * 3. Generates the correct single breakdownByAccessor (not an array)
 *
 * Expected compiler output structure:
 * - Single column with ID ending in _breakdown (not _breakdown_0)
 * - visualization.breakdownByAccessor: string (not an array)
 */

import { runIfMain } from '../generator-utils.js';

export async function generateMetricMultiFieldBreakdown(): Promise<void> {
  // This fixture validates the compiled structure when the compiler receives:
  // breakdown:
  //   operation: terms
  //   fields:
  //     - product.category
  //     - customer.region  # This should be IGNORED for metric charts
  //   size: 10

  const compiledStructure = {
    title: 'Metric with Multi-Field breakdown_by (Validation Fixture)',
    visualizationType: 'lnsMetric',
    references: [
      {
        type: 'index-pattern',
        id: 'logs-*',
        name: 'indexpattern-datasource-layer-layer_0'
      }
    ],
    state: {
      datasourceStates: {
        formBased: {
          layers: {
            layer_0: {
              columnOrder: [
                'breakdown_accessor',
                'metric_count'
              ],
              columns: {
                breakdown_accessor: {
                  label: 'Top 10 values of product.category',
                  dataType: 'string',
                  operationType: 'terms',
                  scale: 'ordinal',
                  sourceField: 'product.category',  // Only first field used
                  isBucketed: true,
                  params: {
                    size: 10,
                    orderBy: {
                      type: 'alphabetical',
                      fallback: false
                    },
                    orderDirection: 'asc',
                    otherBucket: false,
                    missingBucket: false,
                    parentFormat: {
                      id: 'terms'
                    },
                    include: [],
                    exclude: [],
                    includeIsRegex: false,
                    excludeIsRegex: false
                  }
                },
                metric_count: {
                  operationType: 'formula',
                  isBucketed: false,
                  dataType: 'number',
                  references: [],
                  label: 'Count',
                  params: {
                    formula: 'count()'
                  },
                  customLabel: true
                }
              }
            }
          }
        }
      },
      internalReferences: [],
      filters: [],
      query: {
        language: 'kuery',
        query: ''
      },
      visualization: {
        layerId: 'layer_0',
        layerType: 'data',
        metricAccessor: 'metric_count',
        showBar: false,
        // KEY: Metric charts use singular breakdownByAccessor (not an array)
        breakdownByAccessor: 'breakdown_accessor'
      },
      adHocDataViews: {
        'logs-*': {}
      }
    }
  };

  // Write the fixture directly
  const fs = await import('fs');
  const path = await import('path');
  const { fileURLToPath } = await import('url');

  const callerDir = path.dirname(fileURLToPath(import.meta.url));
  const kibanaVersion = process.env.KIBANA_VERSION || 'v9.2.0';
  const outputDir = path.join(callerDir, '..', 'output', kibanaVersion);

  fs.mkdirSync(outputDir, { recursive: true });

  const outputPath = path.join(outputDir, 'metric-multi-field-breakdown-validation.json');
  fs.writeFileSync(outputPath, JSON.stringify(compiledStructure, null, 2));

  console.log('✓ Generated: metric-multi-field-breakdown-validation.json');
}

runIfMain(generateMetricMultiFieldBreakdown, import.meta.url);
