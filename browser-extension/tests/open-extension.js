#!/usr/bin/env node
/**
 * Helper script to open Chrome with extension loaded
 * Alternative to Puppeteer automation
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const EXTENSION_PATH = path.resolve(__dirname, '..');

// Find Chrome executable
function findChrome() {
  const possiblePaths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', // macOS
    '/usr/bin/google-chrome', // Linux
    '/usr/bin/chromium-browser', // Linux
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', // Windows
  ];
  
  for (const chromePath of possiblePaths) {
    if (fs.existsSync(chromePath)) {
      return chromePath;
    }
  }
  
  return null;
}

const chromePath = findChrome();

if (!chromePath) {
  console.error('❌ Chrome not found. Please install Google Chrome.');
  console.error('   Or manually load the extension:');
  console.error('   1. Go to chrome://extensions/');
  console.error('   2. Enable Developer mode');
  console.error('   3. Click "Load unpacked"');
  console.error(`   4. Select: ${EXTENSION_PATH}`);
  process.exit(1);
}

console.log('🚀 Opening Chrome with extension...\n');
console.log(`   Extension: ${EXTENSION_PATH}\n`);

const command = `"${chromePath}" --load-extension="${EXTENSION_PATH}" --disable-extensions-except="${EXTENSION_PATH}" chrome://extensions/`;

exec(command, (error, stdout, stderr) => {
  if (error) {
    console.error('Error:', error.message);
    return;
  }
  
  console.log('✅ Chrome opened!');
  console.log('\nNext steps:');
  console.log('1. Find your extension in chrome://extensions/');
  console.log('2. Click the extension icon to open side panel');
  console.log('3. Follow the manual test guide: tests/manual-test.md');
});
