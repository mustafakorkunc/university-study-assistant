import streamlit as st
from modules.db import Course, Flashcard, Misconception, Concept, QuestionAttempt
from datetime import datetime
from modules.adaptive_learning import get_next_best_action, get_course_learning_state, get_concept_state

def render(db, user_id):
    st.header("SYSTEM STATUS // DASHBOARD")
    
    courses = db.query(Course).filter_by(user_id=user_id).all()
    if not courses:
        st.info("NO ACTIVE CONTEXT. INITIALIZE A NEW COURSE WORKSPACE.")
        with st.form("new_course"):
            new_c_name = st.text_input("COURSE TITLE")
            if st.form_submit_button("INITIALIZE"):
                if new_c_name:
                    course = Course(user_id=user_id, title=new_c_name)
                    db.add(course)
                    db.commit()
                    st.rerun()
        return

    selected_course_id = st.session_state.current_course_id
    if not selected_course_id:
        st.warning("SELECT AN ACTIVE CONTEXT FROM THE SIDEBAR.")
        return
        
    course = db.query(Course).get(selected_course_id)
    
    # Calculate some mock metrics or use real ones
    concepts = db.query(Concept).filter_by(course_id=selected_course_id).all()
    states = [get_concept_state(user_id, selected_course_id, c.id, db) for c in concepts]
    states.sort(key=lambda x: x["mastery_score"])
    
    avg_mastery = sum([s["mastery_score"] for s in states]) / len(states) if states else 0.0
    
    def render_progress_bar(pct, width=20):
        filled = int(pct * width)
        return "█" * filled + "░" * (width - filled)

    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("COURSE PROGRESS")
        # Just a mock progress based on concepts for now
        progress = min(1.0, len(concepts) / 20.0)
        st.markdown(f"`{render_progress_bar(progress)} {int(progress*100)}%`")
    
    with col2:
        st.caption("CONCEPT MASTERY")
        st.markdown(f"`{render_progress_bar(avg_mastery)} {int(avg_mastery*100)}%`")
        
    with col3:
        st.caption("SYSTEM STREAK")
        st.markdown("`█████░░░░░ 05 DAYS`")
        
    st.markdown("---")
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader("WEAK CONCEPTS")
        if not states:
            st.write("`[ NO CONCEPTS EXTRACTED ]`")
        else:
            for s in states[:3]:
                if s["mastery_score"] < 0.7:
                    st.markdown(f"> `{s['label']}`  (Mastery: {int(s['mastery_score']*100)}%)")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("NEXT RECOMMENDED ACTION")
        action = get_next_best_action(user_id, selected_course_id, db)
        
        st.info(f"**TARGET**: {action['title']}\n\n**REASON**: {action['reason']}\n\n**EFFORT**: {action['estimated_effort']}")
        if st.button("EXECUTE RECOMMENDED ACTION", type="primary"):
            if "review" in action["title"].lower():
                st.session_state.current_page = "Review"
            elif "learn" in action["title"].lower() or "read" in action["title"].lower():
                st.session_state.current_page = "Tutor"
            else:
                st.session_state.current_page = "Exams"
            st.rerun()

    with col_side:
        st.subheader("RECENT ACTIVITY")
        recent_attempts = db.query(QuestionAttempt).filter_by(course_id=selected_course_id).order_by(QuestionAttempt.timestamp.desc()).limit(5).all()
        if recent_attempts:
            for a in recent_attempts:
                status = "PASS" if a.score >= 70 else "FAIL"
                st.markdown(f"`[{a.timestamp.strftime('%H:%M')}] DIAGNOSTIC: {status}`")
        else:
            st.write("`[ LOG EMPTY ]`")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("MEMORY BANK")
        now = datetime.utcnow()
        due_count = db.query(Flashcard).filter(Flashcard.course_id == selected_course_id, Flashcard.next_review <= now).count()
        st.markdown(f"`DUE REVIEWS: {due_count:02d}`")
