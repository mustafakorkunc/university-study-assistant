# QA & Testing Plan

## 1. Quality Gates
*   **Application Boot**: Streamlit must start without exceptions.
*   **Dependency Check**: Ensure `requirements.txt` is minimal, pinned, and conflict-free.
*   **Database Migrations**: Initial setup must correctly create all tables (User, Course, Document, etc.).

## 2. Testing Layers
*   **Unit Tests**: Use `pytest` for internal logic:
    *   `test_sm2.py`: Verify spaced repetition intervals.
    *   `test_chunking.py`: Verify structural chunker output.
    *   `test_rrf.py`: Verify fusion ranking math.
*   **Integration Tests**:
    *   Test End-to-End ingestion (dummy PDF -> DB -> Vector space).
    *   Test RAG retrieval (query -> top K chunks).
*   **Visual / Browser QA**:
    *   Upload state (Loading spinner, error states for malformed PDFs).
    *   Empty states (Dashboard with no courses, Tutor with no documents).
    *   Responsiveness on narrow widths (simulated mobile).

## 3. Security & Robustness
*   **Secret Handling**: App must NEVER print API keys in tracebacks or UI.
*   **API Limits**: Implement exponential backoff for `google-genai` rate limits (429 errors).
*   **Untrusted Input**: Treat PDF text as untrusted. AI must not execute instructions found inside the PDF (Prompt Injection defense).

## 4. Rollback Strategy
*   Use Git commits effectively. Each Phase is a feature branch or discrete commit.
*   If DB schema breaks, use Alembic downgrades (or recreate DB during early development).
