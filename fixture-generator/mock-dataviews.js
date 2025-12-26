/**
 * Mock DataViews API for fixture generation
 *
 * The LensConfigBuilder requires a DataViews API to build configurations.
 * This mock provides the minimal implementation needed for fixture generation.
 */

/**
 * Creates a mock dataview object with all required methods
 */
function createMockDataView({ id, title, timeFieldName }) {
  // Create a mock fields array with common fields
  const mockFields = [
    { name: '@timestamp', type: 'date', aggregatable: true, searchable: true },
    { name: 'message', type: 'string', aggregatable: false, searchable: true },
    { name: 'count', type: 'number', aggregatable: true, searchable: true },
    { name: 'agent.name', type: 'string', aggregatable: true, searchable: true },
    { name: 'host.name', type: 'string', aggregatable: true, searchable: true },
  ];

  return {
    id: id || 'mock-dataview',
    title: title || 'logs-*',
    timeFieldName: timeFieldName || '@timestamp',
    fields: mockFields,
    getFieldByName: (name) => {
      const found = mockFields.find(f => f.name === name);
      return found || {
        name,
        type: 'string',
        aggregatable: true,
        searchable: true,
      };
    },
    toSpec: function() {
      return {
        id: this.id,
        title: this.title,
        timeFieldName: this.timeFieldName,
        fields: this.fields,
      };
    },
  };
}

/**
 * Creates a mock DataViews API that satisfies the DataViewsCommon interface
 * Required methods: get, create
 */
export function createMockDataViewsAPI() {
  return {
    /**
     * Mock get() method - returns a minimal dataview object
     */
    async get(id) {
      return createMockDataView({ id });
    },

    /**
     * Mock create() method - returns a minimal dataview object
     */
    async create({ title, timeFieldName, id }) {
      return createMockDataView({ id, title, timeFieldName });
    },
  };
}
