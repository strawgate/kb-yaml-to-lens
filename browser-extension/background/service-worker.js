/**
 * Background Service Worker - Handles extension-level events
 */

// Handle action button click to open side panel
chrome.action.onClicked.addListener((tab) => {
  if (chrome.sidePanel && chrome.sidePanel.open) {
    chrome.sidePanel.open({ windowId: tab.windowId });
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'open-sidepanel') {
    // Open side panel
    if (chrome.sidePanel && chrome.sidePanel.open) {
      chrome.sidePanel.open({ windowId: sender.tab.windowId });
    }
    
    // Store YAML to load in side panel
    chrome.storage.local.set({ 
      pendingYaml: request.yaml 
    });
    
    sendResponse({ success: true });
  }
  
  return true;
});

// Listen for side panel opening (if API is available)
// Note: The API uses onOpened (not onPanelShown) in newer Chrome versions
try {
  if (chrome.sidePanel) {
    // Use onOpened if available (newer API)
    if (chrome.sidePanel.onOpened) {
      chrome.sidePanel.onOpened.addListener(async () => {
        // Check if there's pending YAML to load
        const { pendingYaml } = await chrome.storage.local.get('pendingYaml');
        
        if (pendingYaml) {
          // The side panel will load it on initialization
          // We don't clear it here - let the side panel handle it
          console.log('[Background] Side panel opened, pending YAML available');
        }
      });
      console.log('[Background] Registered chrome.sidePanel.onOpened listener');
    } 
    // Fallback to onPanelShown for older Chrome versions (if it exists)
    else if (chrome.sidePanel.onPanelShown) {
      chrome.sidePanel.onPanelShown.addListener(async () => {
        const { pendingYaml } = await chrome.storage.local.get('pendingYaml');
        if (pendingYaml) {
          console.log('[Background] Side panel shown, pending YAML available');
        }
      });
      console.log('[Background] Registered chrome.sidePanel.onPanelShown listener');
    } else {
      console.log('[Background] No side panel event listeners available');
    }
  } else {
    console.log('[Background] chrome.sidePanel not available');
  }
} catch (error) {
  console.error('[Background] Error setting up side panel listener:', error);
}

console.log('[Background] Service worker initialized');
