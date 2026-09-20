# Architecture

## 1. Current Architecture
*   **Frontend**: Streamlit (single page with tabs).
*   **Backend**: Python scripts directly intertwined with UI.
*   **Database**: SQLite (SQLAlchemy) single file (`study_engine.db`) with Document, Chunk, Flashcard. No Course or User models.
*   **RAG**: In-memory BM25 (`rank_bm25`) + Google Gemini `text-embedding-004`. Reciprocal Rank Fusion. Chunks are generated on the fly or pulled from DB, embeddings rebuilt on reload.

## 2. Proposed Architecture

### Frontend Layer (UI)
*   Streamlit using a robust multi-view router via `st.session_state.current_page`.
*   Views: Home/Dashboard, Course Dashboard, Document Viewer, Tutor, Review Session, Exam Simulator.

### Application Service Layer
*   **Auth / Context**: Minimal User session tracking (default local user for now, designed to be multi-tenant).
*   **CourseManager**: Manages courses, enrollments.
*   **IngestionService**: Handles PDF/TXT, extracts layout, calls LLM for concept extraction, chunks, generates embeddings, stores to DB.
*   **RAGService**: Persistent vector search (using `pgvector` equivalent for SQLite like `sqlite-vss` or just storing embeddings as blobs/JSON and loading efficiently via NumPy/FAISS).
*   **TutorService**: Manages chat state, selects modes, queries RAG, outputs Socratic responses with citations.
*   **AssessmentService**: Generates questions, grades answers, updates mastery.
*   **SpacedRepetitionService**: Advanced SM-2 / FSRS, schedules reviews.
*   **RecommendationEngine**: Calculates Next-Best-Action based on due reviews, weak concepts, and study goals.

### Data Layer (Persistence)
*   SQLite (ready to migrate to PostgreSQL).
*   Alembic for migrations.
*   Local file storage for uploaded documents (or `st.session_state` cache fallback).

## 3. Data Model
*   **User**: id, name, created_at
*   **Course**: id, user_id, title, description, created_at
*   **Document**: id, course_id, filename, content_hash, status, created_at
*   **Chunk**: id, document_id, page, section, text, embedding (JSON)
*   **Concept**: id, course_id, label, definition
*   **Flashcard**: id, course_id, concept_id, front, back, sm2_state
*   **Mistake**: id, course_id, question, answer, misconception, timestamp
*   **ChatSession**: id, course_id, history (JSON)
