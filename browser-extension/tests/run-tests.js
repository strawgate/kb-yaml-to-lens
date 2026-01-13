#!/usr/bin/env node
/**
 * Run all tests
 */

const { execSync } = require('child_process');
const path = require('path');

console.log('🧪 Running all tests...\n');

try {
  // Run validation tests
  console.log('1️⃣  Running validation tests...\n');
  execSync('node tests/validate.js', { 
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..')
  });
  
  console.log('\n2️⃣  Running integration tests...\n');
  console.log('   (This will open Chrome - you can watch the tests run)\n');
  
  // Run integration tests
  execSync('node tests/integration.js', { 
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..')
  });
  
  console.log('\n✅ All tests passed!');
  
} catch (error) {
  console.error('\n❌ Tests failed');
  process.exit(1);
}
