/**
 * Content Script - Injects into Kibana pages to enable dashboard export
 */

// Detect if we're on a Kibana dashboard page
function isKibanaDashboardPage() {
  // Only show on dashboard view pages, not listing or other pages
  return (window.location.href.includes('/app/dashboards') || 
          window.location.href.includes('/app/kibana')) &&
         window.location.href.includes('/view/');
}

// Extract dashboard ID from URL
function extractDashboardId() {
  const match = window.location.href.match(/\/view\/([^?#]+)/);
  return match ? match[1] : null;
}

// Inject export button into Kibana UI
function injectExportButton() {
  // Look for Kibana toolbar
  const toolbar = document.querySelector('[data-test-subj="dashboardEditMode"]') ||
                  document.querySelector('.euiHeader__section') ||
                  document.querySelector('[data-test-subj="top-nav"]');
  
  if (!toolbar) {
    console.log('[Dashboard Builder] Kibana toolbar not found, will retry...');
    return false;
  }
  
  // Check if already injected
  if (document.getElementById('kb-dashboard-export-btn')) {
    return true;
  }
  
  // Create export button
  const button = document.createElement('button');
  button.id = 'kb-dashboard-export-btn';
  button.className = 'euiButton euiButton--primary euiButton--small';
  button.innerHTML = `
    <span class="euiButton__content">
      <span class="euiButton__text">📋 Export to YAML</span>
    </span>
  `;
  button.style.cssText = `
    margin-left: 8px;
    background: #006bb4;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  `;
  
  button.addEventListener('click', handleExportClick);
  
  toolbar.appendChild(button);
  console.log('[Dashboard Builder] Export button injected');
  return true;
}

// Handle export button click
async function handleExportClick() {
  const dashboardId = extractDashboardId();
  
  if (!dashboardId) {
    alert('Could not detect dashboard ID. Please open a specific dashboard.');
    return;
  }
  
  try {
    const button = document.getElementById('kb-dashboard-export-btn');
    button.disabled = true;
    button.innerHTML = '<span class="euiButton__content"><span class="euiButton__text">⏳ Exporting...</span></span>';
    
    // Fetch dashboard from Kibana API
    const dashboard = await fetchDashboard(dashboardId);
    
    // Convert to YAML
    const yaml = await decompileDashboard(dashboard);
    
    // Open side panel with YAML
    chrome.runtime.sendMessage({
      action: 'open-sidepanel',
      yaml: yaml
    });
    
    button.disabled = false;
    button.innerHTML = '<span class="euiButton__content"><span class="euiButton__text">✓ Exported!</span></span>';
    
    setTimeout(() => {
      button.innerHTML = '<span class="euiButton__content"><span class="euiButton__text">📋 Export to YAML</span></span>';
    }, 2000);
    
  } catch (error) {
    console.error('[Dashboard Builder] Export failed:', error);
    alert('Export failed: ' + error.message);
    
    const button = document.getElementById('kb-dashboard-export-btn');
    button.disabled = false;
    button.innerHTML = '<span class="euiButton__content"><span class="euiButton__text">📋 Export to YAML</span></span>';
  }
}

// Fetch dashboard from Kibana API
async function fetchDashboard(dashboardId) {
  const response = await fetch(
    `/api/saved_objects/dashboard/${dashboardId}`,
    {
      credentials: 'include',
      headers: {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard: ${response.statusText}`);
  }
  
  return await response.json();
}

// Decompile dashboard controls
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

// Decompile dashboard filters
function decompileFilters(filtersJSON) {
  if (!filtersJSON) return [];
  
  let filters = [];
  try {
    filters = typeof filtersJSON === 'string' ? JSON.parse(filtersJSON) : filtersJSON;
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

// Dashboard decompiler (converts Kibana JSON to YAML)
async function decompileDashboard(dashboard) {
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
  return jsyaml.dump(yamlObj, {
    indent: 2,
    lineWidth: -1,
    noRefs: true
  });
}

// Extract data view ID from panel references
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

// Determine XY chart type from layer configuration
function getXYChartType(layer) {
  const seriesType = layer?.seriesType || 'line';
  if (seriesType.includes('bar')) return 'bar';
  if (seriesType.includes('area')) return 'area';
  return 'line';
}

// Parse a single column from Lens state
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

// Parse Lens layers to extract dimensions, metrics, and breakdown
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

// Decompile a Lens metric panel
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

// Decompile a Lens pie chart panel
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

// Decompile a Lens XY chart panel (line, bar, area)
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

// Decompile a Lens datatable panel
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

// Decompile a Lens gauge panel
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

// Decompile a Lens heatmap panel
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

// Decompile a single panel
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

// Listen for requests from side panel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'upload-dashboard') {
    handleUploadDashboard(request.ndjson, request.kibanaUrl)
      .then(() => sendResponse({ success: true }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (request.action === 'fetch-dashboard') {
    fetchDashboard(request.dashboardId)
      .then(dashboard => sendResponse({ success: true, dashboard: dashboard }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
});

// Upload dashboard to Kibana using the import API
async function handleUploadDashboard(ndjson, kibanaUrl) {
  console.log('[Dashboard Builder] Uploading to:', kibanaUrl);
  
  try {
    // Use Kibana's saved objects import API (same as UI uses)
    const uploadUrl = `${kibanaUrl}/api/saved_objects/_import?overwrite=true`;
    
    console.log('[Dashboard Builder] Using import API:', uploadUrl);
    
    // Create FormData with NDJSON file
    const formData = new FormData();
    const blob = new Blob([ndjson], { type: 'application/ndjson' });
    formData.append('file', blob, 'dashboard.ndjson');
    
    const response = await fetch(uploadUrl, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'kbn-xsrf': 'true'
        // Don't set Content-Type - let browser set it with boundary for FormData
      },
      body: formData
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Dashboard Builder] Upload failed:', response.status, errorText);
      
      let errorDetails = errorText;
      try {
        const errorObj = JSON.parse(errorText);
        if (errorObj.message) {
          errorDetails = errorObj.message;
        }
        if (errorObj.error) {
          errorDetails = `${errorObj.error}: ${errorDetails}`;
        }
      } catch (e) {
        // Use raw error text if not JSON
      }
      
      throw new Error(`Upload failed (${response.status}): ${errorDetails}`);
    }
    
    // Parse success response
    const responseObj = await response.json();
    const successCount = responseObj.successCount || 0;
    const errorCount = responseObj.errors?.length || 0;
    
    console.log('[Dashboard Builder] Import results:', {
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
    
    console.log('[Dashboard Builder] Successfully uploaded', successCount, 'object(s)');
  } catch (error) {
    // Check for common network/SSL errors
    if (error.message.includes('Failed to fetch') || 
        (error.name === 'TypeError' && error.message.includes('fetch') && !error.message.includes('Upload failed'))) {
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

// Initialize when DOM is ready
if (isKibanaDashboardPage()) {
  // Try to inject button immediately
  if (!injectExportButton()) {
    // If failed, wait for Kibana to fully load
    const observer = new MutationObserver(() => {
      if (injectExportButton()) {
        observer.disconnect();
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    // Give up after 10 seconds
    setTimeout(() => observer.disconnect(), 10000);
  }
}

console.log('[Dashboard Builder] Content script loaded');
