import streamlit as st
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import os

# Import custom tools
from logic_v2_GitHub import get_gemini_model, load_problems, check_numeric_match, analyze_and_send_report
from render_v2_GitHub import render_problem_diagram, render_lecture_visual

# 1. Page Configuration
st.set_page_config(page_title="Engineering Statics Tutor", layout="wide")

# 2. CSS Styling
st.markdown("""
    <style>
    div.stButton > button {
        height: 60px;
        padding: 5px 10px;
        font-size: 14px;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "grading_data" not in st.session_state: st.session_state.grading_data = {}
if "user_name" not in st.session_state: st.session_state.user_name = None
if "lecture_topic" not in st.session_state: st.session_state.lecture_topic = None

PROBLEMS = load_problems()

# --- Page 0: Name Entry ---
if st.session_state.user_name is None:
    st.title("🛡️ Engineering Mechanics Portal")
    st.markdown("### Texas A&M University - Corpus Christi")
    with st.form("name_form"):
        name_input = st.text_input("Enter your Full Name to begin")
        if st.form_submit_button("Access Tutor"):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.rerun()
            else:
                st.warning("Identification is required for academic reporting.")
    st.stop()

# --- Page 1: Main Menu ---
if st.session_state.page == "landing":
    st.title("🏗️ Engineering Statics")
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.info("Texas A&M University - Corpus Christi | Dr. Dugan Um")
    
    st.markdown("---")
    st.subheader("💡 Interactive Learning Agents")
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    lectures = [
        ("Free Body Diagram", "S_1.1"), 
        ("Truss", "S_1.2"), 
        ("Geometric Properties", "S_1.3"),
        ("Equilibrium", "S_1.4")
    ]
    for i, (name, pref) in enumerate(lectures):
        with [col_l1, col_l2, col_l3, col_l4][i]:
            if st.button(f"🎓 Lecture: {name}", key=f"lec_{pref}", use_container_width=True):
                st.session_state.lecture_topic = name
                st.session_state.page = "lecture"
                st.rerun()

    st.markdown("---")
    st.subheader("📝 Practice Problems")
    categories = {}
    for p in PROBLEMS:
        cat_main = p.get('category', 'General').split(":")[-1].strip()
        if cat_main not in categories: categories[cat_main] = []
        categories[cat_main].append(p)

    for cat_name, probs in categories.items():
        st.markdown(f"#### {cat_name}")
        for i in range(0, len(probs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(probs):
                    prob = probs[i + j]
                    with cols[j]:
                        if st.button(f"**Problem {prob['id']}**", key=f"btn_{prob['id']}", use_container_width=True):
                            st.session_state.current_prob = prob
                            st.session_state.page = "chat"
                            st.rerun()

# --- Page 2: Socratic Chat ---
elif st.session_state.page == "chat":
    prob = st.session_state.current_prob
    p_id = prob['id']
    if p_id not in st.session_state.grading_data: st.session_state.grading_data[p_id] = {'solved': set()}
    solved = st.session_state.grading_data[p_id]['solved']
    
    # PROBLEM ON LEFT (1), CHAT ON RIGHT (2)
    cols = st.columns([1, 1.2])
    
    with cols[0]:
        st.subheader(f"📌 {prob['category']}")
        with st.container():
            st.info(prob['statement'])
            # Rendered with High DPI for crispness
            st.image(render_problem_diagram(prob), use_container_width=False)
        
        st.markdown("---")
        feedback = st.text_area("Notes for Dr. Um:", placeholder="Hardest part of this problem?", height=100)
        
        if st.button("⬅️ Submit & Return to Menu", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()

    with cols[1]:
        st.subheader("💬 Socratic Discussion")
        
        if p_id not in st.session_state.chat_sessions:
            sys_prompt = f"You are Professor Um. Guide the student through {prob['category']}. Statement: {prob['statement']}. Use Socratic Method. Use LaTeX."
            st.session_state.chat_sessions[p_id] = get_gemini_model(sys_prompt).start_chat(history=[])

        # Chat Container
        chat_container = st.container(height=450)
        with chat_container:
            for msg in st.session_state.chat_sessions[p_id].history:
                with st.chat_message("assistant" if msg.role == "model" else "user"):
                    st.markdown(msg.parts[0].text)

        if user_input := st.chat_input("Analyze the forces..."):
            for target, val in prob['targets'].items():
                if target not in solved and check_numeric_match(user_input, val):
                    st.session_state.grading_data[p_id]['solved'].add(target)
                    st.toast(f"Correct: {target} identified!")

            try:
                with st.spinner("Professor Um is thinking..."):
                    st.session_state.chat_sessions[p_id].send_message(user_input)
                st.rerun()
            except Exception as e:
                st.error("The Professor is busy. Please wait a moment.")

# --- Page 3: Interactive Lecture ---
elif st.session_state.page == "lecture":
    topic = st.session_state.lecture_topic
    st.title(f"🎓 Lab: {topic}")
    col_sim, col_chat = st.columns([1, 1])
    
    with col_sim:
        params = {}
        if topic == "Free Body Diagram":
            params['force'] = st.slider("Force (N)", 10, 100, 50)
            params['theta'] = st.slider("Angle (°)", 0, 90, 45)
        elif topic == "Truss":
            params['load'] = st.slider("Load (N)", 10, 100, 50)
        elif topic == "Geometric Properties":
            params['width'] = st.slider("Width", 10, 80, 40)
            params['height'] = st.slider("Height", 10, 80, 60)
        elif topic == "Equilibrium":
            params['w'] = st.slider("Force (N)", 10, 100, 50)
            params['d'] = st.slider("Distance (m)", 10, 80, 40)
        
        st.image(render_lecture_visual(topic, params))
        
        if st.button("🏠 Exit to Main Menu", use_container_width=True):
            st.session_state.lecture_session = None
            st.session_state.page = "landing"
            st.rerun()

    with col_chat:
        st.subheader("💬 Discussion")
        if "lecture_session" not in st.session_state or st.session_state.lecture_session is None:
            sys_msg = f"You are Professor Um. Teaching {topic}. Use Socratic method."
            st.session_state.lecture_session = get_gemini_model(sys_msg).start_chat(history=[])

        chat_l_container = st.container(height=450)
        with chat_l_container:
            for msg in st.session_state.lecture_session.history:
                with st.chat_message("assistant" if msg.role == "model" else "user"):
                    st.markdown(msg.parts[0].text)
        
        if l_input := st.chat_input("Discuss the physics..."):
            try:
                st.session_state.lecture_session.send_message(l_input)
                st.rerun()
            except:
                st.error("Rate limit reached.")
