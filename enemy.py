"""
스타 인베이더 (Star Invader) - 적 외계인 및 편대 모듈 (enemy.py)
8열 x 3행(24기)의 실제 외계인 스프라이트 생성, 좌우 왕복 이동 및 하강,
가속 긴장감 로직, 무작위 사격을 총괄합니다.
"""

from typing import Tuple
import random
import pygame
import constants
from bullet import Bullet
from resource_loader import load_image

class Enemy(pygame.sprite.Sprite):
    """
    개별 외계인 스프라이트 클래스입니다.
    """
    def __init__(self, x: float, y: float, row: int):
        """
        :param x: 외계인 X 좌표
        :param y: 외계인 Y 좌표
        :param row: 0 (상단 사령관), 1 (중단 돌격형), 2 (하단 보병형)
        """
        super().__init__()
        self.row = row
        self.width = constants.ENEMY_WIDTH
        self.height = constants.ENEMY_HEIGHT
        
        # 행에 따른 외계인 이미지 파일 및 대표 색상 설정
        if row == 0:
            image_path = constants.IMAGE_ENEMY_TOP
            self.color = constants.COLOR_ENEMY_1
        elif row == 1:
            image_path = constants.IMAGE_ENEMY_MID
            self.color = constants.COLOR_ENEMY_2
        else:
            image_path = constants.IMAGE_ENEMY_BOTTOM
            self.color = constants.COLOR_ENEMY_3
            
        # 외계인 이미지 로드 및 Rect 생성
        loaded_img: pygame.Surface = load_image(image_path, target_size=(self.width, self.height))
        self.image = loaded_img
        self.rect = loaded_img.get_rect(topleft=(int(x), int(y)))

    @property
    def center_pos(self) -> Tuple[int, int]:
        """외계인 중앙 정수 좌표 반환 (타입 안전 보장)"""
        if self.rect is not None:
            return (int(self.rect.centerx), int(self.rect.centery))
        return (0, 0)


class EnemyFleet:
    """
    8x3 편대 전체를 일괄 통솔하는 외계인 군단 관리 클래스입니다.
    """
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.direction_x = 1 # 1: 오른쪽, -1: 왼쪽
        
        self.last_shoot_time = pygame.time.get_ticks()
        self.shoot_interval = random.randint(
            constants.ENEMY_SHOOT_INTERVAL_MIN,
            constants.ENEMY_SHOOT_INTERVAL_MAX
        )
        
        self.create_fleet()

    def create_fleet(self):
        """
        8열 x 3행의 외계인 편대를 생성합니다.
        """
        self.enemies.empty()
        
        total_fleet_width = (constants.ENEMY_COLS - 1) * constants.ENEMY_SPACING_X + constants.ENEMY_WIDTH
        start_x = (constants.SCREEN_WIDTH - total_fleet_width) // 2
        
        for row in range(constants.ENEMY_ROWS):
            for col in range(constants.ENEMY_COLS):
                enemy_x = start_x + col * constants.ENEMY_SPACING_X
                enemy_y = constants.ENEMY_START_Y + row * constants.ENEMY_SPACING_Y
                enemy = Enemy(enemy_x, enemy_y, row)
                self.enemies.add(enemy)

    def get_current_speed(self) -> float:
        """
        남은 적의 수에 반비례하여 이동 속도를 점진적으로 증가시킵니다.
        """
        total_initial = constants.ENEMY_ROWS * constants.ENEMY_COLS
        remaining = len(self.enemies)
        if remaining == 0:
            return constants.ENEMY_BASE_SPEED_X
            
        speed_factor = 1.0 + (1.0 - (remaining / total_initial)) * 2.5
        return constants.ENEMY_BASE_SPEED_X * speed_factor

    def update(self, bullet_group: pygame.sprite.Group):
        """
        편대 이동, 벽 충돌 시 반대 방향 전환 및 하강, 무작위 사격을 처리합니다.
        """
        if not self.enemies:
            return

        current_speed = self.get_current_speed()
        move_down = False
        
        # 1. 좌우 이동 및 화면 끝 감지
        for sprite in self.enemies.sprites():
            if isinstance(sprite, Enemy) and sprite.rect is not None:
                sprite.rect.x += int(self.direction_x * current_speed)
                
                if self.direction_x > 0 and sprite.rect.right >= constants.SCREEN_WIDTH - 15:
                    move_down = True
                elif self.direction_x < 0 and sprite.rect.left <= 15:
                    move_down = True

        # 2. 벽에 닿았으면 방향 전환 후 전체 하강
        if move_down:
            self.direction_x *= -1
            for sprite in self.enemies.sprites():
                if isinstance(sprite, Enemy) and sprite.rect is not None:
                    sprite.rect.y += constants.ENEMY_DROP_DISTANCE

        # 3. 무작위 탄환 발사
        self._handle_shooting(bullet_group)

    def _handle_shooting(self, bullet_group: pygame.sprite.Group):
        """
        무작위 적을 선택하여 하단으로 레이저를 투하합니다.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot_time >= self.shoot_interval:
            self.last_shoot_time = current_time
            self.shoot_interval = random.randint(
                constants.ENEMY_SHOOT_INTERVAL_MIN,
                constants.ENEMY_SHOOT_INTERVAL_MAX
            )
            
            sprites = self.enemies.sprites()
            if sprites:
                shooting_enemy = random.choice(sprites)
                if isinstance(shooting_enemy, Enemy) and shooting_enemy.rect is not None:
                    new_bullet = Bullet(
                        shooting_enemy.rect.centerx,
                        shooting_enemy.rect.bottom,
                        is_enemy=True
                    )
                    bullet_group.add(new_bullet)

    def has_invaded(self) -> bool:
        """
        외계인이 방어선에 도달했는지 확인합니다.
        """
        for sprite in self.enemies.sprites():
            if isinstance(sprite, Enemy) and sprite.rect is not None:
                if sprite.rect.bottom >= constants.INVASION_Y_LIMIT:
                    return True
        return False
