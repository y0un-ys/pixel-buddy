# Pixel Buddy v0.3.1 — macOS 지원

## Mac 앱 만들기

1. 이 폴더 전체를 Mac에 압축 해제합니다.
2. Python 3.11 이상을 설치합니다.
3. 터미널에서 이 폴더로 이동하여 `bash build_mac.command`를 실행합니다. (`build_mac.command` 더블클릭도 가능하지만 보안 설정에 따라 차단될 수 있습니다.)
4. `dist/PixelBuddy.app`을 **응용 프로그램(Applications)** 폴더로 옮기고 실행합니다.
5. 개발자가 서명한 앱이 아니므로 macOS Gatekeeper 경고가 나올 수 있습니다. 출처를 확인한 후 macOS 설정 > 개인정보 보호 및 보안에서 허용하세요. 보안 기능 전체 해제는 권장하지 않습니다.

## 접근성 권한

다른 앱에서 키보드 입력 활동 감지는 macOS **개인정보 보호 및 보안 > 손쉬운 사용(Accessibility)** 허용이 필요할 수 있습니다. 실제 입력한 문자는 기록하지 않으며 이벤트 시점만 처리합니다. 브라우저 창 제목은 macOS 권한에 따라 접근 불가할 수 있으며, 영상 감지는 추정입니다. 권한이 없으면 설정에서 수동 모드를 선택하세요.

## 데이터 / 자동 실행

- macOS 저장 위치: `~/Library/Application Support/PixelBuddy/save.sqlite3`
- Windows 저장 위치는 기존대로 `%LOCALAPPDATA%\PixelBuddy\save.sqlite3`입니다.
- macOS 로그인 자동 실행은 `~/Library/LaunchAgents/com.pixelbuddy.desktop.plist`를 이용하며 설정에서 해제할 수 있습니다.
- 실행 파일의 위치를 옮기면 자동 실행을 껐다 다시 켜세요.
- Windows와 Mac 사이에 기존 데이터가 자동 동기화되지는 않습니다.

## 제약

이 패키지는 **Mac에서 `.app`을 만드는 소스/빌드 키트**입니다. 이 환경은 Linux라 서명된 macOS `.app`의 실제 빌드 및 실행 검증은 수행하지 못했습니다. Steam 게임 감지와 전체화면 자동 숨김은 macOS에서 제한적이며 Windows와 완전히 동일하게 동작하지 않습니다.
