#!/usr/bin/env node
/**
 * Integration tests - Load extension in Puppeteer and test functionality
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const EXTENSION_PATH = path.resolve(__dirname, '..');
const EXTENSION_ID_FILE = path.join(EXTENSION_PATH, '.extension-id');

// Try to find system Chrome
function findChromeExecutable() {
  const possiblePaths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', // macOS
    '/usr/bin/google-chrome', // Linux
    '/usr/bin/chromium-browser', // Linux
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', // Windows
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe' // Windows
  ];
  
  for (const chromePath of possiblePaths) {
    if (fs.existsSync(chromePath)) {
      return chromePath;
    }
  }
  
  return null;
}

async function runTests() {
  console.log('🚀 Starting integration tests...\n');
  
  let browser;
  let extensionPage;
  
  try {
    // Launch Chrome with extension
    console.log('📦 Launching Chrome with extension...');
    console.log(`   Extension path: ${EXTENSION_PATH}\n`);
    
    // Try to use system Chrome first
    const chromeExecutable = findChromeExecutable();
    const launchOptions = {
      headless: false, // Set to true for CI
      args: [
        `--disable-extensions-except=${EXTENSION_PATH}`,
        `--load-extension=${EXTENSION_PATH}`,
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security', // Allow extension loading
        '--disable-features=IsolateOrigins,site-per-process' // Help with extension loading
      ],
      timeout: 60000,
      protocolTimeout: 60000
    };
    
    if (chromeExecutable) {
      console.log(`   Using system Chrome: ${chromeExecutable}`);
      launchOptions.executablePath = chromeExecutable;
    } else {
      console.log('   Using Puppeteer bundled Chromium');
    }
    
    browser = await puppeteer.launch(launchOptions);
    
    // Wait a bit for extension to initialize
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Wait for extension to load and get its ID
    console.log('  ⏳ Waiting for extension to load...');
    let extensionId = null;
    let attempts = 0;
    const maxAttempts = 10;
    
    while (!extensionId && attempts < maxAttempts) {
      const targets = await browser.targets();
      const extensionTarget = targets.find(target => {
        const url = target.url();
        return (target.type() === 'service_worker' || target.type() === 'background_page') && 
               url.includes('chrome-extension://');
      });
      
      if (extensionTarget) {
        extensionId = extensionTarget.url().split('/')[2];
        break;
      }
      
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    if (!extensionId) {
      // Try alternative method: check extension pages
      const pages = await browser.pages();
      for (const page of pages) {
        const url = page.url();
        if (url.startsWith('chrome-extension://')) {
          extensionId = url.split('/')[2];
          break;
        }
      }
    }
    
    if (!extensionId) {
      throw new Error('Extension did not load. Make sure the extension is valid and all files exist.');
    }
    
    console.log(`  ✓ Extension loaded with ID: ${extensionId}`);
    
    // Save extension ID for reference
    fs.writeFileSync(EXTENSION_ID_FILE, extensionId);
    
    // Open a new page
    const page = await browser.newPage();
    
    // Test 1: Open side panel
    console.log('\n🧪 Test 1: Opening side panel...');
    await page.goto('chrome-extension://' + extensionId + '/sidepanel/index.html');
    await page.waitForSelector('#status', { timeout: 5000 });
    console.log('  ✓ Side panel loaded');
    
    // Test 2: Check Pyodide initialization
    console.log('\n🧪 Test 2: Checking Pyodide initialization...');
    
    // Wait for initialization to start
    await page.waitForFunction(
      () => window.pythonCompiler !== undefined,
      { timeout: 10000 }
    );
    console.log('  ✓ PythonCompiler instance created');
    
    // Check if initialization is in progress or complete
    const isReady = await page.evaluate(() => {
      return window.pythonCompiler?.isReady || false;
    });
    
    if (isReady) {
      console.log('  ✓ Pyodide already initialized');
    } else {
      console.log('  ⏳ Waiting for Pyodide initialization (this may take 10-30 seconds)...');
      
      // Wait for initialization to complete
      await page.waitForFunction(
        () => window.pythonCompiler?.isReady === true,
        { timeout: 60000 }
      );
      console.log('  ✓ Pyodide initialized successfully');
    }
    
    // Test 3: Test compilation
    console.log('\n🧪 Test 3: Testing YAML compilation...');
    const testYaml = `---
dashboards:
  - name: Test Dashboard
    panels:
      - title: Test Panel
        grid: { x: 0, y: 0, w: 24, h: 15 }
        markdown:
          content: "# Hello World"
`;
    
    const compileResult = await page.evaluate(async (yaml) => {
      return await window.pythonCompiler.compile(yaml);
    }, testYaml);
    
    if (compileResult.success) {
      console.log('  ✓ Compilation successful');
      console.log(`  ✓ Compiled in ${compileResult.compileTime}ms`);
    } else {
      throw new Error(`Compilation failed: ${compileResult.error}`);
    }
    
    // Test 4: Check preview rendering
    console.log('\n🧪 Test 4: Checking preview rendering...');
    const hasPreview = await page.evaluate(() => {
      const visualPreview = document.getElementById('visual-preview');
      const jsonPreview = document.getElementById('json-preview');
      return visualPreview && jsonPreview;
    });
    
    if (hasPreview) {
      console.log('  ✓ Preview elements found');
    } else {
      throw new Error('Preview elements not found');
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ All integration tests passed!');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error('   Error type:', error.constructor.name);
    
    if (error.message.includes('socket hang up') || error.message.includes('Target closed')) {
      console.error('\n💡 Troubleshooting tips:');
      console.error('   1. Make sure Chrome/Chromium is installed');
      console.error('   2. Try running: npm install puppeteer --force');
      console.error('   3. Check that the extension path is correct');
      console.error('   4. Verify all required files exist (run: npm run test:validate)');
      console.error('\n   Alternative: Use manual testing instead:');
      console.error('   - Run: npm run test:open (opens Chrome with extension)');
      console.error('   - Or follow: tests/manual-test.md');
    }
    
    // Take screenshot for debugging
    if (browser) {
      try {
        const pages = await browser.pages();
        if (pages.length > 0) {
          await pages[0].screenshot({ path: path.join(EXTENSION_PATH, 'test-failure.png') });
          console.log('  📸 Screenshot saved to test-failure.png');
        }
      } catch (screenshotError) {
        // Ignore screenshot errors
      }
    }
    
    process.exit(1);
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch (closeError) {
        // Ignore close errors
      }
    }
  }
}

// Run tests
runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
