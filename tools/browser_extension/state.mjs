export const HEARTBEAT_MS = 2000;
export const EXPIRY_MS = 6000;

// Deliberately retain no URL, title, or page data. The clock is injectable so
// suspension, expiry, and heartbeat boundaries can be tested without timers.
export class MediaState {
  constructor(now = () => Date.now()) {
    this.now = now;
    this.frames = new Map();
    this.lastReportAt = -Infinity;
    this.lastReportedPlaying = undefined;
  }

  observe(message, sender) {
    if (
      !message || message.type !== "media-state" ||
      typeof message.playing !== "boolean" ||
      Object.keys(message).some(key => !["type", "playing"].includes(key)) ||
      !Number.isInteger(sender?.tab?.id) || sender.tab.id < 0 ||
      !Number.isInteger(sender.frameId) || sender.frameId < 0
    ) {
      return false;
    }
    this.frames.set(`${sender.tab.id}:${sender.frameId}`, {
      tabId: sender.tab.id,
      playing: message.playing,
      lastSeen: this.now()
    });
    return true;
  }

  removeTab(tabId) {
    for (const [key, frame] of this.frames) {
      if (frame.tabId === tabId) this.frames.delete(key);
    }
  }

  playing() {
    const now = this.now();
    for (const [key, frame] of this.frames) {
      if (now - frame.lastSeen >= EXPIRY_MS) this.frames.delete(key);
    }
    return [...this.frames.values()].some(frame => frame.playing);
  }

  report() {
    const playing = this.playing();
    const now = this.now();
    if (
      playing === this.lastReportedPlaying &&
      now - this.lastReportAt < HEARTBEAT_MS
    ) return null;
    this.lastReportAt = now;
    this.lastReportedPlaying = playing;
    return { browser: "chromium", playing };
  }
}
