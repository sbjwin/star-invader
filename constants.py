"""
스타 인베이더 (Star Invader) - 게임 설정 및 상수 정의 파일
초보자 팁: 게임의 속도, 색상, 점수 및 이미지 파일 경로 등을 변경하고 싶을 때 이 파일의 값들을 수정하면 됩니다.
"""

import os
import sys

# ==========================================
# 1. 경로 설정 (Assets Path & Data Path)
# ==========================================
# 실행 환경(PyInstaller 패키징 여부)에 따른 리소스 디렉토리 결정
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # PyInstaller 패키징 실행 환경
    ASSETS_BASE_DIR = str(sys._MEIPASS)
    DATA_BASE_DIR = os.path.dirname(sys.executable)
else:
    # 일반 파이썬 실행 환경
    ASSETS_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_BASE_DIR = ASSETS_BASE_DIR

BASE_DIR = ASSETS_BASE_DIR
ASSETS_DIR = os.path.join(ASSETS_BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# 세부 이미지 파일 경로
IMAGE_PLAYER = os.path.join(IMAGES_DIR, "player", "player.png")
IMAGE_ENEMY_TOP = os.path.join(IMAGES_DIR, "enemy", "enemy_top.png")
IMAGE_ENEMY_MID = os.path.join(IMAGES_DIR, "enemy", "enemy_mid.png")
IMAGE_ENEMY_BOTTOM = os.path.join(IMAGES_DIR, "enemy", "enemy_bottom.png")
IMAGE_BG_SPACE = os.path.join(IMAGES_DIR, "background", "bg_space.png")
IMAGE_TITLE_LOGO = os.path.join(IMAGES_DIR, "background", "title_logo.png")
IMAGE_EXPLOSION = os.path.join(IMAGES_DIR, "effects", "explosion.png")
IMAGE_BULLET_UI = os.path.join(IMAGES_DIR, "ui", "bullet_and_ui.png")

# 사운드 및 랭킹 파일 경로
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
SOUND_SHOOT = os.path.join(SOUNDS_DIR, "laser_shoot.wav")
RANKING_FILE = os.path.join(DATA_BASE_DIR, "ranking.json")
MAX_RANKING_ENTRIES = 5

# ==========================================
# 2. 화면 및 기본 설정
# ==========================================
SCREEN_WIDTH = 600       # 게임 화면 가로 크기 (픽셀)
SCREEN_HEIGHT = 800      # 게임 화면 세로 크기 (픽셀)
FPS = 60                 # 초당 프레임 수 (60 FPS)
GAME_TITLE = "스타 인베이더 (Star Invader)"

# ==========================================
# 3. 색상 정의 (RGB 값)
# ==========================================
COLOR_BLACK = (10, 10, 20)       # 짙은 우주 배경색
COLOR_WHITE = (255, 255, 255)    # 기본 흰색
COLOR_PLAYER = (80, 220, 100)    # 플레이어 기본 테마 (네온 그린)
COLOR_PLAYER_BULLET = (120, 255, 255) # 플레이어 탄환 색상 (시안)
COLOR_ENEMY_1 = (255, 80, 100)   # 적 1행 색상 (핫 핑크)
COLOR_ENEMY_2 = (255, 180, 50)   # 적 2행 색상 (오렌지)
COLOR_ENEMY_3 = (240, 230, 80)   # 적 3행 색상 (옐로우)
COLOR_ENEMY_BULLET = (255, 100, 100) # 적 탄환 색상 (레드)
COLOR_HUD = (200, 220, 255)      # 상단 HUD UI 색상

# ==========================================
# 4. 플레이어 설정
# ==========================================
PLAYER_WIDTH = 48        # 플레이어 우주선 가로 크기
PLAYER_HEIGHT = 40       # 플레이어 우주선 세로 크기
PLAYER_SPEED = 6         # 플레이어 이동 속도
PLAYER_MAX_LIVES = 3     # 시작 목숨 개수
PLAYER_SHOOT_COOLDOWN = 220  # 발사 제한 시간 (밀리초)
PLAYER_MAX_BULLETS = 3   # 동시 존재 가능한 탄환 수
PLAYER_INVINCIBLE_DURATION = 1200 # 피격 후 무적 지속 시간 (밀리초)

# ==========================================
# 5. 탄환 설정
# ==========================================
BULLET_WIDTH = 8         # 탄환 가로 크기
BULLET_HEIGHT = 20       # 탄환 세로 크기
PLAYER_BULLET_SPEED = 10 # 플레이어 탄환 상승 속도
ENEMY_BULLET_SPEED = 4.5 # 적 탄환 하강 속도

# ==========================================
# 6. 적 편대 (Alien Fleet) 설정
# ==========================================
ENEMY_ROWS = 3           # 적 편대 행 수
ENEMY_COLS = 8           # 적 편대 열 수 (총 24기)
ENEMY_WIDTH = 40         # 적 기체 가로 크기
ENEMY_HEIGHT = 32        # 적 기체 세로 크기
ENEMY_SPACING_X = 58     # 적 가로 간격
ENEMY_SPACING_Y = 44     # 적 세로 간격
ENEMY_START_Y = 110      # 편대 시작 Y 좌표

ENEMY_BASE_SPEED_X = 1.3 # 적 편대 기본 이동 속도
ENEMY_DROP_DISTANCE = 18 # 벽 충돌 시 하강 거리
ENEMY_SHOOT_INTERVAL_MIN = 800   # 사격 최소 간격
ENEMY_SHOOT_INTERVAL_MAX = 2000  # 사격 최대 간격

# ==========================================
# 7. 이펙트 및 비주얼 설정
# ==========================================
EXPLOSION_SIZE = 48      # 폭발 이펙트 크기 (정사각형)
EXPLOSION_FRAMES = 5     # 폭발 스프라이트 프레임 수
EXPLOSION_SPEED = 4      # 폭발 프레임 변경 속도 (틱 단위)
BG_SCROLL_SPEED = 1.2    # 우주 배경 스크롤 속도

# ==========================================
# 8. 점수 및 게임 오버 기준
# ==========================================
SCORE_PER_ENEMY = 100    # 적 격파 점수
INVASION_Y_LIMIT = SCREEN_HEIGHT - 90 # 침략 허용 한계선
