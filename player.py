"""
스타 인베이더 (Star Invader) - 플레이어 기체 모듈 (player.py)
플레이어 우주선 이미지 로드, 이동 조작, 탄환 발사, 피격 무적 깜빡임 효과를 관리합니다.
"""

from typing import Tuple
import pygame
import constants
from bullet import Bullet
from resource_loader import load_image

class Player(pygame.sprite.Sprite):
    """
    플레이어가 조작하는 네온 아케이드 우주선 클래스입니다.
    """
    def __init__(self, x: float, y: float):
        super().__init__()
        
        self.width = constants.PLAYER_WIDTH
        self.height = constants.PLAYER_HEIGHT
        self.speed = constants.PLAYER_SPEED
        self.lives = constants.PLAYER_MAX_LIVES
        
        # 발사 쿨다운 타이머
        self.last_shot_time = 0
        
        # 피격 무적 상태 변수
        self.is_invincible = False
        self.invincible_start_time = 0
        
        # 실제 플레이어 전투기 이미지 로드
        loaded_image: pygame.Surface = load_image(
            constants.IMAGE_PLAYER,
            target_size=(self.width, self.height)
        )
        self.base_image = loaded_image
        self.image = self.base_image.copy()
        self.rect = loaded_image.get_rect(center=(int(x), int(y)))

    @property
    def center_pos(self) -> Tuple[int, int]:
        """기체 중앙 정수 좌표 반환 (타입 안전 보장)"""
        if self.rect is not None:
            return (int(self.rect.centerx), int(self.rect.centery))
        return (constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT - 60)

    def handle_input(self):
        """
        키보드 입력을 감지하여 좌우로 부드럽게 이동합니다.
        """
        if self.rect is None:
            return

        keys = pygame.key.get_pressed()
        
        # 왼쪽 이동 (← 또는 A)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            
        # 오른쪽 이동 (→ 또는 D)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            
        # 화면 좌우 경계 밖으로 나가지 않도록 고정
        if self.rect.left < 10:
            self.rect.left = 10
        if self.rect.right > constants.SCREEN_WIDTH - 10:
            self.rect.right = constants.SCREEN_WIDTH - 10

    def shoot(self, bullet_group: pygame.sprite.Group) -> bool:
        """
        스페이스바 입력 시 전방으로 에너지 레이저를 발사합니다.
        """
        if self.rect is None:
            return False

        current_time = pygame.time.get_ticks()
        
        # 동시 탄환 개수 제한 체크
        player_bullet_count = len([b for b in bullet_group if isinstance(b, Bullet) and not b.is_enemy])
        if player_bullet_count >= constants.PLAYER_MAX_BULLETS:
            return False
            
        # 연사 쿨다운 체크
        if current_time - self.last_shot_time >= constants.PLAYER_SHOOT_COOLDOWN:
            self.last_shot_time = current_time
            # 기체 중앙 상단에서 탄환 발사
            new_bullet = Bullet(self.rect.centerx, self.rect.top, is_enemy=False)
            bullet_group.add(new_bullet)
            return True
            
        return False

    def hit(self) -> bool:
        """
        적 탄환이나 외계인과 충돌했을 때 호출됩니다.
        :return: True면 목숨 감소, False면 무적 상태라 무시됨
        """
        if self.is_invincible:
            return False
            
        self.lives -= 1
        self.is_invincible = True
        self.invincible_start_time = pygame.time.get_ticks()
        return True

    def update(self):
        """
        매 프레임마다 이동 및 무적 깜빡임 애니메이션을 처리합니다.
        """
        self.handle_input()
        
        # 무적 시간 처리 (1.2초 동안 깜빡임)
        if self.is_invincible:
            elapsed = pygame.time.get_ticks() - self.invincible_start_time
            if elapsed >= constants.PLAYER_INVINCIBLE_DURATION:
                self.is_invincible = False
                self.image = self.base_image.copy()
            else:
                # 80ms 주기로 깜빡거리게 만듦
                if (elapsed // 80) % 2 == 0:
                    self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # 투명
                else:
                    self.image = self.base_image.copy()

    def reset_position(self):
        """
        새 게임 시작 시 위치 및 상태 초기화
        """
        if self.rect is not None:
            self.rect.center = (constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT - 60)
        self.is_invincible = False
        self.image = self.base_image.copy()
