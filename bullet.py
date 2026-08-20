"""
스타 인베이더 (Star Invader) - 탄환 모듈 (bullet.py)
플레이어와 외계인이 발사하는 탄환 스프라이트의 움직임 및 소멸을 관리합니다.
"""

from typing import Tuple
import pygame
import constants
from resource_loader import get_bullet_image

class Bullet(pygame.sprite.Sprite):
    """
    탄환 클래스: 레이저/플라즈마 스프라이트를 표현합니다.
    """
    def __init__(self, x: float, y: float, is_enemy: bool = False):
        """
        :param x: 발사 X 좌표
        :param y: 발사 Y 좌표
        :param is_enemy: True면 적 탄환(아래로 하강), False면 플레이어 탄환(위로 상승)
        """
        super().__init__()
        self.is_enemy = is_enemy
        
        # 탄환 이미지 로드 및 Rect 생성
        bullet_surface: pygame.Surface = get_bullet_image(is_enemy=self.is_enemy)
        self.image = bullet_surface
        self.rect = bullet_surface.get_rect(center=(int(x), int(y)))
        
        # 이동 속도 설정
        if self.is_enemy:
            self.speed = constants.ENEMY_BULLET_SPEED
        else:
            self.speed = -constants.PLAYER_BULLET_SPEED  # 위쪽으로 이동 (음수)

    @property
    def center_pos(self) -> Tuple[int, int]:
        """탄환 중앙 정수 좌표 반환 (타입 안전 보장)"""
        if self.rect is not None:
            return (int(self.rect.centerx), int(self.rect.centery))
        return (0, 0)

    def update(self):
        """
        매 프레임마다 탄환을 이동시키고 화면 밖으로 벗어나면 자동 제거(kill)합니다.
        """
        if self.rect is None:
            return

        self.rect.y += int(self.speed)
        
        # 화면 위/아래를 벗어나면 스프라이트 그룹에서 제거
        if self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()
