import streamlit as st
import json
import re
import numpy as np
import matplotlib.pyplot as plt
import os
import time

# Import custom tools
from logic_v2_GitHub import get_gemini_model, load_problems, check_numeric_match, analyze_and_send_report
from render_v2_GitHub import render_problem_diagram, render_lecture_visual

# 1. Page Configuration
st.set_page_config(page_title="Engineering Statics Tutor", layout="wide")

# 2. CSS Styling: Removing top padding and compacting elements
st.markdown("""
    <style>
    /* Remove top padding of the main container */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Minimize spacing between elements */
    .stVerticalBlock { gap: 0.5rem; }
    
    div.stButton > button {
        height: 50px;
        padding: 5px 10px;
        font-size: 14px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    /* Activity Indicator Styling */
    .indicator-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "grading_data" not in st.session_state: st.session_state.grading_data = {}
if "user_name" not in st.session_state: st.session_state.user_name = None
if "lecture_topic" not in st.session_state: st.session_state.lecture_topic = None
if "api_busy" not in st.session_state: st.session_state.api_busy = False

PROBLEMS = load_problems()

# --- Activity Indicator Logic ---
def draw_indicator():
    with st.sidebar:
        st.markdown("### 🤖 Agent Status")
        if st.session_state.api_busy:
            st.markdown('<div class="indicator-box" style="background-color: #ff4b4b; color: white;">🔴 Professor is Busy</div>', unsafe_allow_html=True)
            st.caption("The AI is currently processing or rate-limited. Please wait a moment.")
        else:
            st.markdown('<div class="indicator-box" style="background-color: #28a745; color: white;">🟢 Professor is Ready</div>', unsafe_allow_html=True)
            st.caption("Connection stable. You can proceed with your analysis.")

# --- Page 0: Name Entry ---
if st.session_state.user_name is None:
    st.title("🛡️ Engineering Mechanics Portal")
    with st.form("name_form"):
        name_input = st.text_input("Enter Full Name to begin")
        if st.form_submit_button("Access Tutor"):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.rerun()
    st.stop()

# --- Page 1: Main Menu ---
if st.session_state.page == "landing":
    draw_indicator()
    st.title("🏗️ Engineering Statics")
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    
    st.markdown("---")
    st.subheader("💡 Interactive Learning Agents")
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    lectures = [
        ("Free Body Diagram", "S_1.1"), ("Truss", "S_1.2"), 
        ("Geometric Properties", "S_1.3"), ("Equilibrium", "S_1.4")
    ]
    for i, (name, pref) in enumerate(lectures):
        with [col_l1, col_l2, col_l3, col_l4][i]:
            if st.button(f"🎓 Lecture: {name}", key=f"lec_{pref}", use_container_width=True):
                st.session_state.lecture_topic = name
                st.session_state.page = "lecture"; st.rerun()

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
                            st.session_state.page = "chat"; st.rerun()

# --- Page 2: Socratic Chat ---
elif st.session_state.page == "chat":
    draw_indicator()
    prob = st.session_state.current_prob
    p_id = prob['id']
    if p_id not in st.session_state.grading_data: st.session_state.grading_data[p_id] = {'solved': set()}
    solved = st.session_state.grading_data[p_id]['solved']
    
    cols = st.columns([1, 1.2])
    
    with cols[0]:
        st.markdown(f"### 📌 {prob['category']}")
        st.info(prob['statement'])
        st.image(render_problem_diagram(prob), use_container_width=False)
        
        feedback = st.text_area("Notes for Dr. Um:", placeholder="Provide your feedback to the professor.", height=70)
        if st.button("⬅️ Submit & Return", use_container_width=True):
            st.session_state.page = "landing"; st.rerun()

    with cols[1]:
        st.markdown("### 💬 Socratic Discussion")
        if p_id not in st.session_state.chat_sessions:
            sys_prompt = f"You are Professor Um. Use Socratic Method for: {prob['statement']}. Use LaTeX."
            # Plain initialization without nested try/except
            model = get_gemini_model(sys_prompt)
            st.session_state.chat_sessions[p_id] = model.start_chat(history=[])

        chat_container = st.container(height=350)
        with chat_container:
            if p_id in st.session_state.chat_sessions:
                for msg in st.session_state.chat_sessions[p_id].history:
                    with st.chat_message("assistant" if msg.role == "model" else "user"):
                        st.markdown(msg.parts[0].text)

        if user_input := st.chat_input("Analyze..."):
            st.session_state.api_busy = True
            for target, val in prob['targets'].items():
                if target not in solved and check_numeric_match(user_input, val):
                    st.session_state.grading_data[p_id]['solved'].add(target)
                    st.toast(f"Correct: {target}!")
            
            # Simple direct message sending to monitor cause of failure
            with st.spinner("Professor is reflecting..."):
                st.session_state.chat_sessions[p_id].send_message(user_input)
            
            st.session_state.api_busy = False
            st.rerun()

# --- Page 3: Interactive Lecture ---
elif st.session_state.page == "lecture":
    draw_indicator()
    topic = st.session_state.lecture_topic
    st.markdown(f"## 🎓 Lab: {topic}")
    col_sim, col_chat = st.columns([1, 1])
    
    with col_sim:
        params = {}
        if topic == "Free Body Diagram":
            params['force'] = st.slider("Force", 10, 100, 50)
            params['theta'] = st.slider("Angle", 0, 90, 45)
        elif topic == "Truss":
            params['load'] = st.slider("Load", 10, 100, 50)
        elif topic == "Geometric Properties":
            params['width'] = st.slider("Width", 10, 80, 40)
            params['height'] = st.slider("Height", 10, 80, 60)
        elif topic == "Equilibrium":
            params['w'] = st.slider("Weight", 10, 100, 50)
            params['d'] = st.slider("Distance", 10, 80, 40)
        
        st.image(render_lecture_visual(topic, params))
        if st.button("🏠 Exit", use_container_width=True):
            st.session_state.page = "landing"; st.rerun()

    with col_chat:
        st.markdown("### 💬 Discussion")
        if "lecture_session" not in st.session_state or st.session_state.lecture_session is None:
            model = get_gemini_model("Professor Um mode")
            st.session_state.lecture_session = model.start_chat(history=[])
        
        chat_l_container = st.container(height=350)
        with chat_l_container:
            if st.session_state.get("lecture_session"):
                for msg in st.session_state.lecture_session.history:
                    with st.chat_message("assistant" if msg.role == "model" else "user"):
                        st.markdown(msg.parts[0].text)
        
        if l_input := st.chat_input("Discuss..."):
            st.session_state.api_busy = True
            with st.spinner("Thinking..."):
                st.session_state.lecture_session.send_message(l_input)
            st.session_state.api_busy = False
            st.rerun()
