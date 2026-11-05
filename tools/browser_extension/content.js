(() => {
  function publish() {
    const playing = [...document.querySelectorAll("video")].some(video =>
      video instanceof HTMLVideoElement &&
      !video.paused && !video.ended &&
      video.readyState >= 2 && video.videoWidth > 0
    );
    // A reload/update can invalidate this script's extension context. No page
    // data enters this message; the next live document starts fresh.
    try {
      chrome.runtime.sendMessage({ type: "media-state", playing }).catch(() => {});
    } catch {
      // No live worker remains after extension removal/reload.
    }
  }

  for (const event of [
    "play", "playing", "pause", "ended", "emptied",
    "loadeddata", "loadedmetadata", "resize"
  ]) {
    document.addEventListener(event, event => {
      if (event.target instanceof HTMLVideoElement) publish();
    }, true);
  }
  new MutationObserver(publish).observe(document, { childList: true, subtree: true });
  // This is the liveness lease, not a playback inference based on elapsed time.
  setInterval(publish, 2000);
  publish();
})();
