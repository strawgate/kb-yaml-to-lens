#!/usr/bin/env node
/**
 * Simple validation test - no browser required
 * Use this if Puppeteer integration tests fail
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Simple Extension Validation\n');

const EXTENSION_PATH = path.resolve(__dirname, '..');
let hasErrors = false;

// Check manifest
console.log('1. Checking manifest.json...');
try {
  const manifestPath = path.join(EXTENSION_PATH, 'manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  console.log('   ✓ Valid JSON');
  console.log(`   ✓ Name: ${manifest.name}`);
  console.log(`   ✓ Version: ${manifest.version}`);
  
  if (!manifest.content_security_policy?.extension_pages?.includes('wasm-unsafe-eval')) {
    console.log('   ⚠️  CSP may not allow WASM');
  } else {
    console.log('   ✓ CSP configured for WASM');
  }
} catch (error) {
  console.log(`   ❌ ${error.message}`);
  hasErrors = true;
}

// Check key files
console.log('\n2. Checking key files...');
const keyFiles = [
  'sidepanel/index.html',
  'sidepanel/pyodide-loader.js',
  'editor.js',
  'actions.js',
  'background/service-worker.js'
];

keyFiles.forEach(file => {
  const filePath = path.join(EXTENSION_PATH, file);
  if (fs.existsSync(filePath)) {
    console.log(`   ✓ ${file}`);
  } else {
    console.log(`   ❌ Missing: ${file}`);
    hasErrors = true;
  }
});

// Check Pyodide
console.log('\n3. Checking Pyodide files...');
const pyodideFiles = [
  'lib/pyodide/pyodide.js',
  'lib/pyodide/pyodide.asm.js',
  'lib/pyodide/pyodide.asm.wasm',
  'lib/pyodide/pyodide-lock.json',
  'lib/pyodide/python_stdlib.zip'
];

let pyodideComplete = true;
pyodideFiles.forEach(file => {
  const filePath = path.join(EXTENSION_PATH, file);
  if (fs.existsSync(filePath)) {
    const size = (fs.statSync(filePath).size / 1024 / 1024).toFixed(2);
    console.log(`   ✓ ${file} (${size} MB)`);
  } else {
    console.log(`   ❌ Missing: ${file}`);
    pyodideComplete = false;
    hasErrors = true;
  }
});

if (!pyodideComplete) {
  console.log('\n   💡 Run ./setup.sh to download Pyodide files');
}

// Summary
console.log('\n' + '='.repeat(50));
if (hasErrors) {
  console.log('❌ Validation found issues');
  console.log('   Fix the errors above and try again');
  process.exit(1);
} else {
  console.log('✅ Basic validation passed!');
  console.log('\n   Extension should be ready to load in Chrome.');
  console.log('   Go to chrome://extensions/ and click "Load unpacked"');
  process.exit(0);
}
