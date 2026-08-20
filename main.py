"""
스타 인베이더 (Star Invader) - 메인 게임 실행 파일 (main.py)
타이틀 로고, 우주 배경 스크롤, 5단계 폭발 애니메이션, 기체 스프라이트,
상단 HUD 아이콘 및 게임 상태 머신(대기/플레이/게임오버/승리)을 총괄합니다.
"""

from typing import List, Tuple
import sys
import pygame
import constants
from player import Player
from enemy import Enemy, EnemyFleet
from bullet import Bullet
from resource_loader import load_image, load_sprite_sheet, get_life_icon

# ==========================================
# 1. 5단계 폭발 애니메이션 스프라이트 클래스
# ==========================================
class Explosion(pygame.sprite.Sprite):
    """
    적 격파 또는 플레이어 피격 시 재생되는 5프레임 순차 폭발 애니메이션입니다.
    """
    _FRAMES: List[pygame.Surface] = []

    def __init__(self, center_pos: Tuple[int, int], size: int = constants.EXPLOSION_SIZE):
        super().__init__()
        
        # 폭발 프레임 최초 1회 로드 (배경 스마트 투명화)
        if not Explosion._FRAMES:
            Explosion._FRAMES = load_sprite_sheet(
                constants.IMAGE_EXPLOSION,
                frame_count=constants.EXPLOSION_FRAMES,
                target_size=(size, size),
                transparent_bg=True
            )
            
        self.frames = Explosion._FRAMES
        self.current_frame = 0
        self.anim_speed = constants.EXPLOSION_SPEED
        self.anim_timer = 0
        
        # 첫 번째 프레임 표면에서 직접 Rect 생성
        frame_surface: pygame.Surface = self.frames[self.current_frame]
        self.image = frame_surface
        self.rect = frame_surface.get_rect(center=center_pos)

    def update(self):
        """
        프레임 타이머에 따라 다음 폭발 이미지로 교체하고, 끝나면 자동 삭제합니다.
        """
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.current_frame += 1
            
            if self.current_frame < len(self.frames):
                self.image = self.frames[self.current_frame]
            else:
                self.kill() # 5프레임 애니메이션 종료 후 소멸


# ==========================================
# 2. 게임 메인 클래스
# ==========================================
class StarInvaderGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(constants.GAME_TITLE)
        
        self.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # 폰트 로드
        self._init_fonts()
        
        # 그래픽 리소스 로드
        self._load_graphics()
        
        # 게임 상태 변수 ("READY", "PLAYING", "GAME_OVER", "VICTORY")
        self.state = "READY"
        self.score = 0
        
        # 스프라이트 및 게임 오브젝트 초기화
        self._init_game_objects()

    def _init_fonts(self):
        """
        한글 폰트를 안전하게 로드합니다.
        """
        korean_fonts = ["malgungothic", "맑은고딕", "nanumgothic", "applegothic", "d2coding", "arial"]
        font_name = None
        for font in korean_fonts:
            if pygame.font.match_font(font):
                font_name = font
                break
                
        self.font_title = pygame.font.SysFont(font_name, 36, bold=True)
        self.font_main = pygame.font.SysFont(font_name, 22, bold=True)
        self.font_sub = pygame.font.SysFont(font_name, 17)

    def _load_graphics(self):
        """
        타이틀 로고, 우주 배경, HUD 아이콘 등의 그래픽 에셋을 준비합니다.
        """
        # 1. 우주 배경 이미지 (화면 크기에 맞춤, 배경 불투명)
        self.bg_space = load_image(
            constants.IMAGE_BG_SPACE,
            target_size=(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            transparent_bg=False
        )
        self.bg_scroll_y = 0.0 # 배경 무한 스크롤 Y 좌표
        
        # 2. 타이틀 로고 이미지 (가로 440px, 세로 160px, 스마트 투명화)
        self.title_logo = load_image(
            constants.IMAGE_TITLE_LOGO,
            target_size=(440, 160),
            transparent_bg=True
        )
        
        # 3. HUD 잔여 목숨용 미니 우주선 아이콘
        self.life_icon = get_life_icon()

    def _init_game_objects(self):
        """
        플레이어, 적 편대, 탄환 및 폭발 스프라이트 그룹을 생성합니다.
        """
        self.player = Player(
            constants.SCREEN_WIDTH // 2,
            constants.SCREEN_HEIGHT - 60
        )
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.bullet_group = pygame.sprite.Group()
        self.enemy_fleet = EnemyFleet()
        self.explosion_group = pygame.sprite.Group()

    def reset_game(self):
        """
        새 게임을 시작할 때 점수와 오브젝트를 리셋합니다.
        """
        self.score = 0
        self._init_game_objects()
        self.state = "PLAYING"

    def handle_events(self):
        """
        키보드 입력을 처리합니다.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                    
                # 대기 화면에서 시작
                if self.state == "READY":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        
                # 플레이 중 탄환 발사
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        self.player.shoot(self.bullet_group)
                        
                # 게임오버/승리 시 재시작
                elif self.state in ["GAME_OVER", "VICTORY"]:
                    if event.key == pygame.K_r:
                        self.reset_game()

    def update(self):
        """
        배경 스크롤 및 게임 상태를 업데이트합니다.
        """
        # 우주 배경 무한 스크롤 이동
        self.bg_scroll_y += constants.BG_SCROLL_SPEED
        if self.bg_scroll_y >= constants.SCREEN_HEIGHT:
            self.bg_scroll_y = 0

        # 폭발 애니메이션은 모든 화면 상태에서 계속 업데이트
        self.explosion_group.update()

        # 실제 게임 플레이 중일 때
        if self.state == "PLAYING":
            self.player_group.update()
            self.bullet_group.update()
            self.enemy_fleet.update(self.bullet_group)
            
            # 충돌 검사
            self._check_collisions()
            
            # 승리 조건
            if len(self.enemy_fleet.enemies) == 0:
                self.state = "VICTORY"
                
            # 패배 조건
            elif self.player.lives <= 0:
                self.state = "GAME_OVER"
            elif self.enemy_fleet.has_invaded():
                self.state = "GAME_OVER"

    def _check_collisions(self):
        """
        탄환과 기체 간 충돌 판정 및 폭발 이펙트 생성
        """
        # 1. 플레이어 탄환 ↔ 적 외계인 충돌
        for sprite in self.bullet_group.sprites():
            if isinstance(sprite, Bullet) and not sprite.is_enemy:
                hit_enemies = pygame.sprite.spritecollide(sprite, self.enemy_fleet.enemies, True)
                if hit_enemies:
                    sprite.kill()
                    for enemy in hit_enemies:
                        if isinstance(enemy, Enemy):
                            self.score += constants.SCORE_PER_ENEMY
                            # 격파된 외계인 위치에 5단계 폭발 생성
                            self.explosion_group.add(Explosion(enemy.center_pos))

        # 2. 적 탄환 ↔ 플레이어 충돌
        for sprite in self.bullet_group.sprites():
            if isinstance(sprite, Bullet) and sprite.is_enemy:
                if pygame.sprite.collide_rect(sprite, self.player):
                    if self.player.hit():
                        sprite.kill()
                        # 플레이어 위치에 피격 폭발 이펙트 생성
                        self.explosion_group.add(Explosion(self.player.center_pos))

        # 3. 외계인 ↔ 플레이어 직접 충돌
        if pygame.sprite.spritecollide(self.player, self.enemy_fleet.enemies, False):
            if self.player.hit():
                self.explosion_group.add(Explosion(self.player.center_pos))

    def draw(self):
        """
        화면을 렌더링합니다.
        """
        # 1. 우주 배경 무한 스크롤 그리기
        self._draw_scrolling_background()

        # 2. 폭발 이펙트 그리기
        self.explosion_group.draw(self.screen)

        # 3. 상태별 화면 그리기
        if self.state == "READY":
            self._draw_ready_screen()
        elif self.state == "PLAYING":
            self._draw_playing_screen()
        elif self.state == "GAME_OVER":
            self._draw_game_over_screen()
        elif self.state == "VICTORY":
            self._draw_victory_screen()

        pygame.display.flip()

    def _draw_scrolling_background(self):
        """
        우주 배경 이미지를 위아래로 이어 붙여 끊김 없이 부드럽게 스크롤합니다.
        """
        y1 = int(self.bg_scroll_y)
        y2 = y1 - constants.SCREEN_HEIGHT
        self.screen.blit(self.bg_space, (0, y1))
        self.screen.blit(self.bg_space, (0, y2))

    def _draw_playing_screen(self):
        """
        게임 진행 중: 외계인 편대, 탄환, 플레이어 및 HUD 표시
        """
        # 외계인 편대 그리기
        self.enemy_fleet.enemies.draw(self.screen)
        
        # 탄환 그리기
        self.bullet_group.draw(self.screen)
        
        # 플레이어 우주선 그리기
        self.player_group.draw(self.screen)
        
        # 폭발 이펙트 (오브젝트 위로 렌더링)
        self.explosion_group.draw(self.screen)
        
        # 상단 HUD 그리기
        self._draw_hud()

    def _draw_hud(self):
        """
        상단 점수(SCORE)와 미니 기체 아이콘 기반 목숨(LIVES)을 표시합니다.
        """
        # 점수 표시
        score_str = f"SCORE: {self.score:06d}"
        score_surf = self.font_main.render(score_str, True, constants.COLOR_HUD)
        self.screen.blit(score_surf, (20, 16))
        
        # 목숨 라벨 표시
        lives_label = self.font_main.render("LIVES:", True, constants.COLOR_HUD)
        label_x = constants.SCREEN_WIDTH - 150
        self.screen.blit(lives_label, (label_x, 16))
        
        # 미니 우주선 아이콘으로 목숨 개수 표시
        icon_start_x = label_x + lives_label.get_width() + 10
        for i in range(max(0, self.player.lives)):
            self.screen.blit(self.life_icon, (icon_start_x + i * 28, 14))
            
        # 상단 HUD 구분선 (사이버 블루 네온 라인)
        pygame.draw.line(self.screen, (60, 100, 150), (0, 50), (constants.SCREEN_WIDTH, 50), 2)
        
        # 하단 방어선 (은은한 붉은 경고선)
        pygame.draw.line(
            self.screen, (120, 30, 40),
            (0, constants.INVASION_Y_LIMIT),
            (constants.SCREEN_WIDTH, constants.INVASION_Y_LIMIT),
            1
        )

    def _draw_ready_screen(self):
        """
        시작 대기 화면: 타이틀 로고 이미지와 조작법 안내를 표시합니다.
        """
        cx = constants.SCREEN_WIDTH // 2
        
        # 타이틀 로고 이미지 렌더링
        logo_rect = self.title_logo.get_rect(center=(cx, 220))
        self.screen.blit(self.title_logo, logo_rect)
        
        # 반투명 안내 패널 박스
        panel_rect = pygame.Rect(cx - 240, 360, 480, 260)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((10, 15, 30, 180)) # 짙은 반투명 남색
        pygame.draw.rect(panel_surface, (80, 140, 220), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # 시작 버튼 깜빡임 연출
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            start_surf = self.font_main.render("[ SPACE ] 키를 눌러 출격", True, constants.COLOR_ENEMY_3)
            self.screen.blit(start_surf, (cx - start_surf.get_width() // 2, 385))
        else:
            start_surf = self.font_main.render("[ SPACE ] 키를 눌러 출격", True, constants.COLOR_WHITE)
            self.screen.blit(start_surf, (cx - start_surf.get_width() // 2, 385))

        # 조작 가이드
        controls_1 = self.font_sub.render("조작법: [ ← / → ] 또는 [ A / D ] 키로 좌우 이동", True, constants.COLOR_WHITE)
        controls_2 = self.font_sub.render("사격: [ SPACE ] 키 (최대 3연사)", True, constants.COLOR_PLAYER_BULLET)
        controls_3 = self.font_sub.render("외계인이 지구 방어선에 도달하기 전에 모두 섬멸하세요!", True, constants.COLOR_ENEMY_2)
        
        self.screen.blit(controls_1, (cx - controls_1.get_width() // 2, 450))
        self.screen.blit(controls_2, (cx - controls_2.get_width() // 2, 490))
        self.screen.blit(controls_3, (cx - controls_3.get_width() // 2, 530))

    def _draw_game_over_screen(self):
        """
        패배 화면: 게임오버 문구 및 최종 점수
        """
        cx = constants.SCREEN_WIDTH // 2
        
        title_surf = self.font_title.render("GAME OVER", True, constants.COLOR_ENEMY_1)
        score_surf = self.font_main.render(f"최종 점수: {self.score:,}점", True, constants.COLOR_WHITE)
        restart_surf = self.font_main.render("[ R ] 키를 눌러 다시 도전", True, constants.COLOR_HUD)
        quit_surf = self.font_sub.render("[ ESC ] 키: 게임 종료", True, (160, 160, 180))
        
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 280))
        self.screen.blit(score_surf, (cx - score_surf.get_width() // 2, 360))
        self.screen.blit(restart_surf, (cx - restart_surf.get_width() // 2, 440))
        self.screen.blit(quit_surf, (cx - quit_surf.get_width() // 2, 500))

    def _draw_victory_screen(self):
        """
        승리 화면: 축하 문구 및 최종 점수
        """
        cx = constants.SCREEN_WIDTH // 2
        
        title_surf = self.font_title.render("★ MISSION COMPLETE ★", True, constants.COLOR_ENEMY_3)
        msg_surf = self.font_main.render("외계인 군단을 모두 섬멸했습니다!", True, constants.COLOR_PLAYER)
        score_surf = self.font_main.render(f"최종 점수: {self.score:,}점", True, constants.COLOR_WHITE)
        restart_surf = self.font_main.render("[ R ] 키를 눌러 다시 플레이", True, constants.COLOR_HUD)
        quit_surf = self.font_sub.render("[ ESC ] 키: 게임 종료", True, (160, 160, 180))
        
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 260))
        self.screen.blit(msg_surf, (cx - msg_surf.get_width() // 2, 320))
        self.screen.blit(score_surf, (cx - score_surf.get_width() // 2, 380))
        self.screen.blit(restart_surf, (cx - restart_surf.get_width() // 2, 460))
        self.screen.blit(quit_surf, (cx - quit_surf.get_width() // 2, 520))

    def run(self):
        """
        게임 실행 루프
        """
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(constants.FPS)
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = StarInvaderGame()
    game.run()
