import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";
import { MediaState, EXPIRY_MS, HEARTBEAT_MS } from "../state.mjs";

const message = playing => ({ type: "media-state", playing });
const sender = (tabId = 1, frameId = 0) => ({
  tab: { id: tabId }, frameId
});

function clockedState() {
  let time = 0;
  return { state: new MediaState(() => time), advance: ms => { time += ms; } };
}

test("aggregates independent frames and tabs through pause and end reports", () => {
  const { state } = clockedState();
  state.observe(message(true), sender(1, 0));
  state.observe(message(true), sender(1, 2));
  state.observe(message(false), sender(2, 0));
  assert.deepEqual(state.report(), { browser: "chromium", playing: true });
  state.observe(message(false), sender(1, 0)); // pause
  assert.equal(state.playing(), true);
  assert.equal(state.report(), null);
  state.observe(message(false), sender(1, 2)); // ended
  assert.deepEqual(state.report(), { browser: "chromium", playing: false });
});

test("heartbeat reports at the exact two-second boundary, changes immediately", () => {
  const { state, advance } = clockedState();
  state.observe(message(true), sender());
  assert.equal(state.report().playing, true);
  advance(HEARTBEAT_MS - 1);
  state.observe(message(true), sender());
  assert.equal(state.report(), null);
  advance(1);
  state.observe(message(true), sender());
  assert.equal(state.report().playing, true);
  assert.equal(state.report(), null);
  state.observe(message(false), sender());
  assert.equal(state.report().playing, false);
});

test("leases expire at six seconds and live frames remain independent", () => {
  const { state, advance } = clockedState();
  state.observe(message(true), sender(1));
  state.report();
  advance(1000);
  state.observe(message(true), sender(2));
  advance(EXPIRY_MS - 1001);
  assert.equal(state.frames.size, 2);
  assert.equal(state.playing(), true);
  advance(1);
  assert.equal(state.playing(), true);
  assert.equal(state.frames.size, 1);
  advance(1000);
  assert.deepEqual(state.report(), { browser: "chromium", playing: false });
  assert.equal(state.frames.size, 0);
});

test("closing or navigating a tab removes only its frames", () => {
  const { state } = clockedState();
  for (const frame of [0, 2, 8]) state.observe(message(true), sender(1, frame));
  state.observe(message(true), sender(2));
  state.removeTab(1);
  assert.equal(state.frames.size, 1);
  assert.equal(state.playing(), true);
  state.removeTab(2);
  assert.equal(state.playing(), false);
  state.removeTab(999);
  assert.equal(state.frames.size, 0);
});

test("a replacement frame report overwrites old document state", () => {
  const { state } = clockedState();
  state.observe(message(true), { ...sender(), documentId: "old" });
  state.observe(message(false), { ...sender(), documentId: "new" });
  assert.equal(state.playing(), false);
  assert.equal(state.frames.size, 1);
});

test("malformed or content-bearing messages and invalid senders are rejected", () => {
  const { state } = clockedState();
  for (const invalid of [
    null, undefined, {}, [], { type: "other", playing: true },
    { type: "media-state" }, message("true"), message(1),
    { ...message(true), url: "https://example.invalid" },
    { ...message(true), title: "not allowed" }
  ]) assert.equal(state.observe(invalid, sender()), false);
  for (const invalid of [
    null, {}, { frameId: 0 }, { tab: { id: -1 }, frameId: 0 },
    { tab: { id: 1 }, frameId: -1 }, { tab: { id: 1 }, frameId: 1.5 }
  ]) assert.equal(state.observe(message(true), invalid), false);
  assert.equal(state.frames.size, 0);
});

test("a restarted worker recovers from the next content heartbeat without storage", () => {
  const before = new MediaState(() => 0);
  before.observe(message(true), sender());
  before.report();
  const after = new MediaState(() => HEARTBEAT_MS);
  assert.equal(after.playing(), false);
  after.observe(message(true), sender());
  assert.deepEqual(after.report(), { browser: "chromium", playing: true });
  assert.deepEqual(Object.keys(after.report() ?? {}), []);
});

test("content observes real videos, dynamic DOM, required events, and heartbeat", async () => {
  const source = await readFile(new URL("../content.js", import.meta.url), "utf8");
  class Video {
    constructor(overrides = {}) {
      Object.assign(this, {
        paused: false, ended: false, readyState: 2, videoWidth: 640
      }, overrides);
    }
  }
  const listeners = new Map();
  const sent = [];
  const intervals = [];
  let videos = [];
  let mutation;
  vm.runInNewContext(source, {
    HTMLVideoElement: Video,
    document: {
      querySelectorAll: selector => { assert.equal(selector, "video"); return videos; },
      addEventListener: (event, callback, capture) => {
        assert.equal(capture, true);
        listeners.set(event, callback);
      }
    },
    MutationObserver: class {
      constructor(callback) { mutation = callback; }
      observe(_document, options) {
        assert.equal(options.subtree, true);
        assert.equal(options.childList, true);
      }
    },
    chrome: { runtime: { sendMessage: payload => { sent.push(payload); return Promise.resolve(); } } },
    setInterval: (callback, ms) => { intervals.push({ callback, ms }); }
  });
  assert.equal(sent.at(-1).playing, false);
  assert.equal(intervals.length, 1);
  assert.equal(intervals[0].ms, HEARTBEAT_MS);
  const video = new Video();
  videos = [video];
  mutation(); // dynamically inserted, already-playing video
  assert.equal(sent.at(-1).playing, true);
  for (const event of ["play", "playing", "pause", "ended", "emptied"]) {
    assert.equal(typeof listeners.get(event), "function");
  }
  video.paused = true;
  listeners.get("pause")({ target: video });
  assert.equal(sent.at(-1).playing, false);
  video.paused = false;
  listeners.get("playing")({ target: video });
  assert.equal(sent.at(-1).playing, true);
  video.ended = true;
  listeners.get("ended")({ target: video });
  assert.equal(sent.at(-1).playing, false);
  video.ended = false;
  video.readyState = 1;
  listeners.get("emptied")({ target: video });
  assert.equal(sent.at(-1).playing, false);
  video.readyState = 2;
  video.videoWidth = 0;
  intervals[0].callback();
  assert.equal(sent.at(-1).playing, false);
  video.videoWidth = 640;
  intervals[0].callback();
  assert.equal(sent.at(-1).playing, true);
  const prior = sent.length;
  listeners.get("play")({ target: { tagName: "AUDIO" } });
  assert.equal(sent.length, prior);
  videos = [];
  mutation(); // removed frame/video cannot leave its local state playing
  assert.equal(sent.at(-1).playing, false);
  for (const payload of sent) {
    assert.deepEqual(Object.keys(payload).sort(), ["playing", "type"]);
  }
});

test("background wires local POST, popup health, close/navigation, and worker recovery", { timeout: 3000 }, async t => {
  const previousChrome = globalThis.chrome;
  const previousFetch = globalThis.fetch;
  t.after(() => {
    globalThis.chrome = previousChrome;
    globalThis.fetch = previousFetch;
  });
  const requests = [];
  let requestSignal;
  globalThis.fetch = async (url, options = {}) => {
    requests.push({ url, options });
    if (requestSignal) {
      const resolve = requestSignal;
      requestSignal = undefined;
      resolve(requests.at(-1));
    }
    return { ok: true, json: async () => ({ connected: true }) };
  };
  function installChrome() {
    const handlers = {};
    globalThis.chrome = {
      runtime: {
        id: "test-extension",
        getURL: path => `chrome-extension://test-extension/${path}`,
        onMessage: { addListener: callback => { handlers.message = callback; } }
      },
      tabs: {
        onRemoved: { addListener: callback => { handlers.removed = callback; } },
        onUpdated: { addListener: callback => { handlers.updated = callback; } }
      }
    };
    return handlers;
  }
  async function nextRequest(action) {
    const arrived = new Promise(resolve => { requestSignal = resolve; });
    action();
    return arrived;
  }
  const fromPage = { ...sender(), id: "test-extension" };
  let handlers = installChrome();
  await import("../background.js?first-worker");
  let request = await nextRequest(() => handlers.message(message(true), fromPage, () => {}));
  assert.equal(request.url, "http://127.0.0.1:38673/media-state");
  assert.equal(request.options.method, "POST");
  assert.equal(request.options.headers["Content-Type"], "application/json");
  assert.equal(request.options.credentials, "omit");
  assert.deepEqual(JSON.parse(request.options.body), { browser: "chromium", playing: true });
  const count = requests.length;
  handlers.message(message(true), { ...fromPage, id: "foreign-extension" }, () => {});
  handlers.message({ type: "status" }, fromPage, () => {});
  handlers.message({ ...message(true), title: "rejected" }, fromPage, () => {});
  assert.equal(requests.length, count);
  const status = new Promise(resolve => {
    assert.equal(handlers.message({ type: "status" }, {
      id: "test-extension", url: "chrome-extension://test-extension/popup.html",
      tab: { id: 2 }
    }, resolve), true);
  });
  assert.deepEqual(await status, { connected: true, playing: true });
  assert.equal(requests.at(-1).url, "http://127.0.0.1:38673/health");
  request = await nextRequest(() => handlers.updated(1, { status: "loading" }));
  assert.equal(JSON.parse(request.options.body).playing, false);
  await nextRequest(() => handlers.message(message(true), fromPage, () => {}));
  request = await nextRequest(() => handlers.removed(1));
  assert.equal(JSON.parse(request.options.body).playing, false);
  // A fresh service worker has no persisted frame state.
  handlers = installChrome();
  await import("../background.js?restarted-worker");
  request = await nextRequest(() => handlers.message(message(true), fromPage, () => {}));
  assert.equal(JSON.parse(request.options.body).playing, true);
});

test("manifest is MV3 with only loopback host access and all-frame content detection", async () => {
  const manifest = JSON.parse(await readFile(new URL("../manifest.json", import.meta.url), "utf8"));
  assert.equal(manifest.manifest_version, 3);
  assert.equal(manifest.background.type, "module");
  assert.deepEqual(manifest.host_permissions, ["http://127.0.0.1/*"]);
  assert.deepEqual(manifest.permissions ?? [], []);
  assert.deepEqual(manifest.content_scripts[0].matches, ["<all_urls>"]);
  assert.equal(manifest.content_scripts[0].all_frames, true);
});
