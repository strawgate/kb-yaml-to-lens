/**
 * Editor - Handles Monaco editor initialization and live compilation
 */

let editor = null;
let debounceTimer = null;
let monacoInitialized = false;
const DEBOUNCE_DELAY = 500; // ms

// Sample dashboard YAML
const SAMPLE_YAML = `---
dashboards:
  - name: Sample Dashboard
    description: A simple example dashboard with various panel types
    panels:
      - title: Welcome Panel
        grid: { x: 0, y: 0, w: 48, h: 5 }
        markdown:
          content: |
            # Welcome to Dashboard Builder!
            
            Edit this YAML to see live preview on the right.
      
      - title: Total Documents
        grid: { x: 0, y: 5, w: 24, h: 15 }
        lens:
          type: metric
          data_view: logs-*
          primary:
            aggregation: count
            label: Total Docs
      
      - title: Status Breakdown
        grid: { x: 24, y: 5, w: 24, h: 15 }
        lens:
          type: pie
          data_view: logs-*
          metrics:
            - aggregation: count
          dimensions:
            - field: status
              type: values
              size: 5
`;

/**
 * Initialize everything when DOM is ready
 */
document.addEventListener('DOMContentLoaded', async () => {
  console.log('[Editor] DOMContentLoaded fired');
  console.log('[Editor] window.pythonCompiler exists?', typeof window.pythonCompiler !== 'undefined');
  console.log('[Editor] Initializing...');
  
  // Show loading overlay
  showLoadingOverlay('Initializing Python runtime...');
  
  // Initialize Monaco editor
  await initMonacoEditor();
  
  // Check for pending YAML from content script (e.g., from Kibana export)
  try {
    const { pendingYaml } = await chrome.storage.local.get('pendingYaml');
    if (pendingYaml) {
      editor.setValue(pendingYaml);
      chrome.storage.local.remove('pendingYaml');
      console.log('[Editor] Loaded pending YAML from content script');
    }
  } catch (error) {
    console.log('[Editor] Could not check for pending YAML:', error);
  }
  
  // Start Python initialization in background
  try {
    if (!window.pythonCompiler) {
      throw new Error('window.pythonCompiler is not defined. Check if pyodide-loader.js loaded correctly.');
    }
    console.log('[Editor] Starting Python compiler initialization...');
    await window.pythonCompiler.initialize();
    hideLoadingOverlay();
    updateStatus('ready', 'Ready!');
    
    // Trigger initial compilation
    compileAndPreview();
  } catch (error) {
    hideLoadingOverlay();
    updateStatus('error', 'Initialization failed');
    console.error('[Editor] Initialization error:', error);
    const errorMessage = error?.message || error?.toString?.() || String(error) || 'Unknown error';
    showError('Failed to initialize compiler: ' + errorMessage);
  }
  
  // Setup event listeners
  setupEventListeners();
  
  // Setup resizer
  setupResizer();
});

/**
 * Initialize Monaco Editor (local bundle) or fall back to textarea
 * 
 * Note: Monaco has issues with duplicate module definitions in Chrome extensions
 * when the side panel is reopened. Using textarea fallback for reliability.
 */
function initMonacoEditor() {
  return new Promise((resolve, reject) => {
    const container = document.getElementById('editor-container');
    
    // Prevent double initialization
    if (monacoInitialized || editor !== null) {
      console.log('[Editor] Editor already initialized, skipping');
      resolve();
      return;
    }
    
    // Use textarea fallback - it's reliable and works perfectly in Chrome extensions
    console.log('[Editor] Using textarea editor');
    monacoInitialized = true;
    initTextareaFallback(container);
    resolve();
  });
}

/**
 * Create the Monaco editor instance
 */
function createMonacoEditor(container) {
  // Create Monaco editor with YAML language and VS Code dark theme
  editor = monaco.editor.create(container, {
    value: SAMPLE_YAML,
    language: 'yaml',
    theme: 'vs-dark',
    automaticLayout: true,
    minimap: { enabled: false },
    fontSize: 13,
    lineHeight: 20,
    padding: { top: 12, bottom: 12 },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    tabSize: 2,
    insertSpaces: true,
    renderWhitespace: 'selection',
    lineNumbers: 'on',
    folding: true,
    bracketPairColorization: { enabled: true },
    scrollbar: {
      verticalScrollbarSize: 10,
      horizontalScrollbarSize: 10
    }
  });

  // Listen for content changes with debouncing
  editor.onDidChangeModelContent(() => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(compileAndPreview, DEBOUNCE_DELAY);
  });
  
  // Expose editor globally for actions.js
  window.editor = editor;

  console.log('[Editor] Monaco editor initialized');
}

/**
 * Initialize textarea fallback when Monaco is not available
 */
function initTextareaFallback(container) {
  const textarea = document.createElement('textarea');
  textarea.id = 'yaml-editor';
  textarea.value = SAMPLE_YAML;
  textarea.style.cssText = `
    width: 100%;
    height: 100%;
    background: #1e1e1e;
    color: #d4d4d4;
    border: none;
    padding: 12px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 20px;
    resize: none;
    outline: none;
    tab-size: 2;
  `;
  container.innerHTML = '';
  container.appendChild(textarea);
  
  // Create a wrapper object to match Monaco editor API
  editor = {
    getValue: () => textarea.value,
    setValue: (val) => { textarea.value = val; },
    onDidChangeModelContent: (callback) => {
      textarea.addEventListener('input', callback);
    }
  };
  
  // Expose editor globally for actions.js
  window.editor = editor;
  
  // Listen for content changes with debouncing
  textarea.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(compileAndPreview, DEBOUNCE_DELAY);
  });
  
  console.log('[Editor] Textarea fallback initialized');
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Tab switching
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const tabName = tab.dataset.tab;
      switchTab(tabName);
    });
  });
  
  // Close error
  document.getElementById('close-error')?.addEventListener('click', () => {
    hideError();
  });
}

/**
 * Setup split pane resizer
 */
function setupResizer() {
  const resizer = document.querySelector('.resizer');
  const leftPane = document.querySelector('.editor-pane');
  
  let isResizing = false;
  
  resizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.body.style.cursor = 'col-resize';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    
    const containerWidth = document.querySelector('.split-pane').offsetWidth;
    const newWidth = (e.clientX / containerWidth) * 100;
    
    if (newWidth > 20 && newWidth < 80) {
      leftPane.style.flex = `0 0 ${newWidth}%`;
    }
  });
  
  document.addEventListener('mouseup', () => {
    isResizing = false;
    document.body.style.cursor = 'default';
  });
}

/**
 * Compile YAML and update preview
 */
async function compileAndPreview() {
  const yamlContent = editor.getValue();
  
  if (!yamlContent.trim()) {
    return;
  }
  
  try {
    updateStatus('compiling', 'Compiling...');
    
    const result = await window.pythonCompiler.compile(yamlContent);
    
    if (result.success) {
      updatePreview(result.ndjson);
      hideError();
      updateStatus('ready', `Compiled in ${result.compileTime}ms`);
    } else {
      showError(result.error);
      updateStatus('error', 'Compilation failed');
    }
  } catch (error) {
    showError('Unexpected error: ' + error.message);
    updateStatus('error', 'Compilation failed');
  }
}

/**
 * Switch between preview tabs
 */
function switchTab(tabName) {
  // Update tab buttons
  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.tab === tabName);
  });
  
  // Update tab content
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.toggle('active', content.id === `${tabName}-preview`);
  });
}

/**
 * Update status indicator
 */
function updateStatus(state, message) {
  const statusEl = document.getElementById('status');
  statusEl.className = `status ${state}`;
  statusEl.textContent = message;
}

/**
 * Show error panel
 */
function showError(message) {
  const errorPanel = document.getElementById('error-panel');
  const errorMessage = document.getElementById('error-message');
  
  errorMessage.textContent = message;
  errorPanel.classList.remove('hidden');
}

/**
 * Hide error panel
 */
function hideError() {
  const errorPanel = document.getElementById('error-panel');
  errorPanel.classList.add('hidden');
}

/**
 * Show loading overlay
 */
function showLoadingOverlay(message) {
  const overlay = document.createElement('div');
  overlay.className = 'loading-overlay';
  overlay.id = 'loading-overlay';
  overlay.innerHTML = `
    <div class="loading-spinner"></div>
    <div class="loading-text">${message}</div>
  `;
  document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.remove();
  }
}
