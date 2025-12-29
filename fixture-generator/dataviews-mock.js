#!/usr/bin/env node
/**
 * Simplified DataViews mock for fixture generation
 *
 * Based on Kibana's official mockDataViewsService from:
 * /kibana/src/platform/packages/shared/kbn-lens-embeddable-utils/config_builder/charts/mock_utils.ts
 *
 * This is a non-Jest version suitable for standalone script execution.
 */

/**
 * Creates a simple mock data view object
 */
function createMockDataView({ id = 'test', title = 'logs-*' } = {}) {
  return {
    id,
    title,
    metaFields: [],
    isPersisted: () => true,
    toSpec: () => ({}),
    fields: {
      getByName: (name) => {
        // Return appropriate field types based on common field names
        switch (name) {
          case '@timestamp':
            return { type: 'datetime', name };
          case 'category':
          case 'agent.name':
          case 'host.name':
          case 'log.level':
          case 'geo.src':
          case 'geo.dest':
            return { type: 'string', name };
          case 'price':
          case 'bytes':
          case 'count':
            return { type: 'number', name };
          default:
            return { type: 'string', name };
        }
      },
    },
  };
}

/**
 * Creates a mock DataViews service compatible with DataViewsCommon interface
 *
 * Implements the minimal interface required by LensConfigBuilder:
 * - get(id): retrieve a data view by ID
 * - create({ id, title, timeFieldName }): create a new data view
 */
export function createDataViewsMock() {
  return {
    /**
     * Mock get() method - returns a data view for the given ID
     */
    async get(id) {
      // Parse the ID if it's a JSON string (as used by some chart builders)
      let dataViewId = id;
      let title = 'logs-*';

      try {
        const parsed = JSON.parse(id);
        if (parsed.index) {
          dataViewId = parsed.index;
          title = parsed.index;
        }
      } catch {
        // Not JSON, use as-is
      }

      return createMockDataView({ id: dataViewId, title });
    },

    /**
     * Mock create() method - returns a new data view
     */
    async create({ id, title, timeFieldName } = {}) {
      return createMockDataView({ id: id || 'created-dataview', title: title || 'logs-*' });
    },
  };
}
