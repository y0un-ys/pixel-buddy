import { MediaState } from "./state.mjs";

const endpoint = "http://127.0.0.1:38673";
const state = new MediaState();
let pending = Promise.resolve();

function report() {
  const payload = state.report();
  if (!payload) return;
  // Preserve request order if several frames change together. A stopped
  // receiver cannot block later reports indefinitely.
  pending = pending.then(async () => {
    try {
      const response = await fetch(`${endpoint}/media-state`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(1500),
        credentials: "omit",
        cache: "no-store"
      });
      if (!response.ok) console.warn("Pixel Buddy receiver rejected media state:", response.status);
    } catch {
      // The next content heartbeat retries; never persist browsing activity.
      console.debug("Pixel Buddy local receiver is unavailable.");
    }
  });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id) return;
  if (state.observe(message, sender)) {
    report();
    return;
  }
  // Only our packaged popup may query health, whether opened as the action
  // popup or as a diagnostic tab. Ordinary content pages cannot use this path.
  if (message?.type !== "status" || sender.url !== chrome.runtime.getURL("popup.html")) return;
  report();
  fetch(`${endpoint}/health`, {
    signal: AbortSignal.timeout(1500),
    credentials: "omit",
    cache: "no-store"
  }).then(async response => {
    const health = response.ok ? await response.json() : null;
    sendResponse({ connected: health?.connected === true, playing: state.playing() });
  }).catch(() => {
    sendResponse({ connected: false, playing: state.playing() });
  });
  return true;
});

chrome.tabs.onRemoved.addListener(tabId => {
  state.removeTab(tabId);
  report();
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "loading") {
    state.removeTab(tabId);
    report();
  }
});
