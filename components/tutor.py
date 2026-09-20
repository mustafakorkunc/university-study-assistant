import streamlit as st
from modules.db import ChatSession, Course
from modules.rag_engine import get_retrieval_service
import json
import config

def render(db, course_id, api_key):
    if not course_id:
        st.warning("NO ACTIVE CONTEXT. PLEASE SELECT A COURSE.")
        return
    if not api_key:
        st.error("API KEY MISSING. PLEASE CONFIGURE SYSTEM.")
        return
        
    course = db.query(Course).get(course_id)
    st.header("◎ NEURAL TUTOR")
    st.caption(f"CONTEXT: {course.title.upper()}")
    
    # Initialize RAG for this course
    if "retrieval_service" not in st.session_state or st.session_state.current_api_key != api_key:
        st.session_state.retrieval_service = get_retrieval_service(api_key=api_key)

    # Load ChatSession
    chat_session = db.query(ChatSession).filter_by(course_id=course_id).first()
    if not chat_session:
        chat_session = ChatSession(course_id=course_id, history_json="[]")
        db.add(chat_session)
        db.commit()
        
    history = json.loads(chat_session.history_json)
    
    # Pre-fill logic from knowledge graph
    if "tutor_prefill" in st.session_state and st.session_state.tutor_prefill:
        history.append({"role": "user", "content": st.session_state.tutor_prefill})
        st.session_state.tutor_prefill = None
        db.commit() # Save the prefill
        
    col_chat, col_side = st.columns([7, 3])
    
    with col_side:
        st.subheader("SYSTEM PARAMS")
        mode = st.selectbox("TUTOR MODE", ["SOCRATIC", "EXPLAIN", "CHALLENGE"])
        if st.button("PURGE MEMORY"):
            chat_session.history_json = "[]"
            db.commit()
            st.rerun()
            
        st.divider()
        st.subheader("STUDENT STATE")
        from modules.db import Concept
        from modules.adaptive_learning import get_concept_state
        concepts = db.query(Concept).filter_by(course_id=course_id).all()
        weak_c = []
        for c in concepts:
            s = get_concept_state(st.session_state.user_id, course_id, c.id, db)
            if s["mastery_score"] < 0.6:
                weak_c.append(c)
                
        if weak_c:
            st.write("`WEAKNESSES DETECTED:`")
            for c in weak_c[:5]:
                st.markdown(f"> `{c.label}`")
        else:
            st.write("`NO SIGNIFICANT WEAKNESSES.`")

    with col_chat:
        st.markdown("---")
        # Render History
        for msg in history:
            role = "STUDENT" if msg["role"] == "user" else "SYSTEM"
            with st.chat_message(msg["role"]):
                st.caption(f"{role}")
                st.markdown(msg["content"])
                if "sources" in msg and msg["sources"]:
                    with st.expander("VIEW SOURCE DATA"):
                        for s in msg["sources"]:
                            st.markdown(f"`{s.get('document_name')} (Pg {s.get('page')}) | {s.get('section')}`")
                            st.caption(s.get('text', '')[:200] + "...")
        st.markdown("---")
        
        # Input
        if prompt := st.chat_input("> type your reasoning... [↵]"):
            history.append({"role": "user", "content": prompt})
            st.rerun()
            
        # Process pending response
        if history and history[-1]["role"] == "user":
            prompt = history[-1]["content"]
            with st.chat_message("assistant"):
                st.caption("SYSTEM")
                with st.spinner("`RETRIEVING & REASONING...`"):
                    evidence = []
                    if st.session_state.retrieval_service:
                        evidence = st.session_state.retrieval_service.retrieve(prompt, course_id, db, top_k=3)
                    
                    from modules.grounding import evaluate_grounding
                    grounding_state, grounding_msg = evaluate_grounding(evidence)
                    
                    if grounding_state == "INSUFFICIENT_EVIDENCE":
                        st.markdown(grounding_msg)
                        history.append({"role": "assistant", "content": grounding_msg, "sources": []})
                        chat_session.history_json = json.dumps(history)
                        db.commit()
                        st.rerun()
                        
                    context_str = "\n".join([f"[{c.get('document_name', 'Doc')} p.{c.get('page', '?')}] {c['text']}" for c in evidence])
                    
                    profile_str = f"Student's weak concepts: {', '.join([c.label for c in weak_c]) if weak_c else 'None'}"
                    
                    system_instruction = f"""
                    You are an Elite Socratic AI Tutor.
                    Mode: {mode}.
                    
                    Student Learning Profile:
                    {profile_str}
                    
                    Rules:
                    1. Base your answer heavily on the Context Evidence.
                    2. SOCRATIC MODE: You MUST ask a leading question. DO NOT give the direct answer. Guide the student to realize the answer themselves. Use short, punchy, terminal-like language.
                    3. If you detect a misconception related to their weak concepts, address it carefully.
                    4. Explicitly cite sources at the end of your message in a list format, like "Sources: Algorithms.pdf (p.14)" based on the context evidence provided.
                    """
                    
                    from google import genai
                    from google.genai import types
                    
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        resp = client.models.generate_content(
                            model=config.LLM_MODEL,
                            contents=f"Context Evidence:\n{context_str}\n\nStudent: {prompt}",
                            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.4)
                        )
                        st.markdown(resp.text)
                        history.append({"role": "assistant", "content": resp.text, "sources": evidence})
                        
                        chat_session.history_json = json.dumps(history)
                        db.commit()
                        # Do not rerun automatically here so the user can read the response as it renders, 
                        # but next chat_input will trigger standard flow
                    except Exception as e:
                        st.error(f"SYSTEM ERROR: Failed to generate response: {e}")
                        history.pop() # Remove user msg to retry
