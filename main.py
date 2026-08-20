"""
스타 인베이더 (Star Invader) - 메인 게임 실행 파일 (main.py)
타이틀 로고, 우주 배경 스크롤, 5단계 폭발 애니메이션, 기체 스프라이트,
상단 HUD 숫자 생명 표시, 탄환 발사 사운드, 3글자 이니셜 랭킹 영구 저장 시스템을 총괄합니다.
"""

from typing import List, Tuple
import sys
import pygame
import constants
from player import Player
from enemy import Enemy, EnemyFleet
from bullet import Bullet
from resource_loader import load_image, load_sprite_sheet, get_life_icon
from sound_manager import SoundManager
from ranking_manager import RankingManager

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
        
        # 사운드 시스템 초기화 및 발사 사운드 준비
        SoundManager.init()
        
        self.screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # 폰트 로드
        self._init_fonts()
        
        # 그래픽 리소스 로드
        self._load_graphics()
        
        # 게임 상태 변수 ("READY", "PLAYING", "NAME_ENTRY", "GAME_OVER", "VICTORY")
        self.state = "READY"
        self.game_end_reason = "GAME_OVER"
        self.score = 0
        
        # 랭킹 및 이니셜 입력 변수
        self.player_name = ""
        self.latest_rank = -1
        self.rankings = RankingManager.load_rankings()
        
        # 스프라이트 및 게임 오브젝트 초기화
        self._init_game_objects()

    def _init_fonts(self):
        """
        한글 폰트 및 모노스페이스 폰트를 안전하게 로드합니다.
        """
        korean_fonts = ["malgungothic", "맑은고딕", "nanumgothic", "applegothic", "d2coding", "arial"]
        font_name = None
        for font in korean_fonts:
            if pygame.font.match_font(font):
                font_name = font
                break
                
        self.font_title = pygame.font.SysFont(font_name, 36, bold=True)
        self.font_main = pygame.font.SysFont(font_name, 22, bold=True)
        self.font_sub = pygame.font.SysFont(font_name, 16)
        self.font_entry = pygame.font.SysFont(font_name, 40, bold=True)
        self.font_rank = pygame.font.SysFont("consolas", 19, bold=True)

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
        새 게임을 시작할 때 점수, 이니셜 및 오브젝트를 리셋합니다.
        """
        self.score = 0
        self.player_name = ""
        self.latest_rank = -1
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
                        
                # 플레이 중 탄환 발사 및 비프 사운드 재생
                elif self.state == "PLAYING":
                    if event.key == pygame.K_SPACE:
                        if self.player.shoot(self.bullet_group):
                            SoundManager.play_shoot()
                            
                # 게임 종료 후 3글자 이니셜 입력 처리
                elif self.state == "NAME_ENTRY":
                    if event.key == pygame.K_RETURN:
                        # 이름 확정 및 랭킹 저장
                        final_name = self.player_name.strip() if self.player_name.strip() else "AAA"
                        self.latest_rank = RankingManager.add_score(final_name, self.score)
                        self.rankings = RankingManager.load_rankings()
                        self.state = self.game_end_reason
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        # 알파벳 A-Z 입력 허용 (최대 3글자)
                        if len(self.player_name) < 3 and event.unicode and event.unicode.isalpha():
                            self.player_name += event.unicode.upper()

                # 게임오버/승리 랭킹 화면에서 재시작
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
            
            # 승리 조건 (적 전멸 시 이니셜 입력 단계로 전환)
            if len(self.enemy_fleet.enemies) == 0:
                self.game_end_reason = "VICTORY"
                self.player_name = ""
                self.state = "NAME_ENTRY"
                
            # 패배 조건 (생명 0 소진 또는 적 침공 시)
            elif self.player.lives <= 0:
                self.game_end_reason = "GAME_OVER"
                self.player_name = ""
                self.state = "NAME_ENTRY"
            elif self.enemy_fleet.has_invaded():
                self.game_end_reason = "GAME_OVER"
                self.player_name = ""
                self.state = "NAME_ENTRY"

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
        elif self.state == "NAME_ENTRY":
            self._draw_name_entry_screen()
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
        상단 점수(SCORE)와 우측 상단 숫자 기반 생명(LIVES)을 명확하게 표시합니다.
        """
        # 1. 좌측 상단 점수 표시
        score_str = f"SCORE: {self.score:06d}"
        score_surf = self.font_main.render(score_str, True, constants.COLOR_HUD)
        self.screen.blit(score_surf, (20, 16))
        
        # 2. 우측 상단 생명 숫자 표시 (요구사항: 오른쪽 상단에 숫자로 표시)
        current_lives = max(0, self.player.lives)
        lives_str = f"LIVES: {current_lives}"
        
        # 생명이 1개 남았을 때는 경고색(붉은색), 그 외에는 네온 그린으로 표시
        lives_color = constants.COLOR_ENEMY_1 if current_lives <= 1 else constants.COLOR_PLAYER
        lives_surf = self.font_main.render(lives_str, True, lives_color)
        lives_x = constants.SCREEN_WIDTH - lives_surf.get_width() - 20
        self.screen.blit(lives_surf, (lives_x, 16))
        
        # 생명 숫자 왼쪽에 미니 기체 아이콘 함께 배치
        icon_x = lives_x - self.life_icon.get_width() - 8
        self.screen.blit(self.life_icon, (icon_x, 18))
            
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
        logo_rect = self.title_logo.get_rect(center=(cx, 200))
        self.screen.blit(self.title_logo, logo_rect)
        
        # 반투명 안내 패널 박스
        panel_rect = pygame.Rect(cx - 240, 330, 480, 290)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((10, 15, 30, 190))
        pygame.draw.rect(panel_surface, (80, 140, 220), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # 시작 버튼 깜빡임 연출
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            start_surf = self.font_main.render("[ SPACE ] 키를 눌러 출격", True, constants.COLOR_ENEMY_3)
        else:
            start_surf = self.font_main.render("[ SPACE ] 키를 눌러 출격", True, constants.COLOR_WHITE)
        self.screen.blit(start_surf, (cx - start_surf.get_width() // 2, 355))

        # 조작 가이드
        controls_1 = self.font_sub.render("조작법: [ ← / → ] 또는 [ A / D ] 키로 좌우 이동", True, constants.COLOR_WHITE)
        controls_2 = self.font_sub.render("사격: [ SPACE ] 키 (레이저 발사음 효과)", True, constants.COLOR_PLAYER_BULLET)
        controls_3 = self.font_sub.render(f"시작 생명: {constants.PLAYER_MAX_LIVES}개 (우측 상단에 표시)", True, constants.COLOR_PLAYER)
        controls_4 = self.font_sub.render("게임 종료 후 3글자 이니셜을 등록하여 랭킹에 도전하세요!", True, constants.COLOR_ENEMY_2)
        
        self.screen.blit(controls_1, (cx - controls_1.get_width() // 2, 415))
        self.screen.blit(controls_2, (cx - controls_2.get_width() // 2, 455))
        self.screen.blit(controls_3, (cx - controls_3.get_width() // 2, 495))
        self.screen.blit(controls_4, (cx - controls_4.get_width() // 2, 535))

    def _draw_name_entry_screen(self):
        """
        게임 종료 후 3글자 알파벳 이니셜을 입력하는 네임 엔트리 화면
        """
        cx = constants.SCREEN_WIDTH // 2
        
        # 반투명 카드 패널
        panel_rect = pygame.Rect(cx - 240, 180, 480, 440)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((10, 15, 30, 220))
        border_color = constants.COLOR_ENEMY_3 if self.game_end_reason == "VICTORY" else constants.COLOR_ENEMY_1
        pygame.draw.rect(panel_surface, border_color, (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=10)
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # 1. 상단 타이틀
        title_text = "★ NEW RECORD ★" if self.game_end_reason == "VICTORY" else "GAME OVER"
        title_surf = self.font_title.render(title_text, True, border_color)
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 210))
        
        # 2. 최종 점수 표시
        score_surf = self.font_main.render(f"최종 점수: {self.score:,}점", True, constants.COLOR_WHITE)
        self.screen.blit(score_surf, (cx - score_surf.get_width() // 2, 270))
        
        # 3. 이니셜 입력 안내
        guide_surf = self.font_sub.render("알파벳 3글자 이니셜을 입력하세요 (A~Z)", True, constants.COLOR_HUD)
        self.screen.blit(guide_surf, (cx - guide_surf.get_width() // 2, 325))
        
        # 4. 3글자 입력 슬롯 박스 렌더링
        box_w, box_h = 64, 76
        gap = 18
        total_w = box_w * 3 + gap * 2
        start_x = cx - total_w // 2
        box_y = 370
        
        blink = (pygame.time.get_ticks() // 350) % 2 == 0
        
        for i in range(3):
            cur_box_x = start_x + i * (box_w + gap)
            is_active_slot = (i == len(self.player_name))
            
            # 슬롯 배경 박스
            slot_rect = pygame.Rect(cur_box_x, box_y, box_w, box_h)
            slot_bg = (25, 35, 60) if is_active_slot else (15, 20, 35)
            pygame.draw.rect(self.screen, slot_bg, slot_rect, border_radius=6)
            
            slot_border_color = (255, 220, 80) if is_active_slot else (70, 100, 150)
            pygame.draw.rect(self.screen, slot_border_color, slot_rect, 2, border_radius=6)
            
            # 글자 렌더링
            if i < len(self.player_name):
                char = self.player_name[i]
                char_surf = self.font_entry.render(char, True, constants.COLOR_WHITE)
                self.screen.blit(char_surf, (cur_box_x + (box_w - char_surf.get_width()) // 2, box_y + 16))
            elif is_active_slot and blink:
                # 활성 슬롯 깜빡이는 언더바 커서
                cursor_surf = self.font_entry.render("_", True, (255, 220, 80))
                self.screen.blit(cursor_surf, (cur_box_x + (box_w - cursor_surf.get_width()) // 2, box_y + 20))
                
        # 5. 조작 안내
        btn_guide1 = self.font_main.render("[ ENTER ] 키를 눌러 랭킹 등록", True, constants.COLOR_PLAYER)
        btn_guide2 = self.font_sub.render("[ BACKSPACE ]: 한 글자 지우기", True, (160, 170, 190))
        self.screen.blit(btn_guide1, (cx - btn_guide1.get_width() // 2, 480))
        self.screen.blit(btn_guide2, (cx - btn_guide2.get_width() // 2, 520))

    def _draw_leaderboard_table(self, start_y: int):
        """
        영구 저장된 TOP 5 랭킹 테이블을 렌더링합니다.
        """
        cx = constants.SCREEN_WIDTH // 2
        
        # 랭킹 헤더
        header_surf = self.font_rank.render("RANK     NAME       SCORE", True, constants.COLOR_HUD)
        self.screen.blit(header_surf, (cx - header_surf.get_width() // 2, start_y))
        
        # 구분선
        line_y = start_y + 24
        pygame.draw.line(self.screen, (70, 100, 150), (cx - 180, line_y), (cx + 180, line_y), 1)
        
        # 랭킹 엔트리
        row_y = line_y + 10
        rank_colors = [
            (255, 215, 0),   # 1위: Gold
            (200, 200, 220), # 2위: Silver
            (205, 127, 50),  # 3위: Bronze
            (100, 220, 255), # 4위: Cyan
            (100, 220, 255)  # 5위: Cyan
        ]
        
        for idx, entry in enumerate(self.rankings):
            rank_num = idx + 1
            color = rank_colors[idx] if idx < len(rank_colors) else constants.COLOR_WHITE
            
            # 플레이어가 새로 달성한 순위는 강조 하이라이트
            is_new_record = (rank_num == self.latest_rank)
            
            name = entry.get("name", "---").ljust(4)
            score = entry.get("score", 0)
            
            entry_str = f" {rank_num}위     {name:4s}    {score:6,d} P"
            entry_surf = self.font_rank.render(entry_str, True, (255, 255, 100) if is_new_record else color)
            
            if is_new_record:
                # 배경 하이라이트 박스
                hl_rect = pygame.Rect(cx - 185, row_y - 2, 370, 24)
                pygame.draw.rect(self.screen, (60, 50, 20), hl_rect, border_radius=4)
                pygame.draw.rect(self.screen, (255, 215, 0), hl_rect, 1, border_radius=4)
                
            self.screen.blit(entry_surf, (cx - entry_surf.get_width() // 2, row_y))
            row_y += 28

    def _draw_game_over_screen(self):
        """
        패배 화면: 게임오버 문구 및 영구 보존 랭킹 보드
        """
        cx = constants.SCREEN_WIDTH // 2
        
        # 메인 타이틀
        title_surf = self.font_title.render("GAME OVER", True, constants.COLOR_ENEMY_1)
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 130))
        
        # 점수 및 달성 랭킹
        score_text = f"내 점수: {self.score:,}점"
        if self.latest_rank > 0:
            score_text += f"  (랭킹 {self.latest_rank}위 등록!)"
        score_surf = self.font_main.render(score_text, True, constants.COLOR_WHITE)
        self.screen.blit(score_surf, (cx - score_surf.get_width() // 2, 185))
        
        # 반투명 랭킹 보드 패널
        panel_rect = pygame.Rect(cx - 230, 230, 460, 230)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((10, 15, 30, 210))
        pygame.draw.rect(panel_surface, (70, 110, 180), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # 랭킹 보드 표 렌더링
        self._draw_leaderboard_table(245)
        
        # 재시작 & 종료 안내
        restart_surf = self.font_main.render("[ R ] 키를 눌러 다시 도전", True, constants.COLOR_ENEMY_3)
        quit_surf = self.font_sub.render("[ ESC ] 키: 게임 종료", True, (160, 160, 180))
        
        self.screen.blit(restart_surf, (cx - restart_surf.get_width() // 2, 490))
        self.screen.blit(quit_surf, (cx - quit_surf.get_width() // 2, 535))

    def _draw_victory_screen(self):
        """
        승리 화면: 축하 문구 및 영구 보존 랭킹 보드
        """
        cx = constants.SCREEN_WIDTH // 2
        
        # 메인 타이틀
        title_surf = self.font_title.render("★ MISSION COMPLETE ★", True, constants.COLOR_ENEMY_3)
        msg_surf = self.font_main.render("지구를 위협하던 외계인 군단을 섬멸했습니다!", True, constants.COLOR_PLAYER)
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 115))
        self.screen.blit(msg_surf, (cx - msg_surf.get_width() // 2, 165))
        
        # 점수 및 달성 랭킹
        score_text = f"내 점수: {self.score:,}점"
        if self.latest_rank > 0:
            score_text += f"  (랭킹 {self.latest_rank}위 등극!)"
        score_surf = self.font_main.render(score_text, True, constants.COLOR_WHITE)
        self.screen.blit(score_surf, (cx - score_surf.get_width() // 2, 205))
        
        # 반투명 랭킹 보드 패널
        panel_rect = pygame.Rect(cx - 230, 245, 460, 230)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((10, 15, 30, 210))
        pygame.draw.rect(panel_surface, (255, 215, 0), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # 랭킹 보드 표 렌더링
        self._draw_leaderboard_table(260)
        
        # 재시작 & 종료 안내
        restart_surf = self.font_main.render("[ R ] 키를 눌러 다시 플레이", True, constants.COLOR_HUD)
        quit_surf = self.font_sub.render("[ ESC ] 키: 게임 종료", True, (160, 160, 180))
        
        self.screen.blit(restart_surf, (cx - restart_surf.get_width() // 2, 500))
        self.screen.blit(quit_surf, (cx - quit_surf.get_width() // 2, 545))

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
