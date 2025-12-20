/**
 * TypeScript type definitions for Kibana Lens visualizations
 * These types match the structure expected by Kibana's LensConfigBuilder API
 */

export interface SavedObjectReference {
  type: string;
  id: string;
  name: string;
}

export type LensVisualizationType =
  | 'lnsXY'
  | 'lnsMetric'
  | 'lnsPie'
  | 'lnsGauge'
  | 'lnsHeatmap'
  | 'lnsDatatable';

export type LensOperationType =
  // Bucket operations
  | 'date_histogram'
  | 'terms'
  | 'filters'
  | 'range'
  | 'intervals'
  // Metric operations
  | 'count'
  | 'sum'
  | 'average'
  | 'min'
  | 'max'
  | 'median'
  | 'percentile'
  | 'unique_count'
  | 'last_value'
  | 'standard_deviation'
  // Pipeline operations
  | 'cumulative_sum'
  | 'counter_rate'
  | 'differences'
  | 'moving_average'
  // Special
  | 'formula'
  | 'static_value';

export interface LensColumn {
  label: string;
  dataType: 'string' | 'number' | 'date' | 'boolean';
  operationType: LensOperationType;
  isBucketed: boolean;
  sourceField?: string;
  scale?: 'ordinal' | 'interval' | 'ratio';
  params?: Record<string, unknown>;
  filter?: { query: string; language: string };
  timeShift?: string;
  references?: string[];
}

export interface FormBasedLayer {
  columns: Record<string, LensColumn>;
  columnOrder: string[];
  incompleteColumns?: Record<string, unknown>;
}

export interface VisualizationState {
  [key: string]: unknown;
}

export interface LensAttributes {
  title: string;
  description?: string;
  visualizationType: LensVisualizationType;
  state: {
    visualization: VisualizationState;
    query: { query: string; language: 'kuery' | 'lucene' };
    filters: unknown[];
    datasourceStates: {
      formBased: {
        layers: Record<string, FormBasedLayer>;
      };
    };
  };
  references: SavedObjectReference[];
}

export interface DashboardSavedObject {
  type: 'dashboard';
  id: string;
  attributes: {
    title: string;
    description: string;
    version: number;
    timeRestore: boolean;
    timeFrom?: string;
    timeTo?: string;
    kibanaSavedObjectMeta: {
      searchSourceJSON: string;
    };
    optionsJSON: string;
    panelsJSON: string;
  };
  references: SavedObjectReference[];
}

export interface GridPosition {
  x: number;
  y: number;
  w: number;
  h: number;
}
