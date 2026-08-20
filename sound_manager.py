"""
스타 인베이더 (Star Invader) - 사운드 관리자 모듈 (sound_manager.py)
효과음(SFX) 로드, 자동 합성 생성 및 재생을 담당합니다.
"""

import os
import math
import struct
import wave
import pygame
import constants

def create_retro_laser_sound(file_path: str):
    """
    외부 오디오 파일이 없을 때 표준 라이브러리(wave, struct, math)를 사용하여
    깔끔하고 청명한 레트로 8비트 아케이드 레이저 사운드(.wav)를 생성합니다.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    sample_rate = 44100
    duration = 0.14  # 140ms 지속 시간
    total_samples = int(sample_rate * duration)
    
    # 주파수: 1300Hz에서 250Hz로 급격히 하강하는 아케이드 피치 스윕
    start_freq = 1300.0
    end_freq = 250.0
    
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        progress = i / total_samples
        
        # 지수적 주파수 감소
        freq = start_freq * ((end_freq / start_freq) ** progress)
        
        # 위상 적분 계산 (누적 위상)
        phase = 2.0 * math.pi * (start_freq * ((end_freq / start_freq) ** (progress / 2)) * t)
        
        # 사각파 + 사인파 합성으로 풍부한 8비트 아케이드 톤 구현
        square_val = 1.0 if math.sin(phase) > 0 else -1.0
        sine_val = math.sin(phase)
        raw_val = 0.65 * square_val + 0.35 * sine_val
        
        # 선형 볼륨 디케이(감쇠) 엔벨로프
        envelope = (1.0 - progress) ** 1.3
        
        amplitude = 0.35 * 32767.0 * envelope
        sample_int = int(raw_val * amplitude)
        sample_int = max(-32768, min(32767, sample_int))
        samples.append(sample_int)
        
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(1)        # 모노
        wav_file.setsampwidth(2)        # 16비트
        wav_file.setframerate(sample_rate)
        
        raw_bytes = struct.pack(f'<{len(samples)}h', *samples)
        wav_file.writeframes(raw_bytes)


class SoundManager:
    """
    게임 내 사운드 효과(SFX)를 안전하게 관리하고 재생하는 클래스입니다.
    """
    _instance = None
    _initialized = False
    _shoot_sound = None

    @classmethod
    def init(cls):
        """
        사운드 믹서 초기화 및 오디오 파일 준비
        """
        if cls._initialized:
            return
            
        try:
            if not pygame.mixer.get_init():
                # 믹서 초기화 (낮은 레이턴시 버퍼 설정)
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                
            # 레이저 사운드 파일이 없으면 자동 생성
            if not os.path.exists(constants.SOUND_SHOOT):
                create_retro_laser_sound(constants.SOUND_SHOOT)
                
            if os.path.exists(constants.SOUND_SHOOT):
                cls._shoot_sound = pygame.mixer.Sound(constants.SOUND_SHOOT)
                cls._shoot_sound.set_volume(0.4) # 적절한 볼륨
                
            cls._initialized = True
        except Exception as e:
            print(f"[알림] 사운드 시스템 초기화 중 경고 (사운드 없이 계속 진행): {e}")
            cls._initialized = True

    @classmethod
    def play_shoot(cls):
        """
        플레이어 탄환 발사 시 비프 레이저 사운드 재생
        """
        if not cls._initialized:
            cls.init()
            
        if cls._shoot_sound:
            try:
                cls._shoot_sound.play()
            except Exception:
                pass
