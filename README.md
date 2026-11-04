# Pixel Buddy 🐾

귀여운 동물 친구가 컴퓨터를 함께 사용하는 Windows/macOS 데스크톱 펫.

**개발 버전:** v0.4.5 · **개발 브랜치:** `dev` (안정 버전만 `main`에 병합)

## 현재 기능

- 동물 5종: 고양이, 강아지, 곰, 여우, 토끼
- 새 3/4 반측면 캐릭터 PNG: `assets/illustrations/{cat,dog,bear,fox,rabbit}.png`
- 공통 `BuddyScene`에서 메인 화면·상점 미리보기·인벤토리 미리보기 렌더링
- 컴퓨터(노트북/데스크톱/듀얼), 책상, 소품, 테마 및 구매/장착 시스템
- 타이핑/마우스/게임/영상 시청/휴식 상태 감지 및 성장/코인
- 이전 저장 데이터 경로와 호환

## v0.4.4 — 일러스트 앱 연결

- 확정된 귀여운 일러스트 5종을 **실제 앱에 연결**했습니다.
- 별도 SVG 의자·몸통·손 레이어를 제거하여 중복 그림과 떠다니는 손 문제를 방지했습니다.
- 책상, 컴퓨터, 소품을 그림 앞쪽에 렌더링하여 겹침 순서를 통일했습니다.
- 그림이 없는 이전 소스에서는 기존 SVG 장면으로 대체합니다.
- GitHub Actions에서 실제 Qt 위젯을 그려 PNG로 캡처하는 시각 검증 도구를 추가했습니다.
- 테스트: `python -m pytest -q` / 실제 화면 캡처: `python tools/preview_illustrated_pet.py`

**아직 남은 작업:** 새 PNG의 손 모양은 정적인 기본 자세입니다. 행동별 앞발 포즈와 의상·머리띠 전용 일러스트는 후속 버전에서 작업합니다. Mac의 실제 화면 동작과 항상 위 동작은 기기에서 추가 검증이 필요합니다.

## v0.4.5 — 활동 애니메이션 및 수면 판정 개선

- 자동 감지는 관찰된 키보드/마우스 이벤트만으로 `typing`/`mouse`를 판정합니다.
- 실제 입력이 없는 일반 대기(`idle`)에서는 Z 표시가 나오지 않습니다. 150초 이상 활동이 없을 때만 시각적으로 `sleep`을 표시합니다.
- 새 동물 PNG는 그대로 유지하고 키보드 타건, 마우스 클릭, 영상 재생, 게임 컨트롤러, 대기·수면 효과를 주변 장비에 표시합니다.
- 모든 효과는 동물 얼굴/팔을 덧그리는 대신 장비 위치에 맞춰 렌더링합니다.
- 설정의 **현재 상태**에서 감지된 행동, 키/마우스 마지막 이벤트 시간, Mac 입력 모니터링 권한을 확인할 수 있습니다.
- 입력한 문자 내용은 읽거나 저장하지 않습니다. macOS 입력 모니터링 권한이 없으면 자동 타이핑 감지가 작동하지 않을 수 있습니다.
- 수동 행동 선택으로 각 애니메이션을 확인할 수 있습니다.
- 자동화 테스트는 GitHub Actions에서 수행하며, `tools/preview_illustrated_pet.py`는 6개 상태와 2개 프레임을 실제 Qt 화면으로 저장합니다.

**알려진 제한:** 현재 캐릭터 PNG는 정지 일러스트입니다. 캐릭터 전체는 작게 움직이고 상태별 장비/연출이 반응하지만, 실제 앞발 관절을 움직이는 개별 프레임 애니메이션은 아직 제작하지 않았습니다.

## 실행/빌드

Python 3.11 이상 필요.

### macOS (Apple Silicon 또는 Intel)

```bash
git clone -b dev https://github.com/y0un-ys/pixel-buddy.git
cd pixel-buddy
bash build_mac.command
open dist/PixelBuddy.app
```

이미 체크아웃했다면 `git switch dev && git pull origin dev` 후 빌드하세요.

macOS Gatekeeper가 미서명 `.command`를 차단하면 Finder 더블클릭 대신 위의 `bash build_mac.command`를 사용하세요. 입력 감지에는 macOS **개인정보 보호 및 보안 → 입력 모니터링** 권한이 필요할 수 있습니다. 입력 글자는 저장하지 않습니다.

### Windows

`build_exe.bat` 실행 후 `dist/PixelBuddy.exe` 실행.

## 개발 및 검증

```bash
python -m pip install -e . pytest
python -m pytest -q
```

CI는 Linux에서 자동화 테스트와 오프스크린 Qt 캡처를 실행합니다. 실제 Windows/macOS 실행과 패키징은 해당 OS에서 별도로 확인해야 합니다.

`main`은 안정 배포용으로 유지하며, 기능 개발은 `dev`에 커밋합니다. 자동 업데이트는 아직 포함되어 있지 않습니다.
