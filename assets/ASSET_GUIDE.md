# 🎨 스타 인베이더 (Star Invader) - 그래픽 에셋 가이드북

본 문서는 프로젝트 내 생성된 모든 그래픽 리소스(`assets/images/`)의 상세 스펙, 비주얼 컨셉, AI 생성 프롬프트, 그리고 Pygame 코드 연동 가이드를 영구 보존하기 위한 가이드 문서입니다.

---

## 📑 목차
1. [에셋 개요 및 파일 매핑](#1-에셋-개요-및-파일-매핑)
2. [에셋별 상세 가이드 및 생성 프롬프트](#2-에셋별-상세-가이드-및-생성-프롬프트)
   - [플레이어 전투기 (`player.png`)](#1-플레이어-전투기-playerpng)
   - [적 편대 상단 - 사령관 (`enemy_top.png`)](#2-적-편대-상단---사령관-enemy_toppng)
   - [적 편대 중단 - 돌격형 (`enemy_mid.png`)](#3-적-편대-중단---돌격형-enemy_midpng)
   - [적 편대 하단 - 보병형 (`enemy_bottom.png`)](#4-적-편대-하단---보병형-enemy_bottompng)
   - [우주 배경 (`bg_space.png`)](#5-우주-배경-bg_spacepng)
   - [폭발 이펙트 시트 (`explosion.png`)](#6-폭발-이펙트-시트-explosionpng)
   - [탄환 & HUD 아이콘 (`bullet_and_ui.png`)](#7-탄환--hud-아이콘-bullet_and_uipng)
   - [타이틀 로고 (`title_logo.png`)](#8-타이틀-로고-title_logopng)
3. [Pygame 코드 연동 및 처리 팁](#3-pygame-코드-연동-및-처리-팁)

---

## 1. 에셋 개요 및 파일 매핑

| 파일 경로 | 용도 | 권장 인게임 크기 | 원본 해상도 |
| :--- | :--- | :--- | :--- |
| `player/player.png` | 플레이어 우주선 | `44 × 28 px` | 1024 × 1024 |
| `enemy/enemy_top.png` | 상단 지휘관 외계인 (Row 0) | `36 × 24 px` | 1024 × 1024 |
| `enemy/enemy_mid.png` | 중단 돌격 외계인 (Row 1) | `36 × 24 px` | 1024 × 1024 |
| `enemy/enemy_bottom.png` | 하단 보병 외계인 (Row 2) | `36 × 24 px` | 1024 × 1024 |
| `enemy/enemy_ufo.png` | 보너스 점수 외계 UFO 모함 | `48 × 48 px` | 1024 × 1024 |
| `enemy/enemy_stealth.png` | 엘리트 스텔스 요격기 | `44 × 44 px` | 1024 × 1024 |
| `enemy/enemy_boss.png` | 중장갑 드레드노트 보스 | `64 × 64 px` | 1024 × 1024 |
| `background/bg_space.png` | 인게임 메인 우주 배경 | `600 × 800 px` | 768 × 1024 |
| `effects/explosion.png` | 적/플레이어 격파 폭발 시트 | 프레임당 `32×32` ~ `48×48` | 1792 × 1024 |
| `ui/bullet_and_ui.png` | 탄환 및 목숨 HUD 아이콘 | 아이콘당 `8×16` ~ `16×16` | 1024 × 1024 |
| `background/title_logo.png` | 시작 대기 화면 타이틀 로고 | `400 × 120 px` | 1792 × 1024 |

---

## 2. 에셋별 상세 가이드 및 생성 프롬프트

### 1) 플레이어 전투기 (`player.png`)
- **역할**: 사용자가 조작하는 1P 메인 아케이드 전투기
- **비주얼 컨셉**: 네온 그린과 사이버 시안의 기체 장갑, 하단 고출력 불꽃 분사
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art sprite of a sleek heroic retro spaceship fighter, top-down vertical scrolling view, centered, vibrant neon green and cyber cyan color scheme with bright white highlights, glowing engine thruster, crisp clean pixel lines, sharp edges, isolated on solid pure black background, authentic arcade game asset, no anti-aliasing
  ```

### 2) 적 편대 상단 - 사령관 (`enemy_top.png`)
- **역할**: 적 편대 최상단(Row 0)에 위치하는 고득점 지휘관 외계인
- **비주얼 컨셉**: 핫핑크/마젠타 장갑판, 붉은 눈과 생체 촉수를 지닌 외계 사령관
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art sprite of an alien commander flagship, octopus-like biometric invader with glowing red eyes, hot pink and magenta cyber armor, top-down vertical scrolling view, centered, clean pixel contours, sharp edges, isolated on solid pure black background, authentic retro arcade shmup asset, no anti-aliasing
  ```

### 3) 적 편대 중단 - 돌격형 (`enemy_mid.png`)
- **역할**: 적 편대 중간(Row 1)에 위치하는 중형 갑각류 드론
- **비주얼 컨셉**: 오렌지 컬러 장갑판, 중앙 발광 코어, 공격적인 집게발
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art sprite of an armored alien crab assault drone, glowing orange carapace with yellow energy core, aggressive pincers and mechanical legs, top-down vertical scrolling view, centered, clean pixel contours, sharp edges, isolated on solid pure black background, authentic retro arcade shmup asset, no anti-aliasing
  ```

### 4) 적 편대 하단 - 보병형 (`enemy_bottom.png`)
- **역할**: 적 편대 하단(Row 2)에서 전선을 형성하는 비틀형 침략기
- **비주얼 컨셉**: 일렉트릭 옐로우 & 라임 외골격, 날카로운 턱과 더듬이
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art sprite of a swarm insect alien beetle drone, bright electric yellow and lime exoskeleton, glowing antenna and sharp mandibles, top-down vertical scrolling view, centered, clean pixel contours, sharp edges, isolated on solid pure black background, authentic retro arcade shmup asset, no anti-aliasing
  ```

### 5) 우주 배경 (`bg_space.png`)
- **역할**: 세로 스크롤 및 고정 화면을 받쳐주는 깊은 우주 배경
- **비주얼 컨셉**: 딥 네이비 & 다크 퍼플 성운, 회전 은하와 흩뿌려진 픽셀 별빛
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art vertical scrolling deep space background, glowing cosmic nebulas in dark purple and deep navy blue, distant shining pixel stars and galaxy clusters, clean retro arcade sci-fi aesthetic, seamless texture, sharp pixels, no blur, high contrast
  ```

### 6) 폭발 이펙트 시트 (`explosion.png`)
- **역할**: 기체 격파 시 재생되는 5단계 순차 폭발 애니메이션
- **비주얼 컨셉**: 중심 코어 폭발부터 바깥 충격파 및 파편 분산까지의 5프레임 시퀀스
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art sprite sheet of a sci-fi space explosion sequence, 5 sequential animation frames from left to right, brilliant bright fiery core bursting into expanding neon orange and yellow shockwave particles, isolated on solid pure black background, arcade game fx asset, crisp pixel edges, sharp details
  ```

### 7) 탄환 & HUD 아이콘 (`bullet_and_ui.png`)
- **역할**: 플레이어 레이저, 적 탄환, 우측 상단 잔여 목숨(Lives) 하트 실드 아이콘
- **AI 생성 프롬프트**:
  ```text
  16-bit pixel art game asset sheet containing: cyan glowing energy laser bolts, red plasma enemy bullets, and a mini neon green spaceship heart shield icon for lives counter, isolated on solid pure black background, crisp pixel edges, arcade game assets
  ```

### 8) 타이틀 로고 (`title_logo.png`)
- **역할**: 대기 화면(READY 상태) 중앙에 배치할 아케이드 엠블럼
- **비주얼 컨셉**: 80~90년대 레트로 네온 크롬 베벨 스타일의 "STAR INVADER" 타이틀 로고
- **AI 생성 프롬프트**:
  ```text
  16-bit arcade pixel art game title logo with glowing futuristic chrome and neon cyan/magenta bevel text spelling STAR INVADER, with pixel stars and grid lines, isolated on solid pure black background, authentic 80s 90s retro arcade logo, crisp pixels
  ```

---

## 3. Pygame 코드 연동 및 처리 팁

### ① 검은색 배경 투명화 (Color-Key) & 크기 스케일링
생성된 스프라이트는 배경이 순수 검은색(`(0, 0, 0)`)으로 처리되어 있으므로, 로드 후 크기를 조정하고 `set_colorkey`를 호출하면 깔끔하게 투명화됩니다.

```python
import pygame

def load_sprite(path, target_width, target_height):
    # 이미지 로드
    raw_img = pygame.image.load(path).convert()
    # 검은색 배경 투명 처리
    raw_img.set_colorkey((0, 0, 0))
    # 게임 스펙 크기로 스케일 (스무딩 없이 깔끔한 도트 유지)
    scaled_img = pygame.transform.scale(raw_img, (target_width, target_height))
    return scaled_img

# 사용 예시:
# player_img = load_sprite("assets/images/player.png", 44, 28)
```

### ② 배경 이미지 로드 (전체 화면 맞춤)
```python
bg_image = pygame.image.load("assets/images/bg_space.png").convert()
bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 메인 루프에서:
# screen.blit(bg_image, (0, 0))
```
