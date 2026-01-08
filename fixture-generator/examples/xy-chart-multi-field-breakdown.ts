#!/usr/bin/env node
/**
 * Example: Generate XY chart with multi-field breakdown (Data View only)
 *
 * Demonstrates creating XY charts with multiple breakdown fields.
 * This validates the multi-field breakdown feature which supports 1-4 fields.
 *
 * Note: The LensConfigBuilder API doesn't expose multi-field breakdown directly
 * in the config interface. This example creates the compiled JSON structure
 * that the compiler should produce when breakdown has multiple fields.
 *
 * Expected compiler output structure:
 * - Multiple columns with IDs ending in _breakdown_0, _breakdown_1, etc.
 * - Each column has operationType: 'terms' with its own field
 * - visualization.layers[0].splitAccessors array contains all breakdown IDs
 */

import { generateFixture, runIfMain } from '../generator-utils.js';

export async function generateXYChartMultiFieldBreakdown(): Promise<void> {
  // This is a DATA VIEW ONLY example since ES|QL queries handle grouping differently
  // The compiler will generate this structure when given:
  // breakdown:
  //   operation: terms
  //   fields:
  //     - product.category
  //     - customer.region
  //   size: 10

  // We're creating the expected compiled JSON structure directly
  // to validate what the compiler should produce
  const compiledStructure = {
    title: 'XY Chart with Multi-Field Breakdown (Validation Fixture)',
    visualizationType: 'lnsXY',
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
                'x_date_histogram',
                'breakdown_0',
                'breakdown_1',
                'metric_count'
              ],
              columns: {
                x_date_histogram: {
                  label: '@timestamp',
                  dataType: 'date',
                  operationType: 'date_histogram',
                  sourceField: '@timestamp',
                  isBucketed: true,
                  scale: 'interval',
                  params: {
                    interval: 'auto',
                    includeEmptyRows: true,
                    dropPartials: false
                  }
                },
                breakdown_0: {
                  label: 'Top 10 values of product.category',
                  dataType: 'string',
                  operationType: 'terms',
                  scale: 'ordinal',
                  sourceField: 'product.category',
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
                breakdown_1: {
                  label: 'Top 10 values of customer.region',
                  dataType: 'string',
                  operationType: 'terms',
                  scale: 'ordinal',
                  sourceField: 'customer.region',
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
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  isBucketed: false,
                  scale: 'ratio',
                  sourceField: '___records___',
                  params: {
                    emptyAsNull: false
                  }
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
        legend: {
          isVisible: true,
          position: 'right'
        },
        valueLabels: 'hide',
        fittingFunction: 'None',
        yLeftScale: 'linear',
        axisTitlesVisibilitySettings: {
          x: true,
          yLeft: true,
          yRight: true
        },
        tickLabelsVisibilitySettings: {
          x: true,
          yLeft: true,
          yRight: true
        },
        labelsOrientation: {
          x: 0,
          yLeft: 0,
          yRight: 0
        },
        gridlinesVisibilitySettings: {
          x: true,
          yLeft: true,
          yRight: true
        },
        preferredSeriesType: 'bar',
        layers: [
          {
            layerId: 'layer_0',
            layerType: 'data',
            seriesType: 'bar',
            accessors: ['metric_count'],
            xAccessor: 'x_date_histogram',
            // KEY: This is what the compiler should generate for multi-field breakdown
            splitAccessors: ['breakdown_0', 'breakdown_1']
          }
        ]
      },
      adHocDataViews: {
        'logs-*': {}
      }
    }
  };

  // Write the fixture directly (not using LensConfigBuilder since it doesn't support this)
  const fs = await import('fs');
  const path = await import('path');
  const { fileURLToPath } = await import('url');

  const callerDir = path.dirname(fileURLToPath(import.meta.url));
  const kibanaVersion = process.env.KIBANA_VERSION || 'v9.2.0';
  const outputDir = path.join(callerDir, '..', 'output', kibanaVersion);

  fs.mkdirSync(outputDir, { recursive: true });

  const outputPath = path.join(outputDir, 'xy-chart-multi-field-breakdown-validation.json');
  fs.writeFileSync(outputPath, JSON.stringify(compiledStructure, null, 2));

  console.log('✓ Generated: xy-chart-multi-field-breakdown-validation.json');
}

runIfMain(generateXYChartMultiFieldBreakdown, import.meta.url);
