import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from modules.db import get_session, User, Course
from components import home, tutor, review, exam, documents, analytics, knowledge, style

import sys
import io

# Force UTF-8 encoding for stdout/stderr to prevent logging crashes in Streamlit Cloud
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

st.set_page_config(page_title="U/SA OS", page_icon="⚡", layout="wide")
style.apply_cyber_theme()

# Init Session State
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "current_course_id" not in st.session_state:
    st.session_state.current_course_id = None
if "current_api_key" not in st.session_state:
    st.session_state.current_api_key = os.getenv("GEMINI_API_KEY")

db = get_session()

# User Authentication (MVP)
if "user_id" not in st.session_state:
    st.title("SYSTEM LOGIN // U/SA")
    st.write("Please authenticate to access the workspace.")
    
    with st.form("login_form"):
        username_input = st.text_input("IDENTIFIER")
        submit = st.form_submit_button("AUTHENTICATE")
        
        if submit and username_input.strip():
            username = username_input.strip().lower()
            user = db.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username)
                db.add(user)
                db.commit()
            st.session_state.user_id = user.id
            st.session_state.username = user.username
            st.rerun()
    st.stop() # Halt execution until logged in

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    ```text
    ╭─────────────────────╮
    │  U/SA               │
    │  UNIVERSITY OS      │
    ╰─────────────────────╯
    ```
    """)
    
    # API Key Handling
    st.caption("SYSTEM CFG")
    api_key_input = st.text_input("GEMINI KEY", value=st.session_state.current_api_key if st.session_state.current_api_key else "", type="password")
    if api_key_input:
        st.session_state.current_api_key = api_key_input
    
    st.divider()

    st.caption("NAVIGATION")
    if st.button("⌂ DASHBOARD", use_container_width=True): st.session_state.current_page = "Dashboard"
    if st.button("◈ DOCUMENTS", use_container_width=True): st.session_state.current_page = "Documents"
    if st.button("◎ NEURAL TUTOR", use_container_width=True): st.session_state.current_page = "Tutor"
    if st.button("◇ FLASHCARDS", use_container_width=True): st.session_state.current_page = "Review"
    if st.button("△ DIAGNOSTIC", use_container_width=True): st.session_state.current_page = "Exams"
    if st.button("⌁ ANALYTICS", use_container_width=True): st.session_state.current_page = "Analytics"
    if st.button("⎔ CONCEPT GRAPH", use_container_width=True): st.session_state.current_page = "Knowledge"

    st.divider()
    
    # Active Course Selector
    st.caption("ACTIVE CONTEXT")
    courses = db.query(Course).filter_by(user_id=st.session_state.user_id).all()
    if courses:
        course_opts = {c.id: c.title for c in courses}
        selected_course = st.selectbox(
            "Active Course", 
            options=list(course_opts.keys()), 
            format_func=lambda x: course_opts[x],
            index=list(course_opts.keys()).index(st.session_state.current_course_id) if st.session_state.current_course_id in course_opts else 0
        )
        st.session_state.current_course_id = selected_course
    else:
        st.info("No courses found. Create one on the Home page.")

# Routing
if st.session_state.current_page == "Dashboard":
    home.render(db, st.session_state.user_id)
elif st.session_state.current_page == "Documents":
    documents.render(db, st.session_state.current_course_id)
elif st.session_state.current_page == "Knowledge":
    knowledge.render(db, st.session_state.current_course_id)
elif st.session_state.current_page == "Tutor":
    tutor.render(db, st.session_state.current_course_id, st.session_state.current_api_key)
elif st.session_state.current_page == "Review":
    review.render(db, st.session_state.current_course_id)
elif st.session_state.current_page == "Exams":
    exam.render(db, st.session_state.current_course_id, st.session_state.current_api_key)
elif st.session_state.current_page == "Analytics":
    analytics.render(db, st.session_state.current_course_id)
else:
    st.error("Page not found.")
