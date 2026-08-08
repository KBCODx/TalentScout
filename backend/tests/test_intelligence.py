import pytest
import os
from app.services.intelligence_service import CandidateIntelligenceService

# Get paths relative to this test file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATES_PATH = os.path.join(BASE_DIR, "data", "candidates.json")
CURRICULUM_PATH = os.path.join(BASE_DIR, "data", "curriculum.json")

@pytest.fixture
def intelligence_service():
    return CandidateIntelligenceService(CANDIDATES_PATH, CURRICULUM_PATH)

def test_load_candidates(intelligence_service):
    assert len(intelligence_service._candidates_data) > 0
    assert intelligence_service._candidates_data[0]["member"]["id"] == "CAND-001"

def test_load_curriculum(intelligence_service):
    assert len(intelligence_service._curriculum_data.get("days", [])) > 0
    assert 1 in intelligence_service._days_map

def test_get_candidate_by_id(intelligence_service):
    candidate = intelligence_service.get_candidate_by_id("CAND-001")
    assert candidate is not None
    assert candidate["member"]["name"] == "Sarah Johnson"

def test_get_invalid_candidate(intelligence_service):
    candidate = intelligence_service.get_candidate_by_id("INVALID-ID")
    assert candidate is None

def test_build_interview_profile(intelligence_service):
    profile = intelligence_service.build_interview_profile("CAND-001")
    assert profile is not None
    assert profile["metadata"]["id"] == "CAND-001"
    assert "signals" in profile
    assert "probe_deeper" in profile["signals"]
    assert "investigate_carefully" in profile["signals"]
    assert "strengths" in profile["signals"]

def test_mission_day_mapping(intelligence_service):
    profile = intelligence_service.build_interview_profile("CAND-001")
    enriched = profile["learning_history"]["enriched_missions"]
    # Day 7 is in Sarah's missions
    day_7_mission = next(m for m in enriched if m["mission"]["day"] == 7)
    assert day_7_mission["curriculum_details"]["title"] == "Embeddings Explained"
    assert "Sentence Transformers" in day_7_mission["curriculum_details"]["tools"]

def test_signals_logic(intelligence_service):
    # CAND-002: Alex Turner
    # Day 10: 4 attempts (probe_deeper)
    # Day 12: 5 attempts (probe_deeper)
    profile = intelligence_service.build_interview_profile("CAND-002")
    signals = profile["signals"]
    assert "Retrieval & Matching Engine" in signals["probe_deeper"]
    assert "Prompt Engineering Fundamentals" in signals["probe_deeper"]

    # CAND-010: Gerald Combs
    # Day 8: passed: false (investigate_carefully)
    profile = intelligence_service.build_interview_profile("CAND-010")
    assert "Vector Databases Overview" in profile["signals"]["investigate_carefully"]
