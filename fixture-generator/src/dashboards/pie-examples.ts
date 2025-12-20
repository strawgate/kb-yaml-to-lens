#!/usr/bin/env node
/**
 * Pie/Donut chart visualization examples
 *
 * Generates test fixtures for pie charts using Kibana's LensConfigBuilder API
 */

import { generateFixture, createDataViewReference } from '../lib/generator';
import { v4 as uuid } from 'uuid';

/**
 * Basic donut chart
 */
async function generatePieDonut() {
  const layerId = uuid();
  const sliceId = uuid();
  const metricId = uuid();
  const dataViewId = 'logs-*';

  const config = {
    title: 'Distribution by Category',
    visualizationType: 'lnsPie',
    state: {
      visualization: {
        shape: 'donut',
        layers: [
          {
            layerId,
            layerType: 'data',
            primaryGroups: [sliceId],
            metrics: [metricId],
            numberDisplay: 'percent',
            categoryDisplay: 'default',
            legendDisplay: 'show',
            legendPosition: 'right',
            nestedLegend: false,
            percentDecimals: 2,
          },
        ],
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns: {
                [sliceId]: {
                  label: 'Top 10 category',
                  dataType: 'string',
                  operationType: 'terms',
                  sourceField: 'category.keyword',
                  isBucketed: true,
                  scale: 'ordinal',
                  params: {
                    size: 10,
                    orderBy: { type: 'column', columnId: metricId },
                    orderDirection: 'desc',
                    otherBucket: false,
                    missingBucket: false,
                  },
                },
                [metricId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [sliceId, metricId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('pie-donut.json', config);
}

/**
 * Pie chart with multiple slice dimensions
 */
async function generatePieMultiLevel() {
  const layerId = uuid();
  const slice1Id = uuid();
  const slice2Id = uuid();
  const metricId = uuid();
  const dataViewId = 'logs-*';

  const config = {
    title: 'Multi-Level Distribution',
    visualizationType: 'lnsPie',
    state: {
      visualization: {
        shape: 'pie',
        layers: [
          {
            layerId,
            layerType: 'data',
            primaryGroups: [slice1Id, slice2Id],
            metrics: [metricId],
            numberDisplay: 'percent',
            categoryDisplay: 'default',
            legendDisplay: 'show',
            legendPosition: 'right',
            nestedLegend: true,
            percentDecimals: 1,
          },
        ],
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns: {
                [slice1Id]: {
                  label: 'Top 5 source',
                  dataType: 'string',
                  operationType: 'terms',
                  sourceField: 'source.keyword',
                  isBucketed: true,
                  scale: 'ordinal',
                  params: {
                    size: 5,
                    orderBy: { type: 'column', columnId: metricId },
                    orderDirection: 'desc',
                    otherBucket: true,
                    missingBucket: false,
                  },
                },
                [slice2Id]: {
                  label: 'Top 3 type',
                  dataType: 'string',
                  operationType: 'terms',
                  sourceField: 'type.keyword',
                  isBucketed: true,
                  scale: 'ordinal',
                  params: {
                    size: 3,
                    orderBy: { type: 'column', columnId: metricId },
                    orderDirection: 'desc',
                    otherBucket: false,
                    missingBucket: false,
                  },
                },
                [metricId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [slice1Id, slice2Id, metricId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('pie-multi-level.json', config);
}

// Run all generators when executed directly
if (require.main === module) {
  Promise.all([
    generatePieDonut(),
    generatePieMultiLevel(),
  ])
    .then(() => console.log('✓ All pie chart fixtures generated'))
    .catch((err) => {
      console.error('Failed to generate fixtures:', err);
      process.exit(1);
    });
}
