import streamlit as st
import streamlit.components.v1 as components
from modules.db import Concept, Flashcard, MistakeLog
from modules.adaptive_learning import get_concept_state

import config
import tempfile
import os

def render(db, course_id):
    if not course_id:
        st.warning("NO ACTIVE CONTEXT. PLEASE SELECT A COURSE.")
        return
        
    st.header("⎔ CONCEPT KNOWLEDGE MAP")
    
    concepts = db.query(Concept).filter_by(course_id=course_id).all()
    flashcards = db.query(Flashcard).filter_by(course_id=course_id).all()
    mistakes = db.query(MistakeLog).filter_by(course_id=course_id).all()
    
    if not concepts:
        st.info("NO CONCEPTS EXTRACTED YET. UPLOAD DOCUMENTS FIRST.")
        return
        
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate pyvis graph dynamically
        from pyvis.network import Network
        net = Network(height="600px", width="100%", bgcolor=config.COLOR_BG, font_color=config.COLOR_TEXT)
        
        # Add nodes
        for c in concepts:
            state = get_concept_state(st.session_state.user_id, course_id, c.id, db)
            mastery = state["mastery_score"]
            
            if mastery >= 0.8:
                color = config.COLOR_PRIMARY # Green
            elif mastery >= 0.4:
                color = config.COLOR_WARNING # Yellow
            else:
                color = config.COLOR_DANGER # Red
                
            net.add_node(c.id, label=c.label, title=f"Mastery: {int(mastery*100)}%\nConfidence: {int(state['confidence_score']*100)}%", color=color)
            
        # Add edges
        from modules.db import ConceptEdge
        edges = db.query(ConceptEdge).join(Concept, ConceptEdge.source_concept_id == Concept.id).filter(Concept.course_id == course_id).all()
        
        for e in edges:
            net.add_edge(e.source_concept_id, e.target_concept_id, title=e.relationship_type, label=e.relationship_type, color=config.COLOR_BORDER)
        
        try:
            # Use write_html to be safe across pyvis versions
            tmp_path = os.path.join(tempfile.gettempdir(), "graph.html")
            net.write_html(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                html = f.read()
            import streamlit.components.v1 as components
            components.html(html, height=600, scrolling=True)
        except Exception as e:
            st.error(f"SYSTEM ERROR: Graph generation failed: {e}")
            
    with col2:
        st.subheader("Concept Details")
        selected_concept_name = st.selectbox("Select a Concept", options=[c.label for c in concepts])
        
        if selected_concept_name:
            c = next(c for c in concepts if c.label == selected_concept_name)
            state = get_concept_state(st.session_state.user_id, course_id, c.id, db)
            
            st.metric("Mastery Estimate", f"{int(state['mastery_score']*100)}%")
            st.metric("Forgetting Risk", f"{int(state['forgetting_risk']*100)}%")
            st.write("**Definition:**")
            st.info(c.definition)
            
            st.divider()
            st.write("**Actions:**")
            if st.button("Practice Concept", use_container_width=True):
                # We can route to Tutor or Exam focused on this concept
                st.session_state.current_page = "Tutor"
                st.session_state.tutor_prefill = f"Let's practice the concept of {c.label}. Ask me a question about it."
                st.rerun()
                
            if st.button("Generate Flashcards", use_container_width=True):
                if "current_api_key" not in st.session_state or not st.session_state.current_api_key:
                    st.error("API Key required.")
                else:
                    with st.spinner(f"Generating flashcards for {c.label}..."):
                        from modules.cognitive_evaluator import generate_flashcards_for_concept
                        cards = generate_flashcards_for_concept(course_id, c.id, 3, "Medium", "Recall", db, st.session_state.current_api_key)
                        
                        if not cards:
                            st.error("Could not generate flashcards.")
                        else:
                            added = 0
                            for card in cards:
                                # Deduplicate
                                existing = db.query(Flashcard).filter_by(course_id=course_id, front=card.front).first()
                                if not existing:
                                    new_fc = Flashcard(course_id=course_id, concept_id=c.id, front=card.front, back=card.back)
                                    db.add(new_fc)
                                    added += 1
                            db.commit()
                            st.success(f"Generated and saved {added} new flashcards!")
                
        st.divider()
        if st.button("Generate AI Edges", use_container_width=True):
            with st.spinner("AI is analyzing concepts..."):
                from modules.concept_graph import extract_concept_edges
                from modules.rag_engine import RetrievalService
                rs = RetrievalService(st.session_state.current_api_key)
                # Fetch a broad sample of context
                results = rs.retrieve("Core concepts", course_id, db, top_k=20)
                context = "\n".join([r["text"] for r in results])
                added = extract_concept_edges(course_id, context, db, st.session_state.current_api_key)
                st.success(f"Added {added} edges!")
                st.rerun()
