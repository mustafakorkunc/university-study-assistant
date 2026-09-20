import streamlit as st
from modules.db import Course, Flashcard, MistakeLog, Document, Chunk
import pandas as pd
from datetime import datetime
from modules.adaptive_learning import get_recurring_misconceptions

def render(db, course_id):
    if not course_id:
        st.warning("NO ACTIVE CONTEXT. PLEASE SELECT A COURSE.")
        return
        
    st.header("⌁ LEARNING ANALYTICS")
    st.caption("TELEMETRY AND INSIGHTS")
    
    col1, col2, col3 = st.columns(3)
    
    docs = db.query(Document).filter_by(course_id=course_id).count()
    chunks = db.query(Chunk).join(Document).filter(Document.course_id == course_id).count()
    cards = db.query(Flashcard).filter_by(course_id=course_id).count()
    
    col1.metric("Documents", docs)
    col2.metric("Knowledge Chunks", chunks)
    col3.metric("Flashcards", cards)
    
    st.divider()
    
    st.subheader("🧠 Mistake Intelligence")
    recurring = get_recurring_misconceptions(st.session_state.user_id, course_id, db)
    
    if recurring:
        st.warning(f"Detected {len(recurring)} active misconceptions!")
        for r in recurring:
            st.write(f"**{r['concept']}**: {r['category']} - {r['description']}")
    else:
        st.success("No recurring misconceptions detected. Great job!")
        
    st.divider()
    
    st.subheader("📝 Mistake Journal (Chronological)")
    mistakes = db.query(MistakeLog).filter_by(course_id=course_id).order_by(MistakeLog.created_at.desc()).limit(20).all()
    
    if not mistakes:
        st.info("You have no logged mistakes for this course. Keep up the good work!")
    else:
        for m in mistakes:
            with st.expander(f"{m.created_at.strftime('%Y-%m-%d')} - {m.question[:50]}..."):
                st.write("**Question:**")
                st.info(m.question)
                st.write("**Your Answer:**")
                st.error(m.student_answer)
                st.write("**Misconception/Correction:**")
                st.success(m.misconception)
                
                if st.button("Delete Log", key=f"del_m_{m.id}"):
                    db.delete(m)
                    db.commit()
                    st.rerun()
