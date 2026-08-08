from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import InterviewRequest, InterviewResponse, Feedback
from app.services.session_service import session_manager

app = FastAPI(title="TalentScout AI Interview API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "talentscout-backend"}

@app.post("/api/interview", response_model=InterviewResponse)
async def handle_interview(request: InterviewRequest):
    session_id = request.sessionId
    
    # Case 1: Initial Request (contains candidate)
    if request.candidate:
        session_manager.create_session(session_id, request.candidate)
        return InterviewResponse(
            reply="Welcome. Let's begin your interview.",
            done=False
        )

    # Case 2: Conversation Turn (contains message)
    if request.message:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=400, detail="Session not found. Please start with candidate data.")
        
        turn = session["turn_count"]
        
        # Simple deterministic mock flow
        if turn == 0:
            reply = "To start, could you tell me about your experience with Python?"
            session_manager.update_session(session_id, request.message, reply)
            return InterviewResponse(reply=reply, done=False)
        
        elif turn == 1:
            reply = "Great. How do you handle asynchronous tasks in FastAPI?"
            session_manager.update_session(session_id, request.message, reply)
            return InterviewResponse(reply=reply, done=False)
        
        else:
            # End of mock interview
            session_manager.end_session(session_id)
            return InterviewResponse(
                reply="Interview completed.",
                done=True,
                feedback=Feedback(
                    summary="The candidate showed basic knowledge of Python and FastAPI.",
                    strengths=["Python basics", "FastAPI familiarity"],
                    gaps=["Advanced concurrency", "Distributed systems"],
                    next=["Review asyncio documentation", "Build a multi-service project"]
                )
            )

    raise HTTPException(status_code=400, detail="Invalid request. Provide either candidate or message.")
