import json
import os
from typing import Dict, Any, List, Optional

class CandidateIntelligenceService:
    def __init__(self, candidates_path: str, curriculum_path: str):
        self.candidates_path = candidates_path
        self.curriculum_path = curriculum_path
        self._candidates_data = self._load_json(candidates_path).get("candidates", [])
        self._curriculum_data = self._load_json(curriculum_path)
        self._days_map = {day["day"]: day for day in self._curriculum_data.get("days", [])}

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def get_candidate_by_id(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        for candidate in self._candidates_data:
            if candidate["member"]["id"] == candidate_id:
                return candidate
        return None

    def build_interview_profile(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        candidate = self.get_candidate_by_id(candidate_id)
        if not candidate:
            return None

        missions = candidate.get("missions", [])
        passed_missions = [m for m in missions if m.get("passed") is True]
        failed_missions = [m for m in missions if m.get("passed") is False]
        skipped_missions = [m for m in missions if m.get("skipped") is True]

        # Derive signals
        signals = {
            "probe_deeper": [m["title"] for m in missions if m.get("attempts", 0) >= 3],
            "investigate_carefully": [m["title"] for m in missions if m.get("passed") is False or m.get("skipped") is True],
            "strengths": [m["title"] for m in missions if m.get("attempts") == 1 and m.get("passed") is True]
        }

        # Enrich missions with curriculum details
        enriched_missions = []
        for m in missions:
            day_num = m.get("day")
            curriculum_day = self._days_map.get(day_num, {})
            enriched_missions.append({
                "mission": m,
                "curriculum_details": curriculum_day
            })

        profile = {
            "metadata": candidate.get("member"),
            "learning_history": {
                "passed": passed_missions,
                "failed": failed_missions,
                "skipped": skipped_missions,
                "enriched_missions": enriched_missions
            },
            "signals": signals,
            "performance_metrics": candidate.get("signals")
        }

        return profile

# Singleton instance with default paths
# Assuming we run from project root or backend dir
# We'll use absolute paths or relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
candidates_file = os.path.join(BASE_DIR, "data", "candidates.json")
curriculum_file = os.path.join(BASE_DIR, "data", "curriculum.json")

intelligence_service = CandidateIntelligenceService(candidates_file, curriculum_file)
