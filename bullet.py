"""
스타 인베이더 (Star Invader) - 탄환 모듈 (v1.0)
"""
import pygame
import constants

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, is_enemy: bool = False):
        super().__init__()
        self.is_enemy = is_enemy
        self.width = constants.BULLET_WIDTH
        self.height = constants.BULLET_HEIGHT
        
        if self.is_enemy:
            self.color = constants.COLOR_ENEMY_BULLET
            self.speed = constants.ENEMY_BULLET_SPEED
        else:
            self.color = constants.COLOR_PLAYER_BULLET
            self.speed = -constants.PLAYER_BULLET_SPEED
            
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height), border_radius=2)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()
