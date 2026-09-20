import streamlit as st
from modules.db import Flashcard, update_sm2, MistakeLog, Concept, FlashcardReviewEvent
from datetime import datetime
from modules.adaptive_learning import get_concept_state

def render(db, course_id):
    if not course_id:
        st.warning("NO ACTIVE CONTEXT. PLEASE SELECT A COURSE.")
        return
        
    st.header("◇ MEMORY BANK REVIEW")
    st.caption("SPACED REPETITION PROTOCOL INITIATED")
    
    with st.expander("MANUAL OVERRIDE: ADD CARD"):
        f_front = st.text_area("Front")
        f_back = st.text_area("Back")
        if st.button("Save Card"):
            if f_front and f_back:
                c = Flashcard(course_id=course_id, front=f_front, back=f_back)
                db.add(c)
                db.commit()
                st.success("Saved!")
                st.rerun()
                
    st.divider()
    
    now = datetime.utcnow()
    # Prioritize cards that are due, then order by ease factor to show harder ones first
    due_cards = db.query(Flashcard).filter(
        Flashcard.course_id == course_id, 
        Flashcard.next_review <= now
    ).order_by(Flashcard.ease_factor.asc()).all()
    
    if not due_cards:
        st.success("🎉 You are all caught up for today in this course!")
        st.info("Check your Dashboard for your Next Best Action.")
        return
        
    st.subheader(f"Due Today: {len(due_cards)}")
    
    card = due_cards[0]
    
    st.markdown("### Question")
    st.info(card.front)
    
    if "review_show_answer" not in st.session_state:
        st.session_state.review_show_answer = False
        
    if not st.session_state.review_show_answer:
        if st.button("Show Answer", type="primary"):
            st.session_state.review_show_answer = True
            st.rerun()
    else:
        st.markdown("### Answer")
        st.success(card.back)
        
        st.write("How well did you remember this?")
        cols = st.columns(6)
        grades = ["0 - Blackout", "1 - Incorrect (Fam)", "2 - Incorrect (Easy)", "3 - Hard", "4 - Good", "5 - Perfect"]
        for i in range(6):
            if cols[i].button(grades[i]):
                prev_interval = card.interval
                
                # Transactional update
                update_sm2(card, i)
                
                # Log event
                rev = FlashcardReviewEvent(
                    flashcard_id=card.id,
                    quality=i,
                    previous_interval=prev_interval,
                    new_interval=card.interval
                )
                db.add(rev)
                db.commit()
                
                # Update learning state immediately if it has a concept
                if card.concept_id:
                    get_concept_state(st.session_state.user_id, course_id, card.concept_id, db)
                
                st.session_state.review_show_answer = False
                st.rerun()
