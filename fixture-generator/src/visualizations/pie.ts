/**
 * Pie/Donut chart visualization builder
 */

import { v4 as uuid } from 'uuid';
import { LensAttributes } from '../types/lens';

export interface PieConfig {
  title: string;
  dataViewId: string;
  shape: 'pie' | 'donut' | 'treemap' | 'waffle' | 'mosaic';
  sliceBy: Array<{
    field: string;
    size?: number;
  }>;
  metric: {
    operation: 'count' | 'sum' | 'average';
    field?: string;
  };
  legend?: {
    isVisible: boolean;
    position: 'top' | 'bottom' | 'left' | 'right';
  };
}

export function buildPieChart(config: PieConfig): LensAttributes {
  const layerId = uuid();
  const metricId = uuid();
  const sliceIds = config.sliceBy.map(() => uuid());

  const columns: Record<string, unknown> = {
    [metricId]: {
      label:
        config.metric.operation === 'count'
          ? 'Count'
          : `${config.metric.operation}(${config.metric.field})`,
      dataType: 'number',
      operationType: config.metric.operation,
      sourceField: config.metric.field || '___records___',
      isBucketed: false,
      scale: 'ratio',
    },
  };

  config.sliceBy.forEach((slice, index) => {
    columns[sliceIds[index]] = {
      label: `Top ${slice.size || 5} ${slice.field}`,
      dataType: 'string',
      operationType: 'terms',
      sourceField: slice.field,
      isBucketed: true,
      scale: 'ordinal',
      params: {
        size: slice.size || 5,
        orderBy: { type: 'column', columnId: metricId },
        orderDirection: 'desc',
        otherBucket: false,
        missingBucket: false,
      },
    };
  });

  const columnOrder = [...sliceIds, metricId];

  return {
    title: config.title,
    visualizationType: 'lnsPie',
    state: {
      visualization: {
        shape: config.shape,
        layers: [
          {
            layerId,
            layerType: 'data',
            primaryGroups: sliceIds,
            metrics: [metricId],
            numberDisplay: 'percent',
            categoryDisplay: 'default',
            legendDisplay: config.legend?.isVisible ? 'show' : 'hide',
            legendPosition: config.legend?.position || 'right',
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
            [layerId]: { columns, columnOrder, incompleteColumns: {} },
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
