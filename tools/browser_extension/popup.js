const refresh = document.getElementById("refresh");
const connection = document.getElementById("connection");
const playing = document.getElementById("playing");

async function update() {
  refresh.disabled = true;
  connection.textContent = "연결 확인 중...";
  try {
    const status = await chrome.runtime.sendMessage({ type: "status" });
    connection.textContent = status?.connected
      ? "Pixel Buddy 연결됨"
      : "연결 안 됨 — Pixel Buddy를 실행해 주세요.";
    playing.textContent = status?.playing
      ? "영상 재생 중"
      : "재생 중인 영상 없음";
  } catch {
    connection.textContent = "확장 프로그램 연결 오류 — 확장을 다시 로드해 주세요.";
    playing.textContent = "영상 상태를 확인할 수 없습니다.";
  } finally {
    refresh.disabled = false;
  }
}

refresh.addEventListener("click", update);
update();
