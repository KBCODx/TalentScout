from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "talentscout-backend"}

def test_interview_flow():
    session_id = "test-session-123"
    
    # 1. Initial Request
    candidate_data = {
        "member": {
            "id": "CAND-001",
            "name": "Sarah Johnson",
            "jobRole": "Senior Data Engineer",
            "yearsExperience": 9,
            "education": "MS Computer Science",
            "status": "COMPLETED"
        },
        "missions": [],
        "signals": {
            "commitDays": 28,
            "missionsCompleted": 30,
            "missionsFirstTry": 20
        }
    }
    
    response = client.post("/api/interview", json={
        "sessionId": session_id,
        "candidate": candidate_data
    })
    assert response.status_code == 200
    assert response.json()["reply"] == "Welcome. Let's begin your interview."
    assert response.json()["done"] is False
    
    # 2. First Turn
    response = client.post("/api/interview", json={
        "sessionId": session_id,
        "message": "I'm ready to start."
    })
    assert response.status_code == 200
    assert "Python" in response.json()["reply"]
    assert response.json()["done"] is False
    
    # 3. Second Turn
    response = client.post("/api/interview", json={
        "sessionId": session_id,
        "message": "I have 5 years of Python experience."
    })
    assert response.status_code == 200
    assert "FastAPI" in response.json()["reply"]
    assert response.json()["done"] is False
    
    # 4. Final Turn
    response = client.post("/api/interview", json={
        "sessionId": session_id,
        "message": "I use async and await."
    })
    assert response.status_code == 200
    assert response.json()["reply"] == "Interview completed."
    assert response.json()["done"] is True
    assert "feedback" in response.json()
    assert "summary" in response.json()["feedback"]

def test_invalid_session():
    response = client.post("/api/interview", json={
        "sessionId": "invalid-session",
        "message": "Hello"
    })
    assert response.status_code == 400
    assert "Session not found" in response.json()["detail"]
