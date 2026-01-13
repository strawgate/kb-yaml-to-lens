#!/usr/bin/env node
/**
 * Validation tests - Check that all required files exist and manifest is valid
 */

const fs = require('fs');
const path = require('path');

const REQUIRED_FILES = [
  'manifest.json',
  'sidepanel/index.html',
  'sidepanel/pyodide-loader.js',
  'sidepanel/preview.js',
  'editor.js',
  'actions.js',
  'background/service-worker.js',
  'content/content-script.js',
  'lib/js-yaml.min.js',
  'sidepanel/styles.css'
];

const REQUIRED_PYODIDE_FILES = [
  'lib/pyodide/pyodide.js',
  'lib/pyodide/pyodide.asm.js',
  'lib/pyodide/pyodide.asm.wasm',
  'lib/pyodide/pyodide.asm.data',
  'lib/pyodide/packages.json',
  'lib/pyodide/repodata.json',
  'lib/pyodide/pyodide-lock.json',
  'lib/pyodide/python_stdlib.zip'
];

let errors = [];
let warnings = [];

console.log('🔍 Validating extension...\n');

// Check required files
console.log('📁 Checking required files...');
REQUIRED_FILES.forEach(file => {
  const filePath = path.join(__dirname, '..', file);
  if (!fs.existsSync(filePath)) {
    errors.push(`Missing required file: ${file}`);
  } else {
    console.log(`  ✓ ${file}`);
  }
});

// Check Pyodide files
console.log('\n🐍 Checking Pyodide files...');
let pyodideMissing = [];
REQUIRED_PYODIDE_FILES.forEach(file => {
  const filePath = path.join(__dirname, '..', file);
  if (!fs.existsSync(filePath)) {
    pyodideMissing.push(file);
    warnings.push(`Missing Pyodide file: ${file} (run ./setup.sh)`);
  } else {
    const stats = fs.statSync(filePath);
    console.log(`  ✓ ${file} (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);
  }
});

// Validate manifest.json
console.log('\n📋 Validating manifest.json...');
try {
  const manifestPath = path.join(__dirname, '..', 'manifest.json');
  const manifestContent = fs.readFileSync(manifestPath, 'utf8');
  const manifest = JSON.parse(manifestContent);
  
  // Check required fields
  const requiredFields = ['manifest_version', 'name', 'version', 'side_panel', 'action'];
  requiredFields.forEach(field => {
    if (!manifest[field]) {
      errors.push(`Missing required manifest field: ${field}`);
    }
  });
  
  // Check CSP
  if (!manifest.content_security_policy) {
    warnings.push('No content_security_policy in manifest (WASM may not work)');
  } else if (!manifest.content_security_policy.extension_pages?.includes('wasm-unsafe-eval')) {
    warnings.push('CSP may not allow WASM execution');
  }
  
  console.log('  ✓ Valid JSON');
  console.log(`  ✓ Manifest version: ${manifest.manifest_version}`);
  console.log(`  ✓ Extension name: ${manifest.name}`);
  
} catch (error) {
  errors.push(`Invalid manifest.json: ${error.message}`);
}

// Check icons
console.log('\n🎨 Checking icons...');
const iconSizes = [16, 48, 128];
iconSizes.forEach(size => {
  const iconPath = path.join(__dirname, '..', 'icons', `icon${size}.png`);
  if (!fs.existsSync(iconPath)) {
    warnings.push(`Missing icon: icons/icon${size}.png`);
  } else {
    console.log(`  ✓ icon${size}.png`);
  }
});

// Summary
console.log('\n' + '='.repeat(50));
if (errors.length === 0 && warnings.length === 0) {
  console.log('✅ All checks passed!');
  process.exit(0);
} else {
  if (errors.length > 0) {
    console.log(`❌ ${errors.length} error(s):`);
    errors.forEach(err => console.log(`   - ${err}`));
  }
  if (warnings.length > 0) {
    console.log(`\n⚠️  ${warnings.length} warning(s):`);
    warnings.forEach(warn => console.log(`   - ${warn}`));
  }
  process.exit(errors.length > 0 ? 1 : 0);
}
