/**
 * Pyodide Loader - Initializes Python runtime and provides compilation interface
 * 
 * This module loads the full dashboard_compiler Python package into the browser
 * using Pyodide (Python compiled to WebAssembly).
 */

class PythonCompiler {
  constructor() {
    this.pyodide = null;
    this.isReady = false;
    this.initPromise = null;
    this.initStartTime = null;
  }

  /**
   * Initialize Pyodide and load Python compiler
   */
  async initialize() {
    if (this.initPromise) return this.initPromise;

    this.initPromise = (async () => {
      try {
        this.initStartTime = Date.now();
        console.log('[Pyodide] Starting initialization...');

        // Load Pyodide from local bundle
        const script = document.createElement('script');
        script.src = chrome.runtime.getURL('lib/pyodide/pyodide.js');
        document.head.appendChild(script);

        await new Promise((resolve, reject) => {
          script.onload = resolve;
          script.onerror = (event) => {
            reject(new Error(`Failed to load Pyodide script from local bundle. Make sure you've run setup.sh to download Pyodide.`));
          };
        });

        console.log('[Pyodide] Script loaded, initializing runtime...');
        
        // Initialize Pyodide with local indexURL (fully offline)
        const indexURL = chrome.runtime.getURL('lib/pyodide/');
        console.log('[Pyodide] Using local indexURL:', indexURL);
        
        this.pyodide = await loadPyodide({
          indexURL: indexURL,
          fullStdLib: false
        });
        
        if (this.pyodide.setCdnUrl) {
          this.pyodide.setCdnUrl(indexURL);
          console.log('[Pyodide] Overrode CDN URL to use local files');
        }

        console.log('[Pyodide] Runtime initialized, installing packages...');

        // Load micropip for package installation
        console.log('[Pyodide] Loading micropip...');
        try {
          await this.pyodide.loadPackage(['micropip']);
          console.log('[Pyodide] ✓ micropip loaded');
        } catch (micropipError) {
          console.error('[Pyodide] Failed to load micropip:', micropipError);
        }

        // Load pyyaml
        console.log('[Pyodide] Loading pyyaml...');
        let pyyamlLoaded = false;
        try {
          await this.pyodide.loadPackage(['pyyaml']);
          console.log('[Pyodide] ✓ pyyaml loaded via loadPackage');
          pyyamlLoaded = true;
        } catch (loadError) {
          console.warn('[Pyodide] loadPackage failed for pyyaml:', loadError.message);
          console.log('[Pyodide] Trying micropip install from local wheel...');
          
          try {
            const wheelUrl = chrome.runtime.getURL('lib/pyodide/pyyaml-6.0.2-cp313-cp313-pyodide_2025_0_wasm32.whl');
            const response = await fetch(wheelUrl);
            if (!response.ok) {
              throw new Error(`Failed to fetch wheel: ${response.status} ${response.statusText}`);
            }
            const wheelData = await response.arrayBuffer();
            this.pyodide.FS.writeFile('/tmp/pyyaml.whl', new Uint8Array(wheelData));
            
            await this.pyodide.runPythonAsync(`
import micropip
await micropip.install('emfs:/tmp/pyyaml.whl')
            `);
            pyyamlLoaded = true;
            console.log('[Pyodide] ✓ pyyaml installed via micropip');
          } catch (micropipError) {
            console.error('[Pyodide] micropip install failed:', micropipError);
          }
        }

        // Install pydantic and dependencies (required for the compiler)
        console.log('[Pyodide] Loading pydantic and dependencies...');
        try {
          // Try loadPackage first (uses local wheels if available)
          await this.pyodide.loadPackage(['typing_extensions', 'annotated_types', 'pydantic_core', 'pydantic']);
          console.log('[Pyodide] ✓ pydantic loaded via loadPackage');
        } catch (loadError) {
          console.warn('[Pyodide] loadPackage failed for pydantic:', loadError.message);
          // Fallback: install from local wheels via micropip
          console.log('[Pyodide] Trying to install pydantic from local wheels...');
          try {
            // Install dependencies in order (versions from Pyodide v0.29.1)
            const wheels = [
              'typing_extensions-4.15.0-py3-none-any.whl',
              'annotated_types-0.7.0-py3-none-any.whl',
              'pydantic_core-2.27.2-cp313-cp313-pyodide_2025_0_wasm32.whl',
              'pydantic-2.10.6-py3-none-any.whl'
            ];
            
            for (const wheel of wheels) {
              try {
                const wheelUrl = chrome.runtime.getURL(`lib/pyodide/${wheel}`);
                const response = await fetch(wheelUrl);
                if (!response.ok) {
                  console.warn(`[Pyodide] Could not fetch ${wheel}: ${response.status}`);
                  continue;
                }
                const wheelData = await response.arrayBuffer();
                this.pyodide.FS.writeFile(`/tmp/${wheel}`, new Uint8Array(wheelData));
                await this.pyodide.runPythonAsync(`
import micropip
await micropip.install('emfs:/tmp/${wheel}')
                `);
                console.log(`[Pyodide] ✓ Installed ${wheel}`);
              } catch (wheelError) {
                console.warn(`[Pyodide] Failed to install ${wheel}:`, wheelError.message);
              }
            }
            console.log('[Pyodide] ✓ pydantic installed via local wheels');
          } catch (micropipError) {
            console.error('[Pyodide] Failed to install pydantic:', micropipError);
            throw new Error('Failed to install pydantic - required for compilation');
          }
        }
        
        // Verify packages
        console.log('[Pyodide] Verifying package installations...');
        await this.pyodide.runPythonAsync(`
import sys
print("Python version:", sys.version)

import yaml
print("✓ yaml module available")

import pydantic
print("✓ pydantic module available, version:", pydantic.__version__)
        `);
        console.log('[Pyodide] ✓ Package verification passed');
        
        console.log('[Pyodide] Loading full dashboard compiler...');
        await this.loadCompiler();

        const initTime = ((Date.now() - this.initStartTime) / 1000).toFixed(2);
        console.log(`[Pyodide] Initialization complete in ${initTime}s`);

        this.isReady = true;
      } catch (error) {
        console.error('[Pyodide] Initialization failed:', error);
        throw new Error(`Failed to initialize Python compiler: ${error.message}`);
      }
    })();

    return this.initPromise;
  }

  /**
   * Load the full Python compiler from browser-extension/python/
   */
  async loadCompiler() {
    // Directory structure to create in Pyodide filesystem
    const directories = [
      'dashboard_compiler',
      'dashboard_compiler/controls',
      'dashboard_compiler/dashboard',
      'dashboard_compiler/filters',
      'dashboard_compiler/lsp',
      'dashboard_compiler/panels',
      'dashboard_compiler/panels/charts',
      'dashboard_compiler/panels/charts/base',
      'dashboard_compiler/panels/charts/datatable',
      'dashboard_compiler/panels/charts/esql',
      'dashboard_compiler/panels/charts/esql/columns',
      'dashboard_compiler/panels/charts/gauge',
      'dashboard_compiler/panels/charts/heatmap',
      'dashboard_compiler/panels/charts/lens',
      'dashboard_compiler/panels/charts/lens/columns',
      'dashboard_compiler/panels/charts/lens/dimensions',
      'dashboard_compiler/panels/charts/lens/metrics',
      'dashboard_compiler/panels/charts/metric',
      'dashboard_compiler/panels/charts/pie',
      'dashboard_compiler/panels/charts/tagcloud',
      'dashboard_compiler/panels/charts/xy',
      'dashboard_compiler/panels/images',
      'dashboard_compiler/panels/links',
      'dashboard_compiler/panels/markdown',
      'dashboard_compiler/panels/search',
      'dashboard_compiler/queries',
      'dashboard_compiler/sample_data',
      'dashboard_compiler/shared',
      'dashboard_compiler/tools',
    ];

    // All Python module files to load
    const modules = [
      'python/dashboard_compiler/__init__.py',
      'python/dashboard_compiler/cli.py',
      'python/dashboard_compiler/cli_context.py',
      'python/dashboard_compiler/cli_options.py',
      'python/dashboard_compiler/controls/__init__.py',
      'python/dashboard_compiler/controls/compile.py',
      'python/dashboard_compiler/controls/config.py',
      'python/dashboard_compiler/controls/types.py',
      'python/dashboard_compiler/controls/view.py',
      'python/dashboard_compiler/dashboard/__init__.py',
      'python/dashboard_compiler/dashboard/compile.py',
      'python/dashboard_compiler/dashboard/config.py',
      'python/dashboard_compiler/dashboard/view.py',
      'python/dashboard_compiler/dashboard_compiler.py',
      'python/dashboard_compiler/filters/__init__.py',
      'python/dashboard_compiler/filters/compile.py',
      'python/dashboard_compiler/filters/config.py',
      'python/dashboard_compiler/filters/view.py',
      'python/dashboard_compiler/kibana_client.py',
      'python/dashboard_compiler/loader.py',
      'python/dashboard_compiler/lsp/__init__.py',
      'python/dashboard_compiler/lsp/grid_extractor.py',
      'python/dashboard_compiler/lsp/grid_updater.py',
      'python/dashboard_compiler/lsp/server.py',
      'python/dashboard_compiler/lsp/utils.py',
      'python/dashboard_compiler/panels/__init__.py',
      'python/dashboard_compiler/panels/auto_layout.py',
      'python/dashboard_compiler/panels/base.py',
      'python/dashboard_compiler/panels/charts/__init__.py',
      'python/dashboard_compiler/panels/charts/base/__init__.py',
      'python/dashboard_compiler/panels/charts/base/compile.py',
      'python/dashboard_compiler/panels/charts/base/config.py',
      'python/dashboard_compiler/panels/charts/base/view.py',
      'python/dashboard_compiler/panels/charts/compile.py',
      'python/dashboard_compiler/panels/charts/config.py',
      'python/dashboard_compiler/panels/charts/datatable/__init__.py',
      'python/dashboard_compiler/panels/charts/datatable/compile.py',
      'python/dashboard_compiler/panels/charts/datatable/config.py',
      'python/dashboard_compiler/panels/charts/datatable/view.py',
      'python/dashboard_compiler/panels/charts/esql/columns/__init__.py',
      'python/dashboard_compiler/panels/charts/esql/columns/compile.py',
      'python/dashboard_compiler/panels/charts/esql/columns/config.py',
      'python/dashboard_compiler/panels/charts/esql/columns/view.py',
      'python/dashboard_compiler/panels/charts/gauge/__init__.py',
      'python/dashboard_compiler/panels/charts/gauge/compile.py',
      'python/dashboard_compiler/panels/charts/gauge/config.py',
      'python/dashboard_compiler/panels/charts/gauge/view.py',
      'python/dashboard_compiler/panels/charts/heatmap/__init__.py',
      'python/dashboard_compiler/panels/charts/heatmap/compile.py',
      'python/dashboard_compiler/panels/charts/heatmap/config.py',
      'python/dashboard_compiler/panels/charts/heatmap/view.py',
      'python/dashboard_compiler/panels/charts/lens/__init__.py',
      'python/dashboard_compiler/panels/charts/lens/columns/__init__.py',
      'python/dashboard_compiler/panels/charts/lens/columns/compile.py',
      'python/dashboard_compiler/panels/charts/lens/columns/view.py',
      'python/dashboard_compiler/panels/charts/lens/dimensions/__init__.py',
      'python/dashboard_compiler/panels/charts/lens/dimensions/compile.py',
      'python/dashboard_compiler/panels/charts/lens/dimensions/config.py',
      'python/dashboard_compiler/panels/charts/lens/metrics/__init__.py',
      'python/dashboard_compiler/panels/charts/lens/metrics/compile.py',
      'python/dashboard_compiler/panels/charts/lens/metrics/config.py',
      'python/dashboard_compiler/panels/charts/metric/__init__.py',
      'python/dashboard_compiler/panels/charts/metric/compile.py',
      'python/dashboard_compiler/panels/charts/metric/config.py',
      'python/dashboard_compiler/panels/charts/metric/view.py',
      'python/dashboard_compiler/panels/charts/pie/__init__.py',
      'python/dashboard_compiler/panels/charts/pie/compile.py',
      'python/dashboard_compiler/panels/charts/pie/config.py',
      'python/dashboard_compiler/panels/charts/pie/view.py',
      'python/dashboard_compiler/panels/charts/tagcloud/__init__.py',
      'python/dashboard_compiler/panels/charts/tagcloud/compile.py',
      'python/dashboard_compiler/panels/charts/tagcloud/config.py',
      'python/dashboard_compiler/panels/charts/tagcloud/view.py',
      'python/dashboard_compiler/panels/charts/view.py',
      'python/dashboard_compiler/panels/charts/xy/__init__.py',
      'python/dashboard_compiler/panels/charts/xy/compile.py',
      'python/dashboard_compiler/panels/charts/xy/config.py',
      'python/dashboard_compiler/panels/charts/xy/metrics.py',
      'python/dashboard_compiler/panels/charts/xy/view.py',
      'python/dashboard_compiler/panels/compile.py',
      'python/dashboard_compiler/panels/config.py',
      'python/dashboard_compiler/panels/images/__init__.py',
      'python/dashboard_compiler/panels/images/compile.py',
      'python/dashboard_compiler/panels/images/config.py',
      'python/dashboard_compiler/panels/images/view.py',
      'python/dashboard_compiler/panels/links/__init__.py',
      'python/dashboard_compiler/panels/links/compile.py',
      'python/dashboard_compiler/panels/links/config.py',
      'python/dashboard_compiler/panels/links/view.py',
      'python/dashboard_compiler/panels/markdown/__init__.py',
      'python/dashboard_compiler/panels/markdown/compile.py',
      'python/dashboard_compiler/panels/markdown/config.py',
      'python/dashboard_compiler/panels/markdown/view.py',
      'python/dashboard_compiler/panels/search/__init__.py',
      'python/dashboard_compiler/panels/search/compile.py',
      'python/dashboard_compiler/panels/search/config.py',
      'python/dashboard_compiler/panels/search/view.py',
      'python/dashboard_compiler/panels/types.py',
      'python/dashboard_compiler/panels/view.py',
      'python/dashboard_compiler/queries/__init__.py',
      'python/dashboard_compiler/queries/compile.py',
      'python/dashboard_compiler/queries/config.py',
      'python/dashboard_compiler/queries/types.py',
      'python/dashboard_compiler/queries/view.py',
      'python/dashboard_compiler/sample_data/__init__.py',
      'python/dashboard_compiler/sample_data/config.py',
      'python/dashboard_compiler/sample_data/loader.py',
      'python/dashboard_compiler/sample_data/timestamps.py',
      'python/dashboard_compiler/shared/__init__.py',
      'python/dashboard_compiler/shared/compile.py',
      'python/dashboard_compiler/shared/config.py',
      'python/dashboard_compiler/shared/defaults.py',
      'python/dashboard_compiler/shared/error_formatter.py',
      'python/dashboard_compiler/shared/errors.py',
      'python/dashboard_compiler/shared/filter_utils.py',
      'python/dashboard_compiler/shared/logging.py',
      'python/dashboard_compiler/shared/model.py',
      'python/dashboard_compiler/shared/view.py',
      'python/dashboard_compiler/tools/__init__.py',
      'python/dashboard_compiler/tools/disassemble.py',
      'python/dashboard_compiler/utils.py',
    ];

    // Create directory structure in Pyodide filesystem
    console.log('[Pyodide] Creating directory structure...');
    for (const dir of directories) {
      try {
        this.pyodide.FS.mkdir(`/home/pyodide/${dir}`);
      } catch (e) {
        // Directory may already exist
      }
    }

    // Load each Python module file
    console.log(`[Pyodide] Loading ${modules.length} Python modules...`);
    let loadedCount = 0;
    const errors = [];
    
    for (const modulePath of modules) {
      try {
        const url = chrome.runtime.getURL(modulePath);
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const code = await response.text();
        
        // Convert path: python/dashboard_compiler/foo.py -> dashboard_compiler/foo.py
        const fsPath = modulePath.replace('python/', '');
        this.pyodide.FS.writeFile(`/home/pyodide/${fsPath}`, code);
        loadedCount++;
      } catch (error) {
        errors.push(`${modulePath}: ${error.message}`);
        console.warn(`[Pyodide] Failed to load ${modulePath}:`, error.message);
      }
    }

    if (errors.length > 0) {
      console.warn(`[Pyodide] ${errors.length} modules failed to load:`, errors);
    }
    console.log(`[Pyodide] Loaded ${loadedCount}/${modules.length} Python modules`);

    // Add the compiler directory to Python path and import the main function
    console.log('[Pyodide] Importing dashboard_compiler...');
    await this.pyodide.runPythonAsync(`
import sys
sys.path.insert(0, '/home/pyodide')

# Import the main compile function
from dashboard_compiler.dashboard_compiler import compile_yaml_to_ndjson
print('✓ dashboard_compiler imported successfully')
    `);
    
    console.log('[Pyodide] Full compiler loaded and ready');
  }

  /**
   * Compile YAML to NDJSON using the full dashboard compiler
   */
  async compile(yamlContent) {
    if (!this.isReady) {
      await this.initialize();
    }

    try {
      const startTime = Date.now();
      
      // Store YAML content in a Python variable to avoid escaping issues
      this.pyodide.globals.set('_yaml_input', yamlContent);
      
      // Call the real compiler
      const result = await this.pyodide.runPythonAsync(`
compile_yaml_to_ndjson(_yaml_input)
      `);
      
      const compileTime = Date.now() - startTime;
      console.log(`[Pyodide] Compiled in ${compileTime}ms`);

      return {
        success: true,
        ndjson: result,
        compileTime
      };
    } catch (error) {
      console.error('[Pyodide] Compilation error:', error);
      
      // Try to extract a more user-friendly error message
      let errorMessage = error.message;
      
      // Check for Pydantic validation errors
      if (errorMessage.includes('ValidationError')) {
        // Extract just the relevant validation error parts
        const match = errorMessage.match(/(\d+ validation error[s]? for [\s\S]*?)(?:For further information|$)/);
        if (match) {
          errorMessage = match[1].trim();
        }
      }
      
      return {
        success: false,
        error: errorMessage
      };
    }
  }

  /**
   * Get initialization progress
   */
  getProgress() {
    if (this.isReady) return 100;
    if (!this.initStartTime) return 0;
    
    const elapsed = Date.now() - this.initStartTime;
    // Estimate ~10 seconds for full init with pydantic
    return Math.min(95, Math.floor((elapsed / 10000) * 100));
  }
}

// Global instance
console.log('[Pyodide] Creating PythonCompiler instance...');
window.pythonCompiler = new PythonCompiler();
console.log('[Pyodide] PythonCompiler instance created, ready to initialize');
