# Product Specification

## 1. Product Positioning
**Name**: Adaptive Learning Workspace (formerly University Study Assistant)
**Tagline**: "An adaptive learning system that builds a model of what you know."
**Core Philosophy**: Intelligence communicated through behavior. We do not use the term "AI" as a gimmick; the system is a tutor, a planner, and an examiner.

## 2. Core User Journey
1.  **Onboarding**: User is greeted, creates their first `Course` (e.g. "Biology 101").
2.  **Ingestion**: User uploads a Syllabus or Lecture Notes. System parses, extracts concepts, and displays progress.
3.  **Dashboard**: Shows "What should I do now?" (Next-Best-Action). E.g. "Review 5 concepts from Lecture 1."
4.  **Tutor Session**: User asks a question. Tutor responds Socratically, citing page numbers from the uploaded notes.
5.  **Review Session**: User engages in active recall via spaced-repetition flashcards. Mistakes are logged to the Mistake Journal.

## 3. Information Architecture (Views)
*   **Home Dashboard**: Global view of today's study goals, active courses, due reviews, and a prominent "Continue Studying" button.
*   **Course Overview**: Course-specific metrics, document list, concept map preview.
*   **Documents**: Upload, manage, and view processing status (Chunks, Concepts found).
*   **Tutor**: Chat interface specific to the course. Includes mode selector (Socratic, Hint, Simplify).
*   **Practice & Exams**: Adaptive question generation and evaluation.
*   **Review**: Distraction-free flashcard review session.

## 4. Key Features
*   **Next-Best-Action Engine**: The dashboard prioritizes actions based on algorithmic need (overdue cards > weak concepts > new material).
*   **Mistake Journal**: Automatically logs incorrect exam or tutor responses, mapping them to specific misconceptions.
*   **Source-Grounded Answers**: Every tutor response must have a traceable citation to a document chunk.
