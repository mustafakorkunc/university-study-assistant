# AI System Design

## 1. Trust Model
*   The AI is a helpful reasoning engine, but the **student's uploaded material is the absolute source of truth**.
*   The AI must distinguish between explicit facts in the text and its own inferences.
*   The AI must admit "I do not have enough evidence" when appropriate.

## 2. Prompt Engineering Architecture
Prompts will be decoupled from the UI logic. We will use a `prompts/` directory or centralized configuration.

**Key Prompt Types**:
*   `TUTOR_SOCRATIC_PROMPT`: Directs the AI to ask leading questions and withhold the final answer.
*   `TUTOR_EXPLAIN_PROMPT`: Directs the AI to explain concepts simply.
*   `CONCEPT_EXTRACTION_PROMPT`: Instructs the AI to return structured JSON (Definitions, Theorems, Relationships) from a chunk.
*   `EVALUATOR_PROMPT`: Uses Bloom's taxonomy to evaluate free-text responses and identify misconceptions.

## 3. RAG 2.0 Pipeline
1.  **Chunking**: Semantic/structural chunking (detect headers, paragraphs).
2.  **Embeddings**: Gemini `text-embedding-004`. Stored efficiently (e.g. NumPy array serialized to DB, loaded into FAISS/memory on app start).
3.  **Retrieval**: BM25 (keyword) + Vector (semantic) -> Reciprocal Rank Fusion (RRF).
4.  **Relevance Threshold**: Discard chunks with extremely low similarity scores.
5.  **Assembly**: Context injected as `[Doc: X, Pg: Y, Section: Z] Text...`

## 4. Structured Output Validation
*   Use `response_mime_type="application/json"` and ideally Pydantic schemas if using modern GenAI SDK features, or manual JSON parsing with retries.
*   Handle `JSONDecodeError` cleanly with fallback logic.
