import streamlit as st
import streamlit.components.v1 as components
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from modules.db import get_session, Document, Chunk, Flashcard, update_sm2
from modules.rag_engine import extract_pdf, HybridRAG
from modules.concept_graph import extract_knowledge_graph, generate_pyvis_html
from modules.cognitive_evaluator import generate_exam_questions, evaluate_response
from modules.exporter import export_to_anki, export_markdown_summary

st.set_page_config(page_title="Academic Study Engine", page_icon="🧠", layout="wide")
st.title("🧠 Cognitive-Science Research & Study Engine")

# Initialize session state for RAG engine and DB
if "rag_engine" not in st.session_state:
    api_key = os.getenv("GEMINI_API_KEY")
    st.session_state.rag_engine = HybridRAG(api_key=api_key) if api_key else None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = []

db = get_session()

# Sidebar for API Key and DB reset
with st.sidebar:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY is missing from .env")
    else:
        st.success("API Key Loaded.")
    
    # Reload documents into RAG
    if st.button("Reload Index from DB"):
        chunks = db.query(Chunk).all()
        chunk_dicts = [{"content": c.content, "page_number": c.page_number, "section_heading": c.section_heading} for c in chunks]
        if st.session_state.rag_engine:
            st.session_state.rag_engine.ingest_chunks(chunk_dicts)
            st.success(f"Indexed {len(chunk_dicts)} chunks.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Knowledge Matrix", "🔬 Socratic Lab", "🔁 Active Recall (SM-2)", "📝 Diagnostic Exam", "📤 Export"])

# --- TAB 1: KNOWLEDGE MATRIX ---
with tab1:
    st.header("Document Ingestion & Semantic Graph")
    uploaded_file = st.file_uploader("Upload Academic Paper / Notes (PDF)", type=["pdf"])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Process & Index Document"):
            if uploaded_file and api_key:
                with st.spinner("Extracting & Chunking..."):
                    extracted_chunks = extract_pdf(uploaded_file)
                    
                    doc = Document(filename=uploaded_file.name)
                    db.add(doc)
                    db.commit()
                    
                    for c in extracted_chunks:
                        db_chunk = Chunk(
                            document_id=doc.id,
                            page_number=c["page_number"],
                            section_heading=c["section_heading"],
                            content=c["content"]
                        )
                        db.add(db_chunk)
                    db.commit()
                    st.success(f"Processed {len(extracted_chunks)} chunks.")
                    
                    # Also reload RAG
                    all_chunks = db.query(Chunk).all()
                    chunk_dicts = [{"content": c.content, "page_number": c.page_number, "section_heading": c.section_heading} for c in all_chunks]
                    st.session_state.rag_engine.ingest_chunks(chunk_dicts)
                    
            elif not api_key:
                st.error("API Key required.")
                
    with col2:
        if st.button("Generate Concept Graph"):
            if api_key:
                with st.spinner("Analyzing relationships..."):
                    all_chunks = db.query(Chunk).all()
                    chunk_dicts = [{"content": c.content} for c in all_chunks]
                    graph_data = extract_knowledge_graph(chunk_dicts, api_key)
                    html = generate_pyvis_html(graph_data)
                    components.html(html, height=500, scrolling=True)

# --- TAB 2: SOCRATIC LAB ---
with tab2:
    st.header("Socratic Lab (Source-Grounded)")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg:
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        st.caption(f"Page {s['page_number']} | {s['section_heading']}")
                        st.text(s['content'][:200] + "...")
                        
    if prompt := st.chat_input("Ask a question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            if st.session_state.rag_engine:
                with st.spinner("Retrieving & Reasoning..."):
                    contexts = st.session_state.rag_engine.search(prompt, top_k=3)
                    context_text = "\n\n".join([f"[Pg {c['page_number']}, {c['section_heading']}] {c['content']}" for c in contexts])
                    
                    from google import genai
                    from google.genai import types
                    import config
                    
                    client = genai.Client(api_key=api_key)
                    sys_prompt = "You are an academic Socratic tutor. Use ONLY the provided context to guide the student. Use LaTeX formatting $$...$$ for math. Do not just give away the answer."
                    full_prompt = f"Context:\n{context_text}\n\nStudent: {prompt}"
                    
                    try:
                        resp = client.models.generate_content(
                            model=config.MODEL_NAME,
                            contents=full_prompt,
                            config=types.GenerateContentConfig(system_instruction=sys_prompt, temperature=0.4)
                        )
                        st.markdown(resp.text)
                        st.session_state.chat_history.append({"role": "assistant", "content": resp.text, "sources": contexts})
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("RAG Engine not initialized.")

# --- TAB 3: ACTIVE RECALL (SM-2) ---
with tab3:
    st.header("Active Recall & Spaced Repetition")
    
    with st.expander("Create New Flashcard"):
        fc_front = st.text_area("Question (Front)", help="Use $...$ for LaTeX math")
        fc_back = st.text_area("Answer (Back)")
        if st.button("Add Card"):
            card = Flashcard(front=fc_front, back=fc_back)
            db.add(card)
            db.commit()
            st.success("Card added!")
            
    st.divider()
    st.subheader("Due for Review")
    
    now = datetime.utcnow()
    due_cards = db.query(Flashcard).filter(Flashcard.next_review <= now).all()
    
    if not due_cards:
        st.info("No cards due for review right now. Great job!")
    else:
        card = due_cards[0]
        st.write(f"**Cards Due:** {len(due_cards)}")
        
        st.markdown("### Question:")
        if "$" in card.front:
            st.markdown(card.front) # Streamlit markdown supports inline math and block math with $$
        else:
            st.markdown(card.front)
            
        if "show_answer" not in st.session_state:
            st.session_state.show_answer = False
            
        if st.button("Show Answer"):
            st.session_state.show_answer = True
            
        if st.session_state.show_answer:
            st.markdown("### Answer:")
            st.markdown(card.back)
            
            st.markdown("**Grade your recall:**")
            cols = st.columns(6)
            for i in range(6):
                if cols[i].button(str(i)):
                    update_sm2(card, i)
                    db.commit()
                    st.session_state.show_answer = False
                    st.rerun()
            st.caption("0: Blackout | 1: Incorrect (remembered) | 2: Incorrect (easy) | 3: Hard | 4: Good | 5: Perfect")

# --- TAB 4: DIAGNOSTIC EXAM SIM ---
with tab4:
    st.header("Diagnostic Exam (Bloom's Taxonomy)")
    
    if st.button("Generate Exam"):
        if api_key:
            with st.spinner("Generating..."):
                all_chunks = db.query(Chunk).all()
                context = "\n".join([c.content for c in all_chunks[:20]]) # sample
                st.session_state.exam_questions = generate_exam_questions(context, api_key)
                
    if st.session_state.exam_questions:
        for i, eq in enumerate(st.session_state.exam_questions):
            st.subheader(f"Q{i+1}: {eq['question']}")
            st.caption(f"Bloom's Level: {eq.get('bloom_level', 'Unknown')}")
            
            ans = st.text_area("Your Answer", key=f"ans_{i}")
            if st.button("Submit Answer", key=f"sub_{i}"):
                with st.spinner("Evaluating..."):
                    all_chunks = db.query(Chunk).all()
                    context = "\n".join([c.content for c in all_chunks[:20]])
                    eval_res = evaluate_response(eq['question'], ans, context, api_key)
                    
                    if "error" in eval_res:
                        st.error(eval_res["error"])
                    else:
                        st.metric("Factual Accuracy", f"{eval_res.get('score', 0)}/100")
                        st.write(f"**Reasoning Quality:** {eval_res.get('reasoning_quality', '')}")
                        st.write(f"**Misconceptions:** {eval_res.get('misconceptions', '')}")
                        st.info(f"**Socratic Guidance:** {eval_res.get('socratic_guidance', '')}")
            st.divider()

# --- TAB 5: EXPORT ---
with tab5:
    st.header("Export Data")
    
    if st.button("Export Deck to Anki (.apkg)"):
        cards = db.query(Flashcard).all()
        if cards:
            path = export_to_anki(cards)
            with open(path, "rb") as file:
                st.download_button("Download Anki Deck", file, file_name="StudyEngine.apkg")
        else:
            st.warning("No flashcards found.")
            
    if st.button("Export Markdown Summary"):
        all_chunks = db.query(Chunk).all()
        context = "\n".join([c.content for c in all_chunks])
        path = export_markdown_summary(context)
        with open(path, "rb") as file:
            st.download_button("Download Summary", file, file_name="Summary.md")
