/**
 * Actions - Handles export and upload functionality
 */

// Debug: Check if jsyaml is loaded
console.log('[Actions] jsyaml available at load:', typeof jsyaml !== 'undefined', typeof window.jsyaml !== 'undefined');

let currentNDJSON = null;
let yaml = null;
let yamlLoadPromise = null;

// Get reference to jsyaml - try multiple ways
function getYamlLib() {
  if (yaml) return yaml;
  if (typeof jsyaml !== 'undefined') {
    yaml = jsyaml;
    return yaml;
  }
  if (typeof window.jsyaml !== 'undefined') {
    yaml = window.jsyaml;
    return yaml;
  }
  return null;
}

// Dynamically load js-yaml if not already loaded
async function ensureYamlLoaded() {
  if (yaml) return yaml;
  
  yaml = getYamlLib();
  if (yaml) return yaml;
  
  // If still not loaded, try to load it dynamically
  if (!yamlLoadPromise) {
    yamlLoadPromise = new Promise((resolve, reject) => {
      console.log('[Actions] Dynamically loading js-yaml...');
      
      // Temporarily hide AMD define to prevent Monaco loader conflicts
      const originalDefine = window.define;
      window.define = undefined;
      
      const script = document.createElement('script');
      script.src = chrome.runtime.getURL('lib/js-yaml.min.js');
      script.onload = () => {
        // Restore AMD define
        window.define = originalDefine;
        
        console.log('[Actions] js-yaml loaded dynamically');
        yaml = getYamlLib();
        if (yaml) {
          resolve(yaml);
        } else {
          reject(new Error('js-yaml loaded but jsyaml global not found'));
        }
      };
      script.onerror = (e) => {
        // Restore AMD define
        window.define = originalDefine;
        
        console.error('[Actions] Failed to load js-yaml:', e);
        reject(new Error('Failed to load js-yaml library'));
      };
      document.head.appendChild(script);
    });
  }
  
  return yamlLoadPromise;
}

// Try to get yaml immediately
yaml = getYamlLib();

if (!yaml) {
  console.warn('[Actions] js-yaml not available at load time, will load dynamically when needed');
}

/**
 * Setup action button handlers
 */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('new-dashboard')?.addEventListener('click', handleNewDashboard);
  document.getElementById('import-dashboard')?.addEventListener('click', handleImportDashboard);
  document.getElementById('export-ndjson')?.addEventListener('click', handleExportNDJSON);
  document.getElementById('upload-kibana')?.addEventListener('click', handleUploadKibana);
  document.getElementById('format-yaml')?.addEventListener('click', handleFormatYAML);
  
  // Check if we're on a dashboard view page and enable/disable import button
  checkDashboardViewPage();
  
  // Re-check periodically and when tabs change
  setInterval(checkDashboardViewPage, 1000);
  chrome.tabs.onActivated.addListener(checkDashboardViewPage);
  chrome.tabs.onUpdated.addListener(checkDashboardViewPage);
});

/**
 * Create new dashboard from template
 */
function handleNewDashboard() {
  if (confirm('Replace current dashboard with a new template?')) {
    const template = `---
dashboards:
  - name: New Dashboard
    description: Enter your description here
    panels:
      - title: Getting Started
        grid: { x: 0, y: 0, w: 48, h: 10 }
        markdown:
          content: |
            # Getting Started
            
            Start building your dashboard here!
`;
    editor.setValue(template);
    updateStatus('ready', 'New dashboard created');
  }
}

/**
 * Export dashboard as NDJSON file
 */
async function handleExportNDJSON() {
  try {
    updateStatus('compiling', 'Exporting...');
    
    const yamlContent = editor.getValue();
    const result = await window.pythonCompiler.compile(yamlContent);
    
    if (!result.success) {
      showError('Cannot export: ' + result.error);
      updateStatus('error', 'Export failed');
      return;
    }
    
    // Parse to get dashboard name for filename
    let filename = 'dashboard.ndjson';
    try {
      const firstLine = result.ndjson.split('\n')[0];
      const dashboard = JSON.parse(firstLine);
      const title = dashboard.attributes?.title || 'dashboard';
      filename = title.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '.ndjson';
    } catch (e) {
      // Use default filename
    }
    
    // Create download
    const blob = new Blob([result.ndjson], { type: 'application/x-ndjson' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    
    updateStatus('ready', 'Exported successfully');
  } catch (error) {
    showError('Export failed: ' + error.message);
    updateStatus('error', 'Export failed');
  }
}

/**
 * Extract Kibana base URL from a tab URL
 */
function extractKibanaUrl(tabUrl) {
  try {
    const url = new URL(tabUrl);
    // Return protocol + host (e.g., https://localhost:5601)
    return `${url.protocol}//${url.host}`;
  } catch (e) {
    return null;
  }
}

/**
 * Upload dashboard directly from side panel using Kibana's import API
 */
async function uploadDashboardDirect(ndjson, kibanaUrl, tabId) {
  console.log('[Upload] Uploading to:', kibanaUrl);
  
  // Use Kibana's saved objects import API
  const uploadUrl = `${kibanaUrl}/api/saved_objects/_import?overwrite=true`;
  
  console.log('[Upload] Using import API:', uploadUrl);
  
  try {
    // Use chrome.scripting to execute fetch in the context of the Kibana tab
    // This way we can use the Kibana session cookies for authentication
    const results = await chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: async (url, ndjsonContent) => {
        // Create a FormData object with the NDJSON file
        const formData = new FormData();
        const blob = new Blob([ndjsonContent], { type: 'application/ndjson' });
        formData.append('file', blob, 'dashboard.ndjson');
        
        const response = await fetch(url, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'kbn-xsrf': 'true'
            // Don't set Content-Type - let browser set it with boundary for FormData
          },
          body: formData
        });
        
        const responseText = await response.text();
        
        return {
          ok: response.ok,
          status: response.status,
          statusText: response.statusText,
          body: responseText
        };
      },
      args: [uploadUrl, ndjson]
    });
    
    const result = results[0].result;
    
    if (!result.ok) {
      console.error('[Upload] Upload failed:', result.status, result.body);
      
      let errorDetails = result.body;
      try {
        const errorObj = JSON.parse(result.body);
        if (errorObj.message) {
          errorDetails = errorObj.message;
        }
        if (errorObj.error) {
          errorDetails = `${errorObj.error}: ${errorDetails}`;
        }
      } catch (e) {
        // Use raw body if not JSON
      }
      
      throw new Error(`Upload failed (${result.status}): ${errorDetails}`);
    }
    
    // Parse success response
    let successCount = 0;
    let errorCount = 0;
    try {
      const responseObj = JSON.parse(result.body);
      successCount = responseObj.successCount || 0;
      errorCount = responseObj.errors?.length || 0;
      
      console.log('[Upload] Import results:', {
        success: successCount,
        errors: errorCount,
        details: responseObj
      });
      
      if (errorCount > 0) {
        const errorMessages = responseObj.errors.map(err => 
          `${err.type} (${err.id}): ${err.error?.message || err.error?.type || 'Unknown error'}`
        ).join('\n');
        throw new Error(`Upload completed with ${errorCount} error(s):\n${errorMessages}`);
      }
    } catch (e) {
      if (e.message.includes('error(s)')) {
        throw e; // Re-throw our formatted error
      }
      // If we can't parse response but it was ok, assume success
      console.log('[Upload] Response:', result.body);
    }
    
    console.log('[Upload] Successfully uploaded', successCount, 'object(s)');
  } catch (error) {
    // Check for common network/SSL errors
    if (error.message && (error.message.includes('Failed to fetch') || 
        (error.message.includes('fetch') && !error.message.includes('Upload failed')))) {
      throw new Error(
        'Network error: Cannot connect to Kibana. This may be due to:\n' +
        '1. SSL certificate issues (ERR_CERT_AUTHORITY_INVALID)\n' +
        '2. CORS restrictions\n' +
        '3. Kibana not running at ' + kibanaUrl + '\n\n' +
        'If using HTTPS with self-signed certificates, visit ' + kibanaUrl + 
        ' in a new tab and accept the certificate warning first.'
      );
    }
    throw error;
  }
}

/**
 * Upload dashboard to Kibana
 */
async function handleUploadKibana() {
  try {
    updateStatus('compiling', 'Uploading...');
    
    const yamlContent = editor.getValue();
    const result = await window.pythonCompiler.compile(yamlContent);
    
    if (!result.success) {
      showError('Cannot upload: ' + result.error);
      updateStatus('error', 'Upload failed');
      return;
    }
    
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.url) {
      showError('No active tab found');
      updateStatus('error', 'Upload failed');
      return;
    }
    
    // Check if current tab is a Kibana page and extract URL
    const isKibanaTab = tab.url.includes('/app/') || 
                        tab.url.includes('kibana') ||
                        tab.url.includes('elastic.co') ||
                        tab.url.includes(':5601') ||
                        tab.url.includes(':9243');
    
    if (!isKibanaTab) {
      const proceed = confirm(
        'Current tab doesn\'t appear to be a Kibana page.\n' +
        'Current URL: ' + tab.url + '\n\n' +
        'To upload dashboards:\n' +
        '1. Navigate to your Kibana instance\n' +
        '2. Try uploading again\n\n' +
        'Click OK to export as NDJSON instead, or Cancel to go back.'
      );
      
      if (proceed) {
        await handleExportNDJSON();
      }
      updateStatus('ready', 'Upload cancelled');
      return;
    }
    
    // Extract Kibana URL from current tab
    const kibanaUrl = extractKibanaUrl(tab.url);
    
    if (!kibanaUrl) {
      showError('Could not determine Kibana URL from current tab');
      updateStatus('error', 'Upload failed');
      return;
    }
    
    console.log('[Upload] Detected Kibana URL:', kibanaUrl, 'from tab:', tab.url);
    
    try {
      // Use direct upload via chrome.scripting API (no content script needed)
      await uploadDashboardDirect(result.ndjson, kibanaUrl, tab.id);
      
      // Extract dashboard ID from NDJSON to navigate to it
      let dashboardId = null;
      try {
        const lines = result.ndjson.split('\n');
        for (const line of lines) {
          if (line.trim()) {
            const obj = JSON.parse(line);
            if (obj.type === 'dashboard') {
              dashboardId = obj.id;
              break;
            }
          }
        }
      } catch (e) {
        console.error('[Upload] Failed to extract dashboard ID:', e);
      }
      
      // Navigate to the dashboard if we found the ID
      if (dashboardId) {
        const dashboardUrl = `${kibanaUrl}/app/dashboards#/view/${dashboardId}`;
        console.log('[Upload] Navigating to dashboard:', dashboardUrl);
        await chrome.tabs.update(tab.id, { url: dashboardUrl });
        updateStatus('ready', 'Dashboard opened!');
      } else {
        updateStatus('ready', 'Uploaded successfully!');
        alert('Dashboard uploaded to ' + kibanaUrl + ' successfully!');
      }
    } catch (error) {
      console.error('[Upload] Upload error:', error);
      
      const errorMsg = error.message || error.toString();
      
      if (errorMsg.includes('CERT') || errorMsg.includes('SSL') || errorMsg.includes('AUTHORITY_INVALID')) {
        showError(
          'SSL Certificate Error:\n\n' +
          'Your Kibana instance uses HTTPS with an invalid certificate. To fix:\n' +
          '1. Visit ' + kibanaUrl + ' and accept the certificate warning\n' +
          '2. Reload the Kibana page\n' +
          '3. Try uploading again\n\n' +
          'Alternative: Use HTTP instead of HTTPS for local development.'
        );
      } else {
        showError('Upload failed: ' + errorMsg);
      }
      
      updateStatus('error', 'Upload failed');
    }
    
  } catch (error) {
    console.error('[Upload] Unexpected error:', error);
    showError('Upload failed: ' + error.message);
    updateStatus('error', 'Upload failed');
  }
}

/**
 * Format YAML
 */
function handleFormatYAML() {
  try {
    const yamlContent = editor.getValue();
    const parsed = yaml.load(yamlContent);
    const formatted = yaml.dump(parsed, {
      indent: 2,
      lineWidth: -1,
      noRefs: true
    });
    editor.setValue(formatted);
    updateStatus('ready', 'YAML formatted');
  } catch (error) {
    showError('Format failed: ' + error.message);
  }
}

/**
 * Store compiled NDJSON for later use
 */
window.addEventListener('preview-updated', (event) => {
  currentNDJSON = event.detail.ndjson;
});

// ============================================================================
// Dashboard Decompilation Functions (from content-script.js)
// ============================================================================

/**
 * Decompile dashboard controls
 */
function decompileControls(controlGroupInput, references) {
  if (!controlGroupInput) return [];
  
  let panels = {};
  try {
    panels = typeof controlGroupInput.panelsJSON === 'string' 
      ? JSON.parse(controlGroupInput.panelsJSON) 
      : (controlGroupInput.panels || {});
  } catch (e) {
    console.error('Failed to parse controls:', e);
    return [];
  }
  
  const controls = [];
  
  // Convert object to array and sort by order
  const controlEntries = Object.entries(panels).sort((a, b) => {
    return (a[1].order || 0) - (b[1].order || 0);
  });
  
  for (const [panelId, panel] of controlEntries) {
    const control = {};
    const controlType = panel.type;
    const config = panel.explicitInput || panel;
    
    // Determine control type
    if (controlType === 'optionsListControl') {
      control.type = 'options';
    } else if (controlType === 'rangeSliderControl') {
      control.type = 'range';
    } else if (controlType === 'timeSliderControl') {
      control.type = 'time';
    } else {
      control.type = controlType;
    }
    
    // Add label
    if (config.title) {
      control.label = config.title;
    }
    
    // Add field
    if (config.fieldName) {
      control.field = config.fieldName;
    }
    
    // Try to find data view from references or config
    if (config.dataViewId) {
      control.data_view = config.dataViewId;
    } else {
      // Look for data view in references
      const controlRef = references?.find(ref => 
        ref.name?.includes(`controlGroup_${panelId}`) && ref.type === 'index-pattern'
      );
      if (controlRef) {
        control.data_view = controlRef.id;
      }
    }
    
    // Add width if not default
    if (config.width && config.width !== 'medium') {
      control.width = config.width;
    }
    
    // Options control specific settings
    if (control.type === 'options') {
      if (config.singleSelect === false || config.selectedOptions?.length > 1) {
        control.multiple = true;
      }
      if (config.searchTechnique && config.searchTechnique !== 'prefix') {
        control.match_technique = config.searchTechnique;
      }
    }
    
    // Range control specific settings
    if (control.type === 'range' && config.step) {
      control.step = config.step;
    }
    
    controls.push(control);
  }
  
  return controls;
}

/**
 * Decompile dashboard filters
 */
function decompileFilters(searchSourceJSON) {
  if (!searchSourceJSON) return [];
  
  let filters = [];
  try {
    const parsed = typeof searchSourceJSON === 'string' ? JSON.parse(searchSourceJSON) : searchSourceJSON;
    
    // searchSourceJSON has structure: { query: {...}, filter: [...], ... }
    // Handle various possible structures
    if (Array.isArray(parsed)) {
      filters = parsed;
    } else if (parsed && Array.isArray(parsed.filter)) {
      // Most common: searchSourceJSON.filter
      filters = parsed.filter;
    } else if (parsed && Array.isArray(parsed.filters)) {
      filters = parsed.filters;
    } else if (parsed && parsed.filter && !Array.isArray(parsed.filter)) {
      // Single filter wrapped in object
      filters = [parsed.filter];
    } else {
      console.log('No filters found in searchSourceJSON:', Object.keys(parsed || {}));
      return [];
    }
  } catch (e) {
    console.error('Failed to parse filters:', e);
    return [];
  }
  
  return filters.map(filter => {
    const meta = filter.meta || {};
    const result = {};
    
    // Handle disabled filters
    if (meta.disabled) {
      result.disabled = true;
    }
    
    // Handle negated filters
    const isNegated = meta.negate === true;
    
    // Handle different filter types
    if (meta.type === 'exists') {
      if (isNegated) {
        result.not = { exists: meta.key };
      } else {
        result.exists = meta.key;
      }
    } else if (meta.type === 'phrase') {
      const phraseFilter = {
        field: meta.key,
        equals: meta.params?.query || meta.value
      };
      if (isNegated) {
        result.not = phraseFilter;
      } else {
        Object.assign(result, phraseFilter);
      }
    } else if (meta.type === 'phrases') {
      const phrasesFilter = {
        field: meta.key,
        in: meta.params || []
      };
      if (isNegated) {
        result.not = phrasesFilter;
      } else {
        Object.assign(result, phrasesFilter);
      }
    } else if (meta.type === 'range') {
      const rangeFilter = { field: meta.key };
      const params = filter.query?.range?.[meta.key] || meta.params || {};
      if (params.gte !== undefined) rangeFilter.gte = String(params.gte);
      if (params.gt !== undefined) rangeFilter.gt = String(params.gt);
      if (params.lte !== undefined) rangeFilter.lte = String(params.lte);
      if (params.lt !== undefined) rangeFilter.lt = String(params.lt);
      if (isNegated) {
        result.not = rangeFilter;
      } else {
        Object.assign(result, rangeFilter);
      }
    } else if (filter.query) {
      // Custom DSL filter
      result.dsl = filter.query;
    }
    
    // Add alias if present
    if (meta.alias) {
      result.alias = meta.alias;
    }
    
    return result;
  }).filter(f => Object.keys(f).length > 0);
}

/**
 * Extract data view ID from panel references
 */
function extractDataView(panel) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const references = attrs.references || [];
  
  // Look for index-pattern reference
  const indexPatternRef = references.find(ref => ref.type === 'index-pattern');
  if (indexPatternRef) {
    return indexPatternRef.id;
  }
  
  // Fallback: try to find from layer references
  const layerRef = references.find(ref => ref.name?.includes('indexpattern-datasource-layer'));
  if (layerRef) {
    return layerRef.id;
  }
  
  return 'logs-*'; // Ultimate fallback
}

// Map Kibana operation types to YAML aggregation names
const OPERATION_MAPPING = {
  'count': 'count',
  'sum': 'sum',
  'avg': 'average',
  'average': 'average',
  'min': 'min',
  'max': 'max',
  'median': 'median',
  'percentile': 'percentile',
  'unique_count': 'unique_count',
  'cardinality': 'unique_count',
  'last_value': 'last_value',
  'counter_rate': 'counter_rate',
  'cumulative_sum': 'cumulative_sum',
  'differences': 'differences',
  'moving_average': 'moving_average'
};

// Map Kibana dimension types to YAML dimension types
const DIMENSION_TYPE_MAPPING = {
  'date_histogram': 'date_histogram',
  'terms': 'values',
  'range': 'range',
  'filters': 'filters',
  'intervals': 'intervals'
};

/**
 * Determine XY chart type from layer configuration
 */
function getXYChartType(layer) {
  const seriesType = layer?.seriesType || 'line';
  if (seriesType.includes('bar')) return 'bar';
  if (seriesType.includes('area')) return 'area';
  return 'line';
}

/**
 * Parse a single column from Lens state
 */
function parseColumn(column, columnId) {
  const opType = column.operationType;
  const field = column.sourceField;
  const label = column.label;
  
  // Check if this is a dimension (bucketed) or metric
  const isBucketed = column.isBucketed === true;
  
  if (isBucketed) {
    // This is a dimension
    const dimension = {
      field: field,
      type: DIMENSION_TYPE_MAPPING[opType] || 'values'
    };
    
    if (label && label !== column.sourceField) {
      dimension.label = label;
    }
    
    // Extract size for terms aggregations
    if (opType === 'terms' && column.params?.size) {
      dimension.size = column.params.size;
    }
    
    // Extract interval for date histograms
    if (opType === 'date_histogram' && column.params?.interval) {
      dimension.interval = column.params.interval;
    }
    
    return { type: 'dimension', data: dimension };
  } else {
    // This is a metric
    const metric = {};
    
    if (opType === 'formula' && column.params?.formula) {
      metric.formula = column.params.formula;
    } else {
      metric.aggregation = OPERATION_MAPPING[opType] || opType;
      if (field && opType !== 'count') {
        metric.field = field;
      }
    }
    
    if (label && label !== 'Count' && label !== column.sourceField) {
      metric.label = label;
    }
    
    // Handle percentile parameter
    if (opType === 'percentile' && column.params?.percentile) {
      metric.percentile = column.params.percentile;
    }
    
    // Handle format
    if (column.params?.format) {
      const format = column.params.format;
      if (format.id && format.id !== 'number') {
        metric.format = { type: format.id };
        if (format.params?.pattern) {
          metric.format.pattern = format.params.pattern;
        }
      }
    }
    
    return { type: 'metric', data: metric };
  }
}

/**
 * Parse Lens layers to extract dimensions, metrics, and breakdown
 */
function parseLensLayers(state) {
  const layers = state?.datasourceStates?.formBased?.layers || 
                 state?.datasourceStates?.indexpattern?.layers || {};
  const visualization = state?.visualization || {};
  
  const result = {
    dimensions: [],
    metrics: [],
    breakdown: [],
    primaryMetric: null
  };
  
  // Get layer order from visualization config if available
  const layerIds = Object.keys(layers);
  if (layerIds.length === 0) return result;
  
  // Parse each layer
  for (const layerId of layerIds) {
    const layer = layers[layerId];
    const columns = layer.columns || {};
    const columnOrder = layer.columnOrder || Object.keys(columns);
    
    // Determine which columns are used for which purpose based on visualization accessors
    const xAccessor = visualization.layers?.find(l => l.layerId === layerId)?.xAccessor;
    const yAccessors = visualization.layers?.find(l => l.layerId === layerId)?.accessors || [];
    const splitAccessor = visualization.layers?.find(l => l.layerId === layerId)?.splitAccessor;
    
    // Also check for metric visualization accessors
    const metricAccessor = visualization.metricAccessor;
    const secondaryMetricAccessor = visualization.secondaryMetricAccessor;
    const maxAccessor = visualization.maxAccessor;
    const breakdownByAccessor = visualization.breakdownByAccessor;
    
    // Parse columns
    for (const columnId of columnOrder) {
      const column = columns[columnId];
      if (!column) continue;
      
      const parsed = parseColumn(column, columnId);
      
      if (parsed.type === 'dimension') {
        // Determine if this is a primary dimension, breakdown, or slice
        if (columnId === xAccessor) {
          result.dimensions.push(parsed.data);
        } else if (columnId === splitAccessor || columnId === breakdownByAccessor) {
          result.breakdown.push(parsed.data);
        } else if (column.isBucketed) {
          // For pie charts, non-x dimensions are slices/dimensions
          result.dimensions.push(parsed.data);
        }
      } else {
        // This is a metric
        if (columnId === metricAccessor) {
          result.primaryMetric = parsed.data;
        } else {
          result.metrics.push(parsed.data);
        }
      }
    }
  }
  
  // If no primary metric was identified but we have metrics, use the first one
  if (!result.primaryMetric && result.metrics.length > 0) {
    result.primaryMetric = result.metrics.shift();
  }
  
  return result;
}

/**
 * Decompile a Lens metric panel
 */
function decompileLensMetric(panel, dataView) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const state = attrs.state || {};
  const parsed = parseLensLayers(state);
  
  const lensConfig = {
    type: 'metric',
    data_view: dataView
  };
  
  // Add primary metric
  if (parsed.primaryMetric) {
    lensConfig.primary = parsed.primaryMetric;
  } else if (parsed.metrics.length > 0) {
    lensConfig.primary = parsed.metrics[0];
  } else {
    lensConfig.primary = { aggregation: 'count' };
  }
  
  // Add secondary metric if present
  if (parsed.metrics.length > 0) {
    lensConfig.secondary = parsed.metrics[0];
  }
  
  // Add breakdown if present
  if (parsed.breakdown.length > 0) {
    lensConfig.breakdown = parsed.breakdown[0];
  } else if (parsed.dimensions.length > 0) {
    // For metrics, dimensions are often used as breakdown
    lensConfig.breakdown = parsed.dimensions[0];
  }
  
  return lensConfig;
}

/**
 * Decompile a Lens pie chart panel
 */
function decompileLensPie(panel, dataView) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const state = attrs.state || {};
  const parsed = parseLensLayers(state);
  
  const lensConfig = {
    type: 'pie',
    data_view: dataView
  };
  
  // Pie charts use dimensions as slices
  if (parsed.dimensions.length > 0) {
    lensConfig.dimensions = parsed.dimensions;
  }
  
  // Add metrics
  if (parsed.primaryMetric) {
    lensConfig.metrics = [parsed.primaryMetric, ...parsed.metrics];
  } else if (parsed.metrics.length > 0) {
    lensConfig.metrics = parsed.metrics;
  } else {
    lensConfig.metrics = [{ aggregation: 'count' }];
  }
  
  // Extract appearance settings
  const viz = state.visualization || {};
  if (viz.shape === 'donut') {
    lensConfig.appearance = lensConfig.appearance || {};
    lensConfig.appearance.shape = 'donut';
  }
  
  return lensConfig;
}

/**
 * Decompile a Lens XY chart panel (line, bar, area)
 */
function decompileLensXY(panel, dataView) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const state = attrs.state || {};
  const viz = state.visualization || {};
  
  // Determine chart type from visualization layers
  const layers = viz.layers || [];
  const primaryLayer = layers.find(l => l.layerType === 'data') || layers[0] || {};
  const chartType = getXYChartType(primaryLayer);
  
  const parsed = parseLensLayers(state);
  
  const lensConfig = {
    type: chartType,
    data_view: dataView
  };
  
  // Add dimension (typically x-axis for time series)
  if (parsed.dimensions.length === 1) {
    lensConfig.dimension = parsed.dimensions[0];
  } else if (parsed.dimensions.length > 1) {
    lensConfig.dimensions = parsed.dimensions;
  }
  
  // Add metrics
  if (parsed.primaryMetric) {
    lensConfig.metrics = [parsed.primaryMetric, ...parsed.metrics];
  } else if (parsed.metrics.length > 0) {
    lensConfig.metrics = parsed.metrics;
  } else {
    lensConfig.metrics = [{ aggregation: 'count' }];
  }
  
  // Add breakdown if present
  if (parsed.breakdown.length > 0) {
    if (parsed.breakdown.length === 1) {
      lensConfig.breakdown = parsed.breakdown[0];
    } else {
      lensConfig.breakdown = parsed.breakdown;
    }
  }
  
  // Extract legend settings
  const legend = viz.legend || {};
  if (legend.isVisible === false) {
    lensConfig.legend = { show: false };
  } else if (legend.position && legend.position !== 'right') {
    lensConfig.legend = { position: legend.position };
  }
  
  return lensConfig;
}

/**
 * Decompile a Lens datatable panel
 */
function decompileLensDatatable(panel, dataView) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const state = attrs.state || {};
  const parsed = parseLensLayers(state);
  
  const lensConfig = {
    type: 'table',
    data_view: dataView
  };
  
  // Tables use dimensions as row groupings
  if (parsed.dimensions.length > 0) {
    lensConfig.dimensions = parsed.dimensions;
  }
  
  // Add metrics as columns
  if (parsed.primaryMetric) {
    lensConfig.metrics = [parsed.primaryMetric, ...parsed.metrics];
  } else if (parsed.metrics.length > 0) {
    lensConfig.metrics = parsed.metrics;
  } else {
    lensConfig.metrics = [{ aggregation: 'count' }];
  }
  
  return lensConfig;
}

/**
 * Decompile a Lens gauge panel
 */
function decompileLensGauge(panel, dataView) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const state = attrs.state || {};
  const parsed = parseLensLayers(state);
  const viz = state.visualization || {};
  
  const lensConfig = {
    type: 'gauge',
    data_view: dataView
  };
  
  // Add primary metric
  if (parsed.primaryMetric) {
    lensConfig.metric = parsed.primaryMetric;
  } else if (parsed.metrics.length > 0) {
    lensConfig.metric = parsed.metrics[0];
  } else {
    lensConfig.metric = { aggregation: 'count' };
  }
  
  // Extract gauge appearance
  if (viz.shape) {
    lensConfig.appearance = { shape: viz.shape };
  }
  
  return lensConfig;
}

/**
 * Decompile a Lens heatmap panel
 */
function decompileLensHeatmap(panel, dataView) {
  const attrs = panel.embeddableConfig?.attributes || {};
  const state = attrs.state || {};
  const parsed = parseLensLayers(state);
  
  const lensConfig = {
    type: 'heatmap',
    data_view: dataView
  };
  
  // Heatmaps typically have x and y axes
  if (parsed.dimensions.length >= 2) {
    lensConfig.x_axis = parsed.dimensions[0];
    lensConfig.y_axis = parsed.dimensions[1];
  } else if (parsed.dimensions.length === 1) {
    lensConfig.x_axis = parsed.dimensions[0];
  }
  
  // Add value metric
  if (parsed.primaryMetric) {
    lensConfig.value = parsed.primaryMetric;
  } else if (parsed.metrics.length > 0) {
    lensConfig.value = parsed.metrics[0];
  } else {
    lensConfig.value = { aggregation: 'count' };
  }
  
  return lensConfig;
}

/**
 * Decompile a single panel
 */
function decompilePanel(panel) {
  const grid = panel.gridData || {};
  const result = {};
  
  // Only add title if present and non-empty
  if (panel.title) {
    result.title = panel.title;
  }
  
  // Add grid positioning
  result.grid = {
    x: grid.x || 0,
    y: grid.y || 0,
    w: grid.w || 24,
    h: grid.h || 15
  };
  
  // Handle different panel types
  if (panel.type === 'visualization') {
    // Legacy visualization - try to extract basic info
    result.lens = {
      type: 'metric',
      data_view: extractDataView(panel),
      primary: { aggregation: 'count' }
    };
    result._comment = 'Legacy visualization - may need manual adjustment';
  } else if (panel.type === 'markdown') {
    const markdown = panel.embeddableConfig?.savedVis?.params?.markdown ||
                     panel.embeddableConfig?.panelConfig?.markdown ||
                     '';
    result.markdown = {
      content: markdown
    };
  } else if (panel.type === 'links') {
    // Handle links panel
    const linksConfig = panel.embeddableConfig || {};
    result.links = {
      links: (linksConfig.links || []).map(link => ({
        label: link.label || '',
        type: link.type || 'dashboard',
        destination: link.destination || link.dashboardId || ''
      }))
    };
  } else if (panel.type === 'lens') {
    const attrs = panel.embeddableConfig?.attributes || {};
    const vizType = attrs.visualizationType || 'lnsMetric';
    const dataView = extractDataView(panel);
    
    // Route to appropriate decompiler based on visualization type
    switch (vizType) {
      case 'lnsMetric':
        result.lens = decompileLensMetric(panel, dataView);
        break;
      case 'lnsPie':
        result.lens = decompileLensPie(panel, dataView);
        break;
      case 'lnsXY':
        result.lens = decompileLensXY(panel, dataView);
        break;
      case 'lnsDatatable':
        result.lens = decompileLensDatatable(panel, dataView);
        break;
      case 'lnsGauge':
        result.lens = decompileLensGauge(panel, dataView);
        break;
      case 'lnsHeatmap':
        result.lens = decompileLensHeatmap(panel, dataView);
        break;
      case 'lnsTagcloud':
        // Tag cloud - treat similar to pie
        result.lens = decompileLensPie(panel, dataView);
        result.lens.type = 'tagcloud';
        break;
      default:
        // Unknown Lens type - provide basic structure
        result.lens = {
          type: vizType.replace('lns', '').toLowerCase(),
          data_view: dataView,
          primary: { aggregation: 'count' }
        };
        result._comment = `Unknown Lens type: ${vizType} - may need manual adjustment`;
    }
  }
  
  return result;
}

/**
 * Dashboard decompiler (converts Kibana JSON to YAML)
 */
async function decompileDashboard(dashboard) {
  // Ensure yaml is available - load dynamically if needed
  try {
    await ensureYamlLoaded();
  } catch (e) {
    console.error('[Decompile] Failed to load yaml:', e);
  }
  
  if (!yaml) {
    console.error('[Decompile] yaml still not available. window.jsyaml:', typeof window.jsyaml, 'jsyaml:', typeof jsyaml);
    throw new Error('js-yaml library failed to load. Check browser console for errors.');
  }
  
  if (!dashboard) {
    throw new Error('Dashboard is null or undefined');
  }
  
  console.log('[Decompile] Dashboard structure:', {
    hasAttributes: !!dashboard.attributes,
    hasReferences: !!dashboard.references,
    keys: Object.keys(dashboard)
  });
  
  const attrs = dashboard.attributes || {};
  const references = dashboard.references || [];
  
  // Parse panels
  let panels = [];
  try {
    panels = JSON.parse(attrs.panelsJSON || '[]');
  } catch (e) {
    console.error('Failed to parse panels:', e);
  }
  
  // Build dashboard object
  const dashboardObj = {
    name: attrs.title || 'Untitled Dashboard'
  };
  
  // Add description if present
  if (attrs.description) {
    dashboardObj.description = attrs.description;
  }
  
  // Parse and add controls
  const controls = decompileControls(attrs.controlGroupInput, references);
  if (controls.length > 0) {
    dashboardObj.controls = controls;
  }
  
  // Parse and add filters
  const filters = decompileFilters(attrs.kibanaSavedObjectMeta?.searchSourceJSON);
  if (filters.length > 0) {
    dashboardObj.filters = filters;
  }
  
  // Add panels
  dashboardObj.panels = panels.map(panel => decompilePanel(panel));
  
  // Build YAML structure
  const yamlObj = {
    dashboards: [dashboardObj]
  };
  
  // Convert to YAML string
  // Use the yaml constant set at module load time
  return yaml.dump(yamlObj, {
    indent: 2,
    lineWidth: -1,
    noRefs: true
  });
}

/**
 * Check if current tab is viewing a dashboard and enable/disable import button
 */
async function checkDashboardViewPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const importBtn = document.getElementById('import-dashboard');
    
    if (!importBtn) {
      console.log('[Import] Import button not found in DOM');
      return;
    }
    
    if (!tab) {
      console.log('[Import] No active tab found');
      importBtn.disabled = true;
      return;
    }
    
    // Check if URL is a dashboard view page
    const hasViewPath = tab.url && tab.url.includes('/view/');
    const isKibanaPage = tab.url && (tab.url.includes('/app/dashboards') || tab.url.includes('/app/kibana'));
    const isDashboardViewPage = isKibanaPage && hasViewPath;
    
    // console.log('[Import] Tab URL:', tab.url);
    // console.log('[Import] Is Kibana page:', isKibanaPage);
    // console.log('[Import] Has /view/ path:', hasViewPath);
    // console.log('[Import] Button should be enabled:', isDashboardViewPage);
    
    if (isDashboardViewPage) {
      importBtn.disabled = false;
      importBtn.title = 'Import Current Dashboard into Editor';
      importBtn.style.opacity = '1';
    } else {
      importBtn.disabled = true;
      importBtn.title = `Import Current Dashboard (navigate to a dashboard view page first)\nCurrent URL: ${tab.url || 'unknown'}`;
      importBtn.style.opacity = '0.5';
    }
  } catch (error) {
    console.error('[Import] Error checking dashboard page:', error);
  }
}

/**
 * Import the current dashboard from Kibana into the editor
 */
async function handleImportDashboard() {
  try {
    updateStatus('compiling', 'Importing dashboard...');
    
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.url) {
      showError('No active tab found');
      updateStatus('error', 'Import failed');
      return;
    }
    
    // Check if we're on a dashboard view page
    const isDashboardViewPage = tab.url.includes('/app/dashboards') || tab.url.includes('/app/kibana');
    const hasViewPath = tab.url.includes('/view/');
    
    if (!isDashboardViewPage || !hasViewPath) {
      showError(
        'Import only works when viewing a specific dashboard.\n\n' +
        'Please navigate to a dashboard view page (e.g., /app/dashboards#/view/dashboard-id) and try again.'
      );
      updateStatus('ready', 'Import cancelled');
      return;
    }
    
    // Extract dashboard ID from current URL
    // Handle both hash-based routing (/dashboards#/view/id) and direct routes
    let dashboardId = null;
    
    // Try hash-based routing first (most common)
    let match = tab.url.match(/#\/view\/([^?&]+)/);
    if (match) {
      dashboardId = decodeURIComponent(match[1]);
    } else {
      // Try direct routing
      match = tab.url.match(/\/view\/([^?#&]+)/);
      if (match) {
        dashboardId = decodeURIComponent(match[1]);
      }
    }
    
    console.log('[Import] URL:', tab.url);
    console.log('[Import] Extracted dashboard ID:', dashboardId);
    
    if (!dashboardId) {
      showError('Could not extract dashboard ID from current page URL:\n' + tab.url + '\n\nExpected URL format: .../dashboards#/view/DASHBOARD_ID');
      updateStatus('error', 'Import failed');
      return;
    }
    
    try {
      // Try to use content script first (better API access)
      let dashboard = null;
      
      try {
        console.log('[Import] Trying to fetch via content script...');
        const response = await chrome.tabs.sendMessage(tab.id, {
          action: 'fetch-dashboard',
          dashboardId: dashboardId
        });
        
        if (response && response.success && response.dashboard) {
          dashboard = response.dashboard;
          console.log('[Import] Successfully fetched via content script');
        } else if (response && !response.success) {
          console.log('[Import] Content script returned error:', response.error);
        }
      } catch (e) {
        console.log('[Import] Content script method failed:', e.message);
      }
      
      // If content script worked, skip to decompilation
      if (dashboard) {
        console.log('[Import] Dashboard fetched:', dashboard);
        
        if (!dashboard.attributes) {
          throw new Error('Dashboard has no attributes. Dashboard structure: ' + JSON.stringify(Object.keys(dashboard)));
        }
        
        const yaml = await decompileDashboard(dashboard);
        
        if (window.editor) {
          window.editor.setValue(yaml);
          updateStatus('ready', 'Dashboard imported successfully!');
        } else {
          showError('Editor not ready');
          updateStatus('error', 'Import failed');
        }
        return;
      }
      
      // Fallback: Use the export API (same pattern as upload uses import API)
      console.log('[Import] Trying export API via chrome.scripting...');
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: async (dashId) => {
          try {
            // Use the saved_objects _export API (counterpart to _import that upload uses)
            const response = await fetch('/api/saved_objects/_export', {
              method: 'POST',
              credentials: 'include',
              headers: {
                'kbn-xsrf': 'true',
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                objects: [{ type: 'dashboard', id: dashId }],
                includeReferencesDeep: false
              })
            });
            
            if (!response.ok) {
              const errorText = await response.text();
              return { 
                error: true, 
                status: response.status,
                statusText: response.statusText,
                body: errorText
              };
            }
            
            // Parse NDJSON response to find dashboard object
            const ndjson = await response.text();
            const lines = ndjson.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
              try {
                const obj = JSON.parse(line);
                if (obj.type === 'dashboard') {
                  return { error: false, data: obj, source: 'export_api' };
                }
              } catch (e) {
                // Skip invalid lines
                continue;
              }
            }
            
            return { 
              error: true, 
              message: 'Dashboard not found in export response',
              body: ndjson.substring(0, 500)
            };
          } catch (err) {
            return { 
              error: true, 
              message: err.message,
              stack: err.stack
            };
          }
        },
        args: [dashboardId]
      });
      
      if (!results || !results[0] || !results[0].result) {
        throw new Error('No response from content script');
      }
      
      const result = results[0].result;
      console.log('[Import] Fetch result:', result);
      
      if (result.error) {
        let errorMsg = 'Failed to fetch dashboard';
        
        if (result.message) {
          errorMsg = result.message;
        } else if (result.status) {
          errorMsg = `Failed to fetch dashboard (${result.status}): ${result.statusText}\n${result.body}`;
        }
        
        if (result.hint) {
          errorMsg += '\n\n' + result.hint;
        }
        
        throw new Error(errorMsg);
      }
      
      console.log('[Import] Dashboard fetched from:', result.source || 'unknown');
      
      dashboard = result.data;
      console.log('[Import] Dashboard fetched:', dashboard);
      
      if (!dashboard) {
        throw new Error('Dashboard data is null or undefined');
      }
      
      if (!dashboard.attributes) {
        throw new Error('Dashboard has no attributes. Dashboard structure: ' + JSON.stringify(Object.keys(dashboard)));
      }
      
      // Decompile dashboard to YAML (using the jsyaml library already loaded in sidepanel)
      const yaml = await decompileDashboard(dashboard);
      
      // Load into editor
      if (window.editor) {
        window.editor.setValue(yaml);
        updateStatus('ready', 'Dashboard imported successfully!');
      } else {
        showError('Editor not ready');
        updateStatus('error', 'Import failed');
      }
      
    } catch (error) {
      console.error('[Import] Import error:', error);
      showError('Import failed: ' + error.message);
      updateStatus('error', 'Import failed');
    }
    
  } catch (error) {
    console.error('[Import] Unexpected error:', error);
    showError('Import failed: ' + error.message);
    updateStatus('error', 'Import failed');
  }
}
