import streamlit as st
from modules.db import QuestionAttempt, Misconception
from modules.cognitive_evaluator import generate_exam_questions, evaluate_response
from modules.rag_engine import RetrievalService
from modules.adaptive_learning import get_concept_state

def render(db, course_id, api_key):
    if not course_id:
        st.warning("NO ACTIVE CONTEXT. PLEASE SELECT A COURSE.")
        return
    if not api_key:
        st.error("API KEY MISSING. PLEASE CONFIGURE SYSTEM.")
        return
        
    st.header("△ DIAGNOSTIC EXAM")
    st.caption("ADAPTIVE COGNITIVE EVALUATION")
    st.write("An infinite practice loop. Questions adapt to your mistakes.")
    
    if "adaptive_exam_active" not in st.session_state:
        st.session_state.adaptive_exam_active = False
        
    if not st.session_state.adaptive_exam_active:
        if st.button("Start Adaptive Session", type="primary"):
            st.session_state.adaptive_exam_active = True
            st.session_state.exam_history = []
            st.session_state.current_q = None
            st.rerun()
        return
        
    if st.button("End Session"):
        st.session_state.adaptive_exam_active = False
        st.session_state.current_q = None
        st.rerun()
        
    # Generate next question if we don't have one
    if not st.session_state.current_q:
        with st.spinner("Analyzing your mastery to generate the next question..."):
            rs = RetrievalService(api_key)
            
            # Decide target concept based on previous mistake or lowest mastery
            target_concept = None
            if st.session_state.exam_history and st.session_state.exam_history[-1]["score"] < 80:
                target_concept = st.session_state.exam_history[-1]["primary_concept"]
                st.info(f"Targeting weak concept: {target_concept}")
            
            query = f"Core information about {target_concept}" if target_concept else "Core concepts"
            evidence = rs.retrieve(query, course_id, db, top_k=5)
            context = "\n".join([c["text"] for c in evidence])
            
            qs = generate_exam_questions(context, api_key, num_questions=1, target_concept=target_concept)
            if qs:
                st.session_state.current_q = qs[0]
                st.session_state.current_context = context
                st.rerun()
            else:
                st.error("Failed to generate question.")
                return

    # Display Current Question
    q = st.session_state.current_q
    st.subheader(f"Question: {q.question}")
    st.caption(f"Bloom's Level: {q.bloom_level} | Target Concept: {q.primary_concept}")
    
    user_ans = st.text_area("Your Answer", key="adaptive_ans")
    
    if st.button("Submit Answer", type="primary"):
        with st.spinner("Evaluating..."):
            res = evaluate_response(q.question, user_ans, st.session_state.current_context, api_key)
            
            if not res:
                st.error("Failed to parse evaluation response.")
                return
                
            # Log Mistake & Misconception
            misc_id = None
            if res.misconception and res.misconception.lower() != "none":
                from modules.db import Concept
                concept_obj = db.query(Concept).filter_by(label=res.primary_concept, course_id=course_id).first()
                c_id = concept_obj.id if concept_obj else None
                
                misc = Misconception(
                    course_id=course_id,
                    concept_id=c_id,
                    category=res.misconception_category or "Unknown",
                    description=res.misconception
                )
                db.add(misc)
                db.commit()
                misc_id = misc.id
                
            # Log Attempt
            attempt = QuestionAttempt(
                course_id=course_id,
                concept_id=c_id if 'c_id' in locals() else None,
                question=q.question,
                student_answer=user_ans,
                score=res.score,
                bloom_level=q.bloom_level,
                misconception_id=misc_id
            )
            db.add(attempt)
            db.commit()
            
            # Immediately update learning state for the concept
            if attempt.concept_id:
                get_concept_state(st.session_state.user_id, course_id, attempt.concept_id, db)
            
            st.session_state.exam_history.append({
                "question": q.question,
                "score": res.score,
                "primary_concept": q.primary_concept,
                "feedback": res.reasoning_quality,
                "socratic": res.socratic_guidance
            })
            
            st.session_state.current_q = None
            st.rerun()

    # Display History
    if st.session_state.exam_history:
        st.divider()
        st.subheader("Session History")
        for h in reversed(st.session_state.exam_history):
            with st.expander(f"{h['score']}/100 - {h['question']}"):
                st.write(f"**Feedback:** {h['feedback']}")
                if h['socratic'] and h['socratic'].lower() != "none":
                    st.info(f"**Socratic Hint:** {h['socratic']}")
