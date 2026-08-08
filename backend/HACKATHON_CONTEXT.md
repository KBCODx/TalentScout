# TalentScout AI Interview Agent - Hackathon Context & Spec Reference

This document serves as the sole technical source of truth and implementation guide for the TalentScout AI Interview Agent backend development. It has been compiled directly from the official hackathon specification files (`data/technical-spec.md`, `data/curriculum.json`, `data/candidates.json`).

---

## 1. HACKATHON REQUIREMENTS

### Core API Contract
*   **Single Required HTTP Endpoint:** `POST /api/interview`
*   **Authentication:** None required.
*   **State Management:** The backend must maintain the conversation state using a provided `sessionId` across multiple requests.

### Request & Response Formats

#### A. Session Initialization (First Request)
*   **Request JSON:**
    ```json
    {
      "sessionId": "string (e.g., abc-123)",
      "candidate": {
        "member": {
          "id": "string",
          "name": "string",
          "jobRole": "string",
          "yearsExperience": number,
          "education": "string",
          "status": "string"
        },
        "missions": [
          { "day": number, "title": "string", "passed": boolean, "attempts": number, "skipped": true }
        ],
        "signals": {
          "commitDays": number,
          "missionsCompleted": number,
          "missionsFirstTry": number
        }
      }
    }
    ```
*   **Expected Response JSON:**
    ```json
    {
      "reply": "Welcome. Let's begin your interview.",
      "done": false
    }
    ```

#### B. Conversation Turn (Subsequent Requests)
*   **Request JSON:**
    ```json
    {
      "sessionId": "string (e.g., abc-123)",
      "message": "string (candidate's response)"
    }
    ```
*   **Expected Response JSON:**
    ```json
    {
      "reply": "string (interviewer's next question or response)",
      "done": false
    }
    ```

#### C. Interview Completion (Final Response)
*   **Response JSON:**
    ```json
    {
      "reply": "Interview completed.",
      "done": true,
      "feedback": {
        "summary": "string (comprehensive text assessment)",
        "strengths": ["string", "string", ...],
        "gaps": ["string", "string", ...],
        "next": ["string", "string", ...]
      }
    }
    ```

### Behavioral Requirements
*   **Conversational Continuity:** The conversation must remain fluid and contextual across multiple API requests using the `sessionId`.
*   **Personalization:** The interviewer must tailor the interview flow and questions to the specific candidate's learning history and professional background.
*   **Automated Evaluation:** Once the interview finishes, the agent must generate a final response containing structured feedback including strengths, knowledge gaps, and clear action items.

---

## 2. TECHNICAL SPECIFICATION

### Required Fields Specification
*   **Requests:**
    *   `sessionId`: Identifies the conversation thread.
    *   `candidate`: Provided *only* on initialization to feed candidate background into the session state.
    *   `message`: Provided on subsequent conversation turns.
*   **Responses:**
    *   `reply`: Monologue or question from the AI interviewer.
    *   `done`: Boolean flag indicating if the interview is complete.
    *   `feedback`: Mandatory *only* when `done` is `true`. Contains the exact sub-fields:
        *   `summary`: Cohesive assessment narrative.
        *   `strengths`: Actionable array of specific technical areas where the candidate demonstrated high proficiency or historical excellence.
        *   `gaps`: Actionable array of areas where the candidate struggled, had high historical attempts, skipped, or showed difficulty during the interview.
        *   `next`: Recommended next steps mapped directly to curriculum topics/tools to help bridge identified gaps.

### Interview Completion Logic
*   **Stateful Control:** The backend must manage a conversation turn counter or evaluation checklist.
*   **Length Control:** The interview should dynamically progress through introductory, core questioning (targeting 3-5 technical topics with follow-ups), and a polite wrap-up phase before outputting `done: true`.

---

## 3. CANDIDATE DATA STRUCTURE (`data/candidates.json`)

The candidate records contain detailed background and performance signals.

### Fields Reference
1.  **`member` (Metadata Object):**
    *   `id`: String (e.g., `"CAND-001"`) - Unique identifier.
    *   `name`: String (e.g., `"Sarah Johnson"`) - Candidate's name.
    *   `jobRole`: String (e.g., `"Senior Data Engineer"`) - Candidate's professional title. Helps set the seniority/technical context.
    *   `yearsExperience`: Number (e.g., `9`) - Years in industry. Used to scale question complexity.
    *   `education`: String (e.g., `"MS Computer Science"`) - Educational credentials.
    *   `status`: String (e.g., `"COMPLETED"`) - Program completion status.
2.  **`missions` (Learning History Array):**
    *   An array of modules/days from the curriculum that the candidate attempted:
        *   `day`: Number (e.g., `7`) - Day of curriculum.
        *   `title`: String (e.g., `"Embeddings Explained"`) - Matches the curriculum day name.
        *   `passed`: Boolean (optional) - `true` if passed, `false` if failed.
        *   `attempts`: Number (optional) - Number of attempts made on this task. A high attempt count (e.g., `4` or `5`) indicates a topic that challenged the candidate.
        *   `skipped`: Boolean (optional) - `true` if the candidate opted to skip this topic entirely.
3.  **`signals` (Aggregated Performance Metrics):**
    *   `commitDays`: Number - Activity consistency score.
    *   `missionsCompleted`: Number - Total passed missions.
    *   `missionsFirstTry`: Number - Number of missions passed on attempt 1. Higher ratio represents strong speed of comprehension.

---

## 4. CURRICULUM DATA STRUCTURE (`data/curriculum.json`)

The curriculum comprises a 31-day AI systems development program divided into 8 core modules.

### Structural Schema
*   **`cohort`:** High-level description (e.g., `"AI Cohort · 31 days · 8 modules"`).
*   **`modules` (Array):**
    *   Divided into 8 blocks (n: 1 to 8), with titles and day-ranges (e.g., Module 3: `"Embeddings & Vector Search"`, days `[7, 10]`).
*   **`days` (Array of daily items):**
    *   `day`: Number (1 to 31) - Matches the day identifier in candidate missions.
    *   `title`: String - Dynamic topic name (e.g., `"Retrieval & Matching Engine"`).
    *   `type`: String - Format of the day (e.g., `"SETUP"`, `"BUILD"`, `"AI_CORE"`, `"SHIP_IT"`, `"LEARN"`, `"OPTIMIZE"`, `"CAPSTONE"`).
    *   `tools`: Array of strings - Exact frameworks, languages, or services used (e.g., `["Pandas", "SQLite", "SQL", "SQLAlchemy"]`).
    *   `objectives`: Array of strings - Specific learning outcomes achieved. Perfect for pulling technical questions or checking concrete knowledge.

---

## 5. PERSONALIZATION OPPORTUNITIES (Candidate Signals)

The backend can utilize specific signals from the candidate object to customize the interview:

1.  **Seniority & Complexity Adaptability (`yearsExperience` + `jobRole` + `education`):**
    *   *High-Exp (e.g., 9+ yrs):* Ask architectural questions. Focus on scalability, security, cost optimization, and deployment strategy.
    *   *Low-Exp / Entry (e.g., 0-1 yrs):* Ask structured, conceptual, and code-comprehension questions. Offer supportive validation.
    *   *Cross-Domain (e.g., DevOps, Business Analyst, UX, Marketing):* Focus on how AI tools integrate with their main skillset (e.g., deploying models for DevOps, usability for UX, or business rules for Business Analysts).
2.  **Weakness/Gap Probing (`attempts > 1` or `passed: false` or `skipped: true`):**
    *   Identify topics where the candidate struggled historically (e.g., took 4+ attempts) or skipped entirely.
    *   Ask constructive, supportive questions to see if they have since consolidated their understanding (e.g., *"I noticed you worked on Prompt Engineering on Day 12. What was the most challenging aspect of prompt versioning for you?"*).
3.  **Strength Validation (`attempts: 1` or `"passed": true`):**
    *   Congratulate/validate topics completed effortlessly. Ask advanced questions on those specific days to test deep technical limits.
4.  **Activity Profile (`commitDays` vs `missionsCompleted`):**
    *   Tailor the pacing of questions. Highly active candidates can be asked complex, open-ended scenarios, while less active profiles can be given clearer, more structured prompts.

---

## 6. INTERVIEW DESIGN CONSTRAINTS

To guarantee a compliant and flawless hackathon implementation, the future system must satisfy:
*   **No Hallucinated Context:** Ensure that questions asked are strictly grounded in tools and objectives defined in `curriculum.json` for days the candidate actually has in their profile.
*   **Strict Session Isolation:** Maintain dynamic conversation states in memory or in a lightweight cache mapped specifically to `sessionId` so multiple concurrent evaluations never cross context.
*   **Guaranteed Termination:** The interview must never get stuck in infinite question loops. A deterministic state machine or conversation length manager must transition to the feedback generation state.
*   **Dynamic Follow-ups:** The next response cannot be a canned question. It must directly reference and evaluate the candidate's last message (e.g., analyzing their trade-offs or agreeing with their architectural choices).

---

## 7. POTENTIAL DIFFERENTIATORS (Winning Enhancements)

To build a memorable, premium hackathon entry, we should include these additions:

1.  **Polished Debug/Judge Panel (Visualization):**
    *   Expose internal AI "thought processes" on the frontend. Show the active "evaluation phase", "assessed score", "selected curriculum target", and the "reasoning for question selection" (e.g., *“Targeting Day 10 Retrieval because candidate took 4 attempts on it”*).
2.  **Genuine Difficulty Progression:**
    *   Scale question difficulty dynamically in real-time. If they answer a concept perfectly, level up to architectural implications. If they struggle, pivot to a helpful hint or simpler definition.
3.  **Explainable Question Selection (Hidden Chain of Thought):**
    *   For every response, let the AI state internally why it is asking this next question. This creates a highly coherent system.
4.  **Evidence-Based Evaluation:**
    *   In the final feedback, have the AI quote or cite actual examples from the interview conversation (e.g., *“Demonstrated strong understanding of local model deployment by explaining how they set up Ollama and loaded Qwen2.5-Coder on Day 2.”*).
5.  **Clean & Modern Frontend Aesthetics:**
    *   Create a modern, chat-centric design using clean layout spacing, responsive state indicators (e.g., “Interviewer is typing...”), and a gorgeous final feedback report complete with progress indicators.

---

## 8. RISKS

*   **Concurrency/Session Leaks:** If session dictionaries are stored globally without thread safety, concurrent users will see each other's chats. *Mitigation:* Use thread-safe state dicts or lightweight persistence indexed strictly by `sessionId`.
*   **Context Token Bloat:** Feeding the entire `curriculum.json` and `candidates.json` into every single LLM call is highly inefficient. *Mitigation:* Only load and inject the active candidate's data and only the curriculum entries related to their completed/attempted days.
*   **Infinite Conversational Loops:** The LLM failing to transition to the exit flow because it keeps asking "Do you have any questions?". *Mitigation:* Programmatically intercept the loop after a fixed question budget and force the LLM to write the final feedback summary.
*   **LLM Out-of-Bounds Questions:** Asking generic trivia or unrelated software engineering questions. *Mitigation:* Lock the system prompt to *only* test subjects documented within the objectives of the candidate's active curriculum days.

---

## 9. IMPLEMENTATION CHECKLIST

- [ ] **Endpoint Validation:** Exposes `POST /api/interview` with no authentication required.
- [ ] **Session Handling:** Correctly isolates, loads, and saves conversation states using `sessionId`.
- [ ] **Start Request Compliance:** Accepts `sessionId` and `candidate` JSON on first request, responds with `{"reply": "...", "done": false}`.
- [ ] **Ongoing Request Compliance:** Accepts subsequent messages with `sessionId` and `message` keys, responds with `{"reply": "...", "done": false}`.
- [ ] **Dynamic Questioning:** Questions asked directly map to active day titles, tools, and objectives in `curriculum.json` where candidate completed missions.
- [ ] **Candidate Personalization:** Paces/frames questions based on experience, job role, and targets historical attempts or skipped items.
- [ ] **Follow-up Capability:** Inspects the candidate's response and asks a context-aware follow-up instead of blindly shifting topics.
- [ ] **Termination Safeguard:** Deterministically stops the interview after a configured turn limit (e.g., 5-8 questions).
- [ ] **Final Response Compliance:** Responds with `{"reply": "Interview completed.", "done": true, "feedback": {...}}`.
- [ ] **Feedback Object Schema:** Formats feedback with exact keys: `summary` (string), `strengths` (array), `gaps` (array), and `next` (array).
- [ ] **Evidence-Grounding:** Mapped strengths, gaps, and next steps in the final feedback directly reflect things discussed or historical curriculum signals.
- [ ] **Performance & Cost Optimization:** Context windows are managed efficiently by loading only relevant candidate/curriculum days.
