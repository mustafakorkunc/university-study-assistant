# PHASE 4: LEARNING INTELLIGENCE REPORT

## Overview
Phase 4 focused on transitioning the University Study Assistant from a simple RAG demo into a robust, event-driven adaptive learning engine. All mastery, analytics, and next-best actions are now derived from a deterministic learning policy fed by immutable event logs.

## 1. Resolved Previous Gaps
- **Database Safety**: Removed the risky `Base.metadata.create_all(engine)` from `modules/db.py`. Streamlit Cloud initialization is now handled securely via a programmatic Alembic execution guard (`alembic.config.main()`).
- **File Validation**: Added strict 10MB limits and `.pdf` / `.txt` MIME validation to document ingestion.
- **Structured Outputs**: Deprecated blind JSON parsing in favor of strict Pydantic model validation (`ExamQuestionList`, `EvaluationResponse`) with built-in semantic checks for Bloom's Taxonomy.

## 2. Event-Driven Learning Model
- **New Entities**: Introduced `QuestionAttempt`, `Misconception`, and `FlashcardReviewEvent`.
- **Concept Edge Topology**: Added `ConceptEdge` to store graph relationships (e.g., `PREREQUISITE`, `RELATED_TO`).

## 3. Policy-Based Mastery & Next Best Action 2.0
- **`modules/learning_policy.py`**: Configurable weights for learning evidence (e.g., Perfect Flashcard = +1.0, Active Misconception = -2.0) generating a deterministic Mastery Score via sigmoid normalization. Ebbinghaus-inspired Forgetting Risk calculates the degradation of retention over time.
- **Next Best Action Engine**: Dynamically routes the user to `REVIEW_FLASHCARDS`, `FIX_MISCONCEPTION`, `TAKE_MINI_EXAM`, or `PRACTICE` based on real-time evidence.

## 4. Adaptive Assessment Loop
- **`components/exam.py`**: Transformed into an infinite, adaptive loop. Questions are generated dynamically by targeting the lowest mastery concept or recently triggered misconceptions.

## 5. Architectural Improvements
- **Grounding Gate**: `modules/grounding.py` intercepts RAG outputs, classifying relevance to prevent hallucinated citations (`GROUNDED`, `PARTIALLY_GROUNDED`, `INSUFFICIENT_EVIDENCE`).
- **Prompt Architecture**: Centralized prompt templates in the `prompts/` directory to decouple engineering from component logic.
- **Knowledge Map 2.0**: The graph visually distinguishes node mastery (Green/Yellow/Red) and dynamically renders AI-extracted relationships.

## 6. Verification
All core engine interactions are covered by local unit tests (`test_learning_loop.py`, `test_grounding_gate.py`, etc.), verifying that the state machine behaves deterministically when presented with passing or failing evidence.
