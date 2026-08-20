"""
스타 인베이더 (Star Invader) - 리소스 로더 모듈 (resource_loader.py)
이미지 에셋 로드, 스마트 배경 투명화(흰색/검은색 배경 자동 감지 및 알파 투명화),
스프라이트 시트 분할 및 캐싱을 총괄합니다.
"""

from typing import Dict, List, Optional, Tuple
import os
import pygame
import constants

# 캐시 딕셔너리
_IMAGE_CACHE: Dict[Tuple[str, Optional[Tuple[int, int]], bool], pygame.Surface] = {}

def remove_background(surface: pygame.Surface) -> pygame.Surface:
    """
    이미지의 모서리 색상을 감지하여 흰색 배경이나 어두운 검은색 배경을 완전히 투명하게 만듭니다.
    """
    surf = surface.convert_alpha()
    w, h = surf.get_size()

    # 모서리 샘플링으로 흰색 배경 여부 확인
    sample_points = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2)]
    white_score = 0
    
    for sx, sy in sample_points:
        color = surf.get_at((sx, sy))
        if color.r > 200 and color.g > 200 and color.b > 200:
            white_score += 1

    is_white_bg = white_score >= 2
    transparent_color = pygame.Color(0, 0, 0, 0)

    # 픽셀별 배경 투명화 처리 (크기가 작아 즉각 처리됨)
    for x in range(w):
        for y in range(h):
            c = surf.get_at((x, y))
            if is_white_bg:
                # 흰색/밝은 배경 제거
                if (c.r > 210 and c.g > 210 and c.b > 210) or ((c.r + c.g + c.b) // 3 > 220):
                    surf.set_at((x, y), transparent_color)
            else:
                # 어두운/검은색 배경 제거
                if (c.r < 28 and c.g < 28 and c.b < 28) or ((c.r + c.g + c.b) // 3 < 25):
                    surf.set_at((x, y), transparent_color)

    return surf


def load_image(
    path: str,
    target_size: Optional[Tuple[int, int]] = None,
    transparent_bg: bool = True
) -> pygame.Surface:
    """
    이미지 파일을 로드하고 배경을 투명하게 만든 후 지정된 크기로 조절합니다.
    :param path: 이미지 파일 경로
    :param target_size: (가로, 세로) 튜플 (None이면 원본 크기 유지)
    :param transparent_bg: True면 흰색/검은색 배경을 완전 투명화 처리
    :return: 가공된 pygame.Surface 객체
    """
    cache_key = (path, target_size, transparent_bg)
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key].copy()

    # 파일 존재 여부 확인
    if not os.path.exists(path):
        print(f"[경고] 이미지 파일을 찾을 수 없습니다: {path}")
        w, h = target_size if target_size else (32, 32)
        fallback_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        fallback_surface.fill((255, 0, 255))
        return fallback_surface

    try:
        raw_surface = pygame.image.load(path)
        
        # 크기 조절을 먼저 수행하여 픽셀 처리 속도 극대화
        if target_size is not None:
            scaled_surface = pygame.transform.scale(raw_surface, target_size)
        else:
            scaled_surface = raw_surface

        # 배경 투명화 처리
        if transparent_bg:
            final_surface = remove_background(scaled_surface)
        else:
            final_surface = scaled_surface.convert()
            
        _IMAGE_CACHE[cache_key] = final_surface
        return final_surface.copy()

    except Exception as e:
        print(f"[에러] 이미지 로드 중 오류 발생 ({path}): {e}")
        w, h = target_size if target_size else (32, 32)
        fallback_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        fallback_surface.fill((255, 0, 255))
        return fallback_surface


def load_sprite_sheet(
    path: str,
    frame_count: int,
    target_size: Optional[Tuple[int, int]] = None,
    transparent_bg: bool = True
) -> List[pygame.Surface]:
    """
    가로로 나열된 스프라이트 시트 이미지를 분할하고 투명화 처리하여 반환합니다.
    """
    if not os.path.exists(path):
        print(f"[경고] 스프라이트 시트 파일을 찾을 수 없습니다: {path}")
        w, h = target_size if target_size else (48, 48)
        return [pygame.Surface((w, h), pygame.SRCALPHA) for _ in range(frame_count)]

    try:
        sheet = pygame.image.load(path)
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // frame_count
        
        frames: List[pygame.Surface] = []
        for i in range(frame_count):
            frame_rect = pygame.Rect(i * frame_width, 0, frame_width, sheet_height)
            frame_surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), frame_rect)

            if target_size is not None:
                frame_surface = pygame.transform.scale(frame_surface, target_size)

            if transparent_bg:
                frame_surface = remove_background(frame_surface)
                
            frames.append(frame_surface)

        return frames

    except Exception as e:
        print(f"[에러] 스프라이트 시트 분할 중 오류 발생 ({path}): {e}")
        w, h = target_size if target_size else (48, 48)
        return [pygame.Surface((w, h), pygame.SRCALPHA) for _ in range(frame_count)]


def get_bullet_image(is_enemy: bool = False) -> pygame.Surface:
    """
    탄환 이미지를 생성하거나 로드합니다. (알파 채널 지원)
    """
    w = constants.BULLET_WIDTH
    h = constants.BULLET_HEIGHT
    
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if is_enemy:
        # 적 탄환: 붉은색 플라즈마 에너지 빔
        color_core = (255, 255, 255)
        color_outer = (255, 60, 80)
        pygame.draw.ellipse(surf, color_outer, (0, 0, w, h))
        pygame.draw.ellipse(surf, color_core, (w // 4, 2, w // 2, h - 4))
    else:
        # 플레이어 탄환: 시안/하늘색 발광 에너지 레이저
        color_core = (255, 255, 255)
        color_outer = (50, 220, 255)
        pygame.draw.rect(surf, color_outer, (0, 0, w, h), border_radius=3)
        pygame.draw.rect(surf, color_core, (1, 2, w - 2, h - 4), border_radius=2)
        
    return surf


def get_life_icon() -> pygame.Surface:
    """
    HUD에 표시할 미니 플레이어 기체 아이콘을 로드합니다. (배경 투명화)
    """
    return load_image(constants.IMAGE_PLAYER, (24, 20), transparent_bg=True)
