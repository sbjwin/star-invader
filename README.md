# 🚀 스타 인베이더 (Star Invader) MVP

> 80~90년대 클래식 레트로 아케이드 명작(스페이스 인베이더, 갤러그)의 핵심 재미를 현대적인 감각의 파이썬 코드로 재현한 **2D 고정 화면 편대 슈팅 게임**입니다.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Engine-pygame--ce-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Pylance](https://img.shields.io/badge/Type_Check-0_Errors-brightgreen?style=flat-square)

---

## 🎯 1. 프로젝트 기획 취지

* **레트로 아케이드 감성의 현대적 구현**: 80년대 오락실 게임의 직관적인 게임플레이(조작 ➔ 사격 ➔ 격파 ➔ 점수 획득)와 긴장감을 살리면서, 네온 픽셀 아트 비주얼과 매끄러운 60 FPS 제어를 결합했습니다.
* **초보자 친화적 클린 아키텍처**: 코딩 초보자도 한눈에 파악할 수 있도록 역할을 5개 모듈로 명확히 분리하고, 모든 소스코드에 상세한 한글 주석을 작성했습니다.
* **완벽한 정적 타입 안정성**: Pylance 및 Pyright 정적 분석 100% 통과(0 Errors, 0 Warnings)로 안정적인 게임 구동 환경을 보장합니다.

---

## 👨‍💻 2. 개발자 정보

* **개발자**: 성백진 (Baekjin Sung) ([@sbjwin](https://github.com/sbjwin))
* **저장소**: [https://github.com/sbjwin/star-invader](https://github.com/sbjwin/star-invader)

---

## 🛠️ 3. 개발환경 설정 및 실행 가이드

누구나 자신의 컴퓨터에서 소스코드를 받아 손쉽게 실행해 볼 수 있습니다.

### 📌 사전 요구사항
* **Python 3.10 이상** (Python 3.11, 3.12, 3.13, 3.14 모두 완벽 지원)
* **Git**

### 💻 1) 프로젝트 복제 (Clone)
```bash
git clone https://github.com/sbjwin/star-invader.git
cd star-invader
```

### 🐍 2) 가상환경 생성 및 활성화 (선택 사항이나 권장)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 📦 3) 의존성 라이브러리 설치
게임 실행을 위해 최신 고성능 파이게임 엔진인 `pygame-ce`를 설치합니다:
```bash
pip install pygame-ce
```

### 🎮 4) 게임 실행
```bash
python main.py
```

---

## 🧪 4. 검증 및 테스트 방법

### 1) 모듈 로드 및 의존성 테스트
```bash
python -c "import pygame, constants, resource_loader, bullet, player, enemy, main; print('모든 모듈 및 에셋 정상 로드 완료!')"
```

### 2) 정적 타입 검사 (Pylance / Pyright)
```bash
npx pyright .
```
*(결과: `0 errors, 0 warnings, 0 informations`)*

---

## 🕹️ 5. 게임 조작법 및 규칙

### ⌨️ 조작 키
| 동작 | 키 입력 | 설명 |
| :--- | :--- | :--- |
| **게임 시작** | `Space` | 대기(`READY`) 화면에서 누르면 전투가 시작됩니다. |
| **좌우 이동** | `←` / `→` 또는 `A` / `D` | 플레이어 우주선을 좌우로 이동합니다 (경계 제한). |
| **미사일 발사** | `Space` | 전방으로 에너지 레이저를 발사합니다 (화면 내 최대 3연사). |
| **재시작** | `R` | 게임오버 또는 미션 승리 시 처음부터 다시 시작합니다. |
| **게임 종료** | `ESC` | 게임 창을 즉시 닫습니다. |

### 🏆 승리 & 패배 조건
* **승리 (`MISSION COMPLETE`)**: 8열 × 3행(총 24기)의 외계인 침략 함대를 모두 섬멸하면 승리!
* **패배 (`GAME OVER`)**:
  * 플레이어의 잔여 목숨(3개)이 모두 소진되었을 때
  * 또는 외계인 편대가 화면 최하단의 **지구 방어선(붉은 경고선)**에 도달했을 때 즉시 패배합니다.

---

## 📂 6. 프로젝트 파일 구조

```text
star-invader/
├── assets/                  # 픽셀 아트 이미지 및 가이드북
│   ├── images/
│   │   ├── background/      # 우주 스크롤 배경 및 타이틀 로고
│   │   ├── player/          # 플레이어 메인 전투기 스프라이트
│   │   ├── enemy/           # 상단/중단/하단 외계인 함선 3종
│   │   ├── effects/         # 5단계 순차 폭발 이펙트 시트
│   │   └── ui/              # 탄환 및 목숨 HUD 아이콘
│   └── ASSET_GUIDE.md       # 그래픽 리소스 프롬프트 및 규격 문서
├── constants.py             # ⚙️ 게임 설정 및 수치값 (화면 크기, 속도, 색상 등)
├── resource_loader.py       # 📦 스마트 배경 투명화 및 스프라이트 로더
├── player.py                # 🛸 플레이어 기체 (조작, 발사, 피격 무적 깜빡임)
├── enemy.py                 # 👾 외계인 편대 (8x3 배치, 좌우 왕복/하강, 가속도)
├── bullet.py                # 🚀 플레이어 레이저 및 적 플라즈마 탄환
├── main.py                  # 🎮 메인 게임 루프, 화면 상태 머신 및 렌더링 총괄
├── mvp_plan.md              # 📋 게임 MVP 기획서
└── README.md                # 📖 프로젝트 소개 및 사용 설명서
```

---

## 📜 라이선스
본 프로젝트는 [MIT License](LICENSE)에 따라 자유롭게 학습, 수정 및 배포할 수 있습니다.
