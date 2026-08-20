"""
스타 인베이더 (Star Invader) - 랭킹 관리자 모듈 (ranking_manager.py)
플레이어의 3글자 이니셜 및 점수를 영구 저장(JSON)하고 순위표를 관리합니다.
"""

from typing import List, Dict, Any
import os
import json
import constants

# 기본 랭킹 데이터 (초기 파일이 없을 때 사용)
DEFAULT_RANKINGS: List[Dict[str, Any]] = [
    {"name": "ACE", "score": 3000},
    {"name": "SKY", "score": 2400},
    {"name": "NEO", "score": 1800},
    {"name": "MAX", "score": 1200},
    {"name": "FOX", "score": 600}
]

class RankingManager:
    """
    JSON 파일을 통한 랭킹 보드 영구 저장 및 랭킹 조회 클래스
    """
    
    @staticmethod
    def load_rankings() -> List[Dict[str, Any]]:
        """
        저장된 랭킹 데이터를 로드합니다. 파일이 없거나 손상된 경우 기본값을 생성하여 저장합니다.
        """
        file_path = constants.RANKING_FILE
        if not os.path.exists(file_path):
            RankingManager.save_all_rankings(DEFAULT_RANKINGS)
            return list(DEFAULT_RANKINGS)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # 점수 기준 내림차순 정렬
                    sorted_data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
                    return sorted_data[:constants.MAX_RANKING_ENTRIES]
        except Exception as e:
            print(f"[경고] 랭킹 파일 로드 실패, 기본값 복구: {e}")

        # 복구 로직
        RankingManager.save_all_rankings(DEFAULT_RANKINGS)
        return list(DEFAULT_RANKINGS)

    @staticmethod
    def save_all_rankings(rankings: List[Dict[str, Any]]) -> bool:
        """
        랭킹 리스트 전체를 파일에 저장합니다.
        """
        file_path = constants.RANKING_FILE
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(rankings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[에러] 랭킹 파일 저장 실패 ({file_path}): {e}")
            return False

    @staticmethod
    def add_score(name: str, score: int) -> int:
        """
        새로운 점수를 랭킹에 추가하고 정렬 후 저장합니다.
        :param name: 플레이어 이니셜 (최대 3글자)
        :param score: 달성 점수
        :return: 새로 등록된 순위 (1위부터 시작, 순위 밖이면 -1)
        """
        rankings = RankingManager.load_rankings()
        
        cleaned_name = name.strip().upper()[:3]
        if not cleaned_name:
            cleaned_name = "AAA"
            
        new_entry = {"name": cleaned_name, "score": int(score)}
        rankings.append(new_entry)
        
        # 점수 기준 내림차순 정렬
        rankings.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # 등록된 위치 찾기
        rank = -1
        for idx, entry in enumerate(rankings):
            if entry is new_entry:
                rank = idx + 1
                break
                
        # 최대 등록 개수로 제한
        rankings = rankings[:constants.MAX_RANKING_ENTRIES]
        RankingManager.save_all_rankings(rankings)
        
        return rank if rank <= constants.MAX_RANKING_ENTRIES else -1
