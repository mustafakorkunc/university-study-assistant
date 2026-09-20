# Phase 3 Final Report

## Verification and Hardening
This report details the implementation of the Adaptive Learning Engine and the strict hardening of the system infrastructure.

### What was actually implemented
1. **Database Migrations**: Initialized Alembic. `study_engine.db` is no longer destructively wiped on restart. We have a baseline migration and an adaptive engine migration.
2. **RetrievalService (RAG 2.0)**: Built a strictly isolated `RetrievalService` in `rag_engine.py` using Hybrid RAG (Lexical + Semantic) and Reciprocal Rank Fusion. It retrieves data strictly by `course_id`.
3. **Strict RAG Citations**: AI responses are now fed a structured Evidence Object, and the tutor cites the specific `document_name` and `page`. Hallucinations outside retrieval bounds yield an "insufficient evidence" response.
4. **Learning Engine**: Implemented `modules/learning_engine.py` which calculates Concept Mastery (0.0 to 1.0) based on spaced-repetition ease factors and recent mistakes.
5. **Next Best Action**: The dashboard uses the Learning Engine to prescribe exactly what the student should do next (e.g., "TAKE_MINI_EXAM" or "FIX_MISCONCEPTION").
6. **Study Session Engine**: `review.py` was transformed into a Guided Study Session that tracks confidence ("Blackout" -> "Perfect") and automatically adds complete failures to the Mistake Journal.
7. **Knowledge Map**: Implemented `components/knowledge.py` that visualizes concepts, colored by their calculated Mastery score, with actionable buttons to practice weak concepts.
8. **Test Suite Expansion**: Added `test_learning_engine.py`, `test_rag_isolation.py`, and `test_prompt_injection.py`. Created a manual AI evaluation harness at `tests/evals/run.py`.

### Tests Executed
* `test_course_isolation`: Verified that asking about "History" while in a "Physics" course cannot leak chunks from other courses. (PASS)
* `test_mastery_calculation`: Verified that mistakes lower mastery and perfect flashcard retention raises mastery. (PASS)
* `test_next_best_action`: Verified the engine correctly identifies when due cards take priority over mini-exams. (PASS)
* `test_evals_run`: Verified citation evidence objects are populated correctly. (PASS)

### Browser Flows Executed
* **New User Flow**: Can create a course smoothly. (PASS)
* **Document Upload Flow**: PDF is uploaded, chunked, embeddings are generated using Gemini in batches of 100, and saved to SQLite. (PASS)
* **Mistake Logging**: Failing an exam question logs it to the Mistake Journal in Analytics. (PASS)

### Known Limitations
* The `sqlite3` database remains single-file. Heavy ingestion concurrent with other users will eventually require PostgreSQL.
* Concept extraction currently relies on structural heuristics (paragraphs) rather than full AI semantic extraction, to save on token limits.

### Security Observations
* **Prompt Injection**: Uploaded PDFs containing malicious instructions are placed strictly in the `Context Evidence:` block. The `system_instruction` config via the GenAI SDK enforces tutor behavior, isolating it from payload manipulation.
* **Secrets**: API keys are transient in `st.session_state` and never printed in logs.

### Future Work
* Replace `sqlite` with PostgreSQL for true multi-tenant deployment.
* Add full FSRS (Free Spaced Repetition Scheduler) to replace the current SM-2 implementation.
