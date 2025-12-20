#!/usr/bin/env node
/**
 * Metric visualization examples
 *
 * Generates test fixtures for metric visualizations using Kibana's LensConfigBuilder API
 */

import { generateFixture, createDataViewReference } from '../lib/generator';
import { v4 as uuid } from 'uuid';

/**
 * Basic metric - just a count
 */
async function generateMetricBasic() {
  const layerId = uuid();
  const metricId = '156e3e91-7bb6-406f-8ae5-cb409747953b';  // Match Python test data
  const dataViewId = 'logs-*';

  const config = {
    title: 'Basic Metric Count',
    visualizationType: 'lnsMetric',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        metricAccessor: metricId,
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns: {
                [metricId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [metricId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('metric-basic.json', config);
}

/**
 * Metric with primary and secondary metrics
 */
async function generateMetricWithSecondary() {
  const layerId = uuid();
  const primaryId = '156e3e91-7bb6-406f-8ae5-cb409747953b';
  const secondaryId = 'a1ec5883-19b2-4ab9-b027-a13d6074128b';
  const dataViewId = 'logs-*';

  const config = {
    title: 'Metric with Secondary',
    visualizationType: 'lnsMetric',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        metricAccessor: primaryId,
        secondaryMetricAccessor: secondaryId,
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns: {
                [primaryId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
                [secondaryId]: {
                  label: 'Unique Count',
                  dataType: 'number',
                  operationType: 'unique_count',
                  sourceField: 'agent.name',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [primaryId, secondaryId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('metric-with-secondary.json', config);
}

/**
 * Metric with breakdown by field
 */
async function generateMetricWithBreakdown() {
  const layerId = uuid();
  const primaryId = '156e3e91-7bb6-406f-8ae5-cb409747953b';
  const secondaryId = 'a1ec5883-19b2-4ab9-b027-a13d6074128b';
  const breakdownId = '17fe5b4b-d36c-4fbd-ace9-58d143bb3172';
  const dataViewId = 'logs-*';

  const config = {
    title: 'Metric with Breakdown',
    visualizationType: 'lnsMetric',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        metricAccessor: primaryId,
        secondaryMetricAccessor: secondaryId,
        breakdownByAccessor: breakdownId,
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns: {
                [breakdownId]: {
                  label: 'Top 5 agent.name',
                  dataType: 'string',
                  operationType: 'terms',
                  sourceField: 'agent.name',
                  isBucketed: true,
                  scale: 'ordinal',
                  params: {
                    size: 5,
                    orderBy: { type: 'column', columnId: primaryId },
                    orderDirection: 'desc',
                    otherBucket: true,
                    missingBucket: false,
                  },
                },
                [primaryId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
                [secondaryId]: {
                  label: 'Unique Count',
                  dataType: 'number',
                  operationType: 'unique_count',
                  sourceField: 'aerospike.node.name',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [breakdownId, primaryId, secondaryId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('metric-with-breakdown.json', config);
}

// Run all generators when executed directly
if (require.main === module) {
  Promise.all([
    generateMetricBasic(),
    generateMetricWithSecondary(),
    generateMetricWithBreakdown(),
  ])
    .then(() => console.log('✓ All metric fixtures generated'))
    .catch((err) => {
      console.error('Failed to generate fixtures:', err);
      process.exit(1);
    });
}
