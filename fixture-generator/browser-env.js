/**
 * Browser Environment Setup for Node.js
 *
 * This script sets up a browser-like environment using jsdom so that
 * Kibana's browser-only code (like FormulaPublicApi) can be imported.
 *
 * Must be imported BEFORE any Kibana code.
 */

const { JSDOM } = require('jsdom');

// Create a minimal DOM environment
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost',
  pretendToBeVisual: true,
});

// Set up global browser objects
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.HTMLElement = dom.window.HTMLElement;
global.Node = dom.window.Node;
global.Element = dom.window.Element;
global.Event = dom.window.Event;
global.CustomEvent = dom.window.CustomEvent;
global.requestAnimationFrame = (cb) => setTimeout(cb, 0);
global.cancelAnimationFrame = (id) => clearTimeout(id);

// Mock storage
const createStorageMock = () => {
  const store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { Object.keys(store).forEach(key => delete store[key]); },
    get length() { return Object.keys(store).length; },
    key: (i) => Object.keys(store)[i] || null,
  };
};

global.window.sessionStorage = createStorageMock();
global.window.localStorage = createStorageMock();

// Mock XMLHttpRequest for APM RUM
global.window.XMLHttpRequest = function() {
  return {
    open: () => {},
    send: () => {},
    setRequestHeader: () => {},
    abort: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
  };
};

// Mock performance API
global.window.performance = {
  now: () => Date.now(),
  timing: { navigationStart: Date.now() },
};

// Mock matchMedia
global.window.matchMedia = (query) => ({
  matches: false,
  media: query,
  addEventListener: () => {},
  removeEventListener: () => {},
});

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock MutationObserver
global.MutationObserver = class MutationObserver {
  constructor() {}
  observe() {}
  disconnect() {}
  takeRecords() { return []; }
};

// Mock fetch
global.fetch = () => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({}),
  text: () => Promise.resolve(''),
});

// Mock location
global.window.location = new URL('http://localhost');

// Mock console.assert
if (!global.console.assert) {
  global.console.assert = (condition, message) => {
    if (!condition) console.error('Assertion failed:', message);
  };
}

console.log('✓ Browser environment initialized');
