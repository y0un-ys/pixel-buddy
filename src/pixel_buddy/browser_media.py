"""Loopback-only video playback reports from the optional browser extension."""
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 38673
MAX_AGE = 6.0
CHROMIUM_APPS = frozenset({
    'chrome.exe', 'msedge.exe', 'brave.exe', 'opera.exe', 'whale.exe',
    'google chrome', 'microsoft edge', 'brave browser', 'opera', 'whale', 'naver whale', 'arc',
    'arc.exe', 'chromium', 'chromium.exe',
})


class _MediaServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int):
        self.lock = threading.Lock()
        self.playing: bool | None = None
        self.updated_at = 0.0
        super().__init__(('127.0.0.1', port), _MediaHandler)


class _MediaHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server: _MediaServer):
        self.media_server = server
        super().__init__(request, client_address, server)

    def setup(self):
        super().setup()
        self.connection.settimeout(2.0)

    def log_message(self, format: str, *args: object) -> None:
        # Do not retain requests or page data in application logs.
        pass

    def _allowed(self) -> bool:
        return (
            self.headers.get('Host') == f'127.0.0.1:{self.media_server.server_port}'
            and re.fullmatch(r'chrome-extension://[a-p]{32}',
                             self.headers.get('Origin', '')) is not None
        )

    def _reply(self, status: int, payload: dict[str, bool]) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        if self._allowed():
            self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if (not self._allowed()
                or self.path not in ('/health', '/media-state')
                or self.headers.get('Access-Control-Request-Method') not in ('GET', 'POST')
                or self.headers.get('Access-Control-Request-Headers', '').lower()
                not in ('', 'content-type')):
            self._reply(403, {'accepted': False})
            return
        self._reply(200, {'accepted': True})

    def do_GET(self):
        # Host-permission GETs from Chromium can omit Origin. This endpoint
        # exposes no state or data, and POST still requires an extension origin.
        local_health = (
            self.path == '/health'
            and self.headers.get('Host') == f'127.0.0.1:{self.media_server.server_port}'
            and not self.headers.get('Origin')
        )
        if not (self._allowed() or local_health):
            self._reply(403, {'connected': False})
        elif self.path == '/health':
            self._reply(200, {'connected': True})
        else:
            self._reply(404, {'connected': False})

    def do_POST(self):
        if not self._allowed():
            self._reply(403, {'accepted': False})
            return
        if self.path != '/media-state':
            self._reply(404, {'accepted': False})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            length = 0
        if not 0 < length <= 128:
            self._reply(413, {'accepted': False})
            return
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            self._reply(415, {'accepted': False})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (ValueError, TimeoutError):
            self._reply(400, {'accepted': False})
            return
        if (not isinstance(payload, dict) or set(payload) != {'browser', 'playing'}
                or payload['browser'] != 'chromium'
                or type(payload['playing']) is not bool):
            self._reply(400, {'accepted': False})
            return
        with self.media_server.lock:
            self.media_server.playing = payload['playing']
            self.media_server.updated_at = time.monotonic()
        self._reply(200, {'accepted': True})


class BrowserMediaBridge:
    def __init__(self, port: int = PORT):
        self._server = _MediaServer(port)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    @property
    def port(self) -> int:
        return self._server.server_port

    def playback_for(self, application: str) -> bool | None:
        if application not in CHROMIUM_APPS:
            return None
        with self._server.lock:
            if (self._server.playing is None
                    or time.monotonic() - self._server.updated_at >= MAX_AGE):
                return None
            return self._server.playing

    def diagnostic(self) -> str:
        playing = self.playback_for('google chrome')
        if playing is None:
            return '브라우저 확장: 미연결 (선택 사항 · 영상 창 감지는 확장 없이 동작)'
        return '영상 연동: 재생 중' if playing else '영상 연동: 연결됨 · 재생 없음'

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2.0)
