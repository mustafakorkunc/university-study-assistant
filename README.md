# Adaptive Learning Workspace

An academic-grade, adaptive personal learning system built with Python, Streamlit, and Google Gemini AI.

## Philosophy

The Adaptive Learning Workspace transforms your passive notes into an active learning engine. It stops treating AI as a "chatbot" and instead models your knowledge, predicts your forgetting curves, and recommends your next best study action.

## Core Features

- **Course Workspaces**: Isolate your learning materials by subject.
- **RAG 2.0 Ingestion**: Upload PDFs/TXTs, parse structurally, extract concepts, and chunk them semantically with local embeddings persistence.
- **Source-Grounded Socratic Tutor**: An AI tutor that refuses to give you the answer directly, instead asking guiding questions strictly grounded in your uploaded materials.
- **Active Recall Engine (SM-2)**: Create manual or AI-assisted flashcards with spaced repetition natively integrated.
- **Adaptive Diagnostic Exams**: Auto-generate Bloom's Taxonomy-aligned exams based on your weak concepts and receive rubric-based evaluation.
- **Mistake Journal**: A centralized log of your misconceptions allowing you to review your exact misunderstandings over time.
- **Next-Best-Action**: A dashboard that tells you exactly what to do when you log in (e.g., "Review 5 due cards").

## Tech Stack

- **Frontend**: Streamlit
- **Backend / DB**: SQLite + SQLAlchemy (Ready for PostgreSQL migration)
- **AI Engine**: Google Gemini (`google-genai` SDK)
- **Retrieval**: BM25 + Gemini `text-embedding-004` (Hybrid Reciprocal Rank Fusion)

## Local Setup

```bash
# 1. Clone repository
git clone https://github.com/mustafakorkunc/university-study-assistant.git
cd university-study-assistant

# 2. Setup Virtual Environment
python -m venv venv
source venv/Scripts/activate # Windows
# source venv/bin/activate # Mac/Linux

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Setup Database
alembic upgrade head

# 5. Add API Key
# Copy .env.example to .env and add your GEMINI_API_KEY
# OR just enter it directly via the app's sidebar settings!

# 6. Run Application
streamlit run app.py
```

## Production Deployment (Streamlit Community Cloud)

1. Connect your GitHub repository to [share.streamlit.io](https://share.streamlit.io/).
2. Select `app.py` as the main entry point.
3. *Do not* add the `GEMINI_API_KEY` to secrets if you want to support multi-tenant usage (users will paste their own key in the sidebar).
4. Click Deploy.

## Testing

```bash
# Run unit tests
python -m pytest
```

## Security & Privacy

- Documents are ingested locally and stored in SQLite. 
- API keys are persisted temporarily in `st.session_state` and erased upon session timeout. No global caching of keys.
- LLM outputs are rigorously validated.

## Known Limitations

- SQLite is currently single-file. Heavy concurrent ingestion requires a PostgreSQL upgrade.
- Video and Audio ingestion are not currently supported.
