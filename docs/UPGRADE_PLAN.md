# Upgrade Plan

## 1. Overview
Transform the University Study Assistant into an adaptive personal learning system (North Star). Move from 5 disjoint tabs to a coherent learning engine driven by a centralized Data Model and Next-Best-Action recommendation engine.

## 2. Phases

### PHASE 1: Foundation
*   **Audit**: Complete.
*   **Tests**: Add Pytest harness.
*   **Data Model**: Introduce SQLAlchemy models for User, Course, Document, Concept, Flashcard, Exam, StudySession, AnalyticsEvent.
*   **Architecture Cleanup**: Introduce service layers separating UI from DB logic and AI calls.
*   **Security & Error Handling**: Refactor error propagation and ensure secrets aren't exposed.

### PHASE 2: Core Learning Workspace
*   **Courses & Documents**: Users can create courses and upload documents bound to a specific course.
*   **Ingestion Pipeline**: Asynchronous or robust sequential pipeline (upload -> parse -> chunk -> embed -> index).
*   **Dashboard**: Implement the "Home Dashboard" displaying active courses, streaks, and recommendations.

### PHASE 3: RAG 2.0
*   **Retrieval**: Upgrade `rag_engine.py` to support course-aware filtering, multi-query retrieval, MMR, and citation grounding.
*   **Evaluation**: Build a local evaluation loop.

### PHASE 4: Tutor
*   **Modes**: Socratic, Explain, Hint, etc.
*   **Memory**: Track recent mistakes, student confidence, and unresolved misconceptions in DB.

### PHASE 5: Learning Engine
*   **Concept Mastery**: Model `ConceptMastery` per user/course.
*   **Adaptive Planner**: Drive "Next-Best-Action" (e.g. Review 8 cards, practice derivatives).

### PHASE 6: Review
*   **Flashcards**: Update SM-2, atomicity, auto-generation.
*   **Mistake Journal**: Record mistakes into a structured journal format.

### PHASE 7: Assessment
*   **Question Bank & Exams**: Adaptive exams driven by mastery levels.

### PHASE 8: Analytics
*   **Progress**: Build visualizations for retention, accuracy, mastery trend.

### PHASE 9: UX Polish
*   Responsive design, accessibility, microinteractions, state management.

### PHASE 10: Deployment
*   Persistent storage config (PostgreSQL readiness).
*   Monitoring and rate-limiting.

## 3. Migration Risks
*   **Data Migration**: Dropping existing schema vs Alembic. Given it's currently a prototype, we will initialize Alembic for future upgrades, and recreate the schema this once.
*   **State Management**: Streamlit's linear execution model makes complex routing (Dashboard -> Course -> Review) challenging. We will use `st.session_state` heavily for view routing.
