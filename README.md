# pixel-buddy 🐾

귀여운 도트 동물 친구와 함께하는 Windows·macOS 데스크톱 펫.

**현재 버전:** v0.4.1 (행동 애니메이션 개선)

**Repository:** https://github.com/y0un-ys/pixel-buddy

# Pixel Buddy v0.4.1 — 공통 캐릭터 도트 행동 애니메이션 개선

Windows + macOS 공통 소스입니다. 기존 v0.3.1 게임 데이터와 상점/동물/레벨/코인 구조를 유지합니다.

## 이번 변경
- 원본 PNG 스프라이트 시트 25개 추가 (`assets/sprites/`): 동물 5종 × 행동 5종, 각각 4프레임. 실제 리소스를 두 OS에 공통 적용합니다.
- 강아지/고양이/곰/여우/토끼의 귀, 털색, 눈, 볼, 입 모양을 따로 디자인했습니다.
- 타이핑/마우스/영상/게임/휴식 상태마다 눈과 표정이 달라집니다. 눈깜빡임 포함.
- 기존 의상/머리띠/소품/책상/컴퓨터는 기존 코드 레이어로 계속 표현됩니다.
- 이미지 리소스가 없으면 기본 도형으로 대체합니다.
- PyInstaller Windows 및 macOS 스크립트에 `assets` 번들링 옵션을 추가했습니다.
- 그래픽 원본을 다시 생성할 경우 `python -m pip install Pillow` 후 `python tools/generate_sprites.py` 실행.

## Windows 빌드
1. 트레이에서 기존 Pixel Buddy 완전 종료.
2. `build_exe.bat` 더블클릭. 최초 빌드 때 Python 3.11+와 인터넷이 필요합니다.
3. `dist/PixelBuddy.exe` 실행.

## macOS 빌드
1. Mac에서 터미널을 열고 프로젝트 폴더로 이동합니다.
2. `bash build_mac.command` 실행. Python 3.11+ 필요.
3. `dist/PixelBuddy.app` 실행.

## 개발 테스트
`PYTHONPATH=src python -m pytest -q` (32 passed, Linux 기반 테스트). Windows/macOS 네이티브 실행 및 UI 시각 검증은 해당 OS에서 별도로 필요합니다.

## 유의사항
- 이번 버전은 캐릭터 그래픽의 **첫 번째 개선 구간**입니다. 고해상도 일러스트나 완성된 전신 프레임 애니메이션이 아닌 64×56 픽셀 얼굴 스프라이트와 기존 동작 레이어의 혼합 방식입니다.
- 저장 데이터 위치는 기존과 동일하며 별도로 백업해 두는 것을 권장합니다.
- 자동 업데이트 기능은 이 버전에 포함되지 않습니다.

## GitHub dev 브랜치에 소스 업로드

이 저장소의 `main` 브랜치는 안정 버전용이며, 개발 작업은 `dev`에서 진행합니다.

로컬에서 최신 파일을 `dev`에 올리려면 원격 저장소를 `git clone -b dev https://github.com/y0un-ys/pixel-buddy.git`로 가져온 다음, **압축을 푼 이 폴더의 내용 전체**를 클론 폴더에 복사하세요. 이어서 아래를 실행합니다.

```bash
git add .
git commit -m "feat: add Pixel Buddy v0.4.1 prototype source and sprites"
git push origin dev
```

`main`으로는 바로 푸시하지 않습니다. 검수 후 Pull Request로 병합합니다.


## v0.4.1 변경 사항

- 타이핑: 양손을 서로 다른 리듬으로 움직이고 눌리는 키 강조
- 마우스: 마우스/화면 커서 이동, 클릭 효과
- 게임: 양손 컨트롤러와 점프하는 화면 캐릭터
- 영상: 재생 진행바와 팝콘을 집어먹는 동작
- 휴식: 호흡 동작 및 잠깐 나타나는 Z 표시
- 애니메이션 4프레임 상태를 순수 Python 함수로 분리해 테스트 가능
