#!/usr/bin/env node
/**
 * XY Chart visualization examples
 *
 * Generates test fixtures for XY charts (line, bar, area) using Kibana's LensConfigBuilder API
 */

import { generateFixture, createDataViewReference } from '../lib/generator';
import { v4 as uuid } from 'uuid';

/**
 * Basic line chart with date histogram
 */
async function generateXYLineChart() {
  const layerId = uuid();
  const xColumnId = uuid();
  const yColumnId = uuid();
  const dataViewId = 'logs-*';

  const config = {
    title: 'Requests Over Time',
    visualizationType: 'lnsXY',
    state: {
      visualization: {
        legend: { isVisible: true, position: 'right' },
        valueLabels: 'hide',
        fittingFunction: 'None',
        preferredSeriesType: 'line',
        layers: [
          {
            layerId,
            layerType: 'data',
            seriesType: 'line',
            xAccessor: xColumnId,
            accessors: [yColumnId],
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
                [xColumnId]: {
                  label: '@timestamp',
                  dataType: 'date',
                  operationType: 'date_histogram',
                  sourceField: '@timestamp',
                  isBucketed: true,
                  scale: 'interval',
                  params: {
                    interval: 'auto',
                    includeEmptyRows: true,
                    dropPartials: false,
                  },
                },
                [yColumnId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [xColumnId, yColumnId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('xy-line-chart.json', config);
}

/**
 * Bar chart with breakdown (split series)
 */
async function generateXYBarWithBreakdown() {
  const layerId = uuid();
  const xColumnId = uuid();
  const yColumnId = uuid();
  const breakdownId = uuid();
  const dataViewId = 'logs-*';

  const config = {
    title: 'Requests by Status Code',
    visualizationType: 'lnsXY',
    state: {
      visualization: {
        legend: { isVisible: true, position: 'right' },
        valueLabels: 'hide',
        fittingFunction: 'None',
        preferredSeriesType: 'bar_stacked',
        layers: [
          {
            layerId,
            layerType: 'data',
            seriesType: 'bar_stacked',
            xAccessor: xColumnId,
            accessors: [yColumnId],
            splitAccessor: breakdownId,
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
                [breakdownId]: {
                  label: 'Top 5 status_code',
                  dataType: 'string',
                  operationType: 'terms',
                  sourceField: 'response.status_code',
                  isBucketed: true,
                  scale: 'ordinal',
                  params: {
                    size: 5,
                    orderBy: { type: 'column', columnId: yColumnId },
                    orderDirection: 'desc',
                    otherBucket: true,
                    missingBucket: false,
                  },
                },
                [xColumnId]: {
                  label: '@timestamp',
                  dataType: 'date',
                  operationType: 'date_histogram',
                  sourceField: '@timestamp',
                  isBucketed: true,
                  scale: 'interval',
                  params: {
                    interval: 'auto',
                  },
                },
                [yColumnId]: {
                  label: 'Count',
                  dataType: 'number',
                  operationType: 'count',
                  sourceField: '___records___',
                  isBucketed: false,
                  scale: 'ratio',
                },
              },
              columnOrder: [breakdownId, xColumnId, yColumnId],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [createDataViewReference(dataViewId, layerId)],
  };

  await generateFixture('xy-bar-stacked.json', config);
}

// Run all generators when executed directly
if (require.main === module) {
  Promise.all([
    generateXYLineChart(),
    generateXYBarWithBreakdown(),
  ])
    .then(() => console.log('✓ All XY chart fixtures generated'))
    .catch((err) => {
      console.error('Failed to generate fixtures:', err);
      process.exit(1);
    });
}
