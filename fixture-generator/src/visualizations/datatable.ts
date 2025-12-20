/**
 * Data table visualization builder
 */

import { v4 as uuid } from 'uuid';
import { LensAttributes } from '../types/lens';

export interface DatatableConfig {
  title: string;
  dataViewId: string;
  columns: Array<{
    field: string;
    operation:
      | 'terms'
      | 'date_histogram'
      | 'count'
      | 'sum'
      | 'average'
      | 'min'
      | 'max';
    label?: string;
    size?: number;
    interval?: string;
  }>;
  sorting?: {
    columnIndex: number;
    direction: 'asc' | 'desc';
  };
}

export function buildDatatable(config: DatatableConfig): LensAttributes {
  const layerId = uuid();
  const columnIds = config.columns.map(() => uuid());

  const columns: Record<string, unknown> = {};
  const bucketColumns: string[] = [];
  const metricColumns: string[] = [];

  config.columns.forEach((col, index) => {
    const colId = columnIds[index];
    const isBucket = ['terms', 'date_histogram'].includes(col.operation);

    if (isBucket) {
      bucketColumns.push(colId);
    } else {
      metricColumns.push(colId);
    }

    columns[colId] = buildTableColumn(col, colId, metricColumns[0]);
  });

  return {
    title: config.title,
    visualizationType: 'lnsDatatable',
    state: {
      visualization: {
        layerId,
        layerType: 'data',
        columns: columnIds.map((colId, index) => ({
          columnId: colId,
          isTransposed: false,
          width: undefined,
          hidden: false,
          colorMode: 'none',
        })),
        sorting: config.sorting
          ? {
              columnId: columnIds[config.sorting.columnIndex],
              direction: config.sorting.direction,
            }
          : undefined,
        rowHeight: 'single',
        headerRowHeight: 'single',
        paging: { size: 10, enabled: true },
      },
      query: { query: '', language: 'kuery' },
      filters: [],
      datasourceStates: {
        formBased: {
          layers: {
            [layerId]: {
              columns,
              columnOrder: [...bucketColumns, ...metricColumns],
              incompleteColumns: {},
            },
          },
        },
      },
    },
    references: [
      {
        type: 'index-pattern',
        id: config.dataViewId,
        name: `indexpattern-datasource-layer-${layerId}`,
      },
    ],
  };
}

function buildTableColumn(
  col: DatatableConfig['columns'][0],
  colId: string,
  metricColId?: string
) {
  switch (col.operation) {
    case 'date_histogram':
      return {
        label: col.label || col.field,
        dataType: 'date',
        operationType: 'date_histogram',
        sourceField: col.field,
        isBucketed: true,
        scale: 'interval',
        params: { interval: col.interval || 'auto' },
      };
    case 'terms':
      return {
        label: col.label || col.field,
        dataType: 'string',
        operationType: 'terms',
        sourceField: col.field,
        isBucketed: true,
        scale: 'ordinal',
        params: {
          size: col.size || 10,
          orderBy: metricColId
            ? { type: 'column', columnId: metricColId }
            : { type: 'alphabetical' },
          orderDirection: 'desc',
        },
      };
    case 'count':
      return {
        label: col.label || 'Count',
        dataType: 'number',
        operationType: 'count',
        sourceField: '___records___',
        isBucketed: false,
        scale: 'ratio',
      };
    default:
      return {
        label: col.label || `${col.operation}(${col.field})`,
        dataType: 'number',
        operationType: col.operation,
        sourceField: col.field,
        isBucketed: false,
        scale: 'ratio',
      };
  }
}
