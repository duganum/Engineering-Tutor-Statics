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
st.set_page_config(page_title="Engineering Statics Tutor", layout="wide", initial_sidebar_state="expanded")

# 2. CSS Styling: Ensuring sidebar visibility and compact layout
st.markdown("""
    <style>
    /* Ensure sidebar is visible */
    [data-testid="stSidebar"] {
        min-width: 180px !important;
    }
    
    /* Remove top padding */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    header {visibility: hidden;}
    
    /* Minimize spacing */
    .stVerticalBlock { gap: 0.5rem; }
    
    div.stButton > button {
        height: 50px;
        padding: 5px 10px;
        font-size: 14px;
        font-weight: 700;
    }
    
    /* Activity Indicator Styling */
    .indicator-box {
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        margin-top: 5px;
        border: 1px solid rgba(0,0,0,0.1);
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

# --- MANDATORY SIDEBAR (Always Runs) ---
with st.sidebar:
    st.title("👨‍🏫 Tutor Control")
    st.markdown("### 🤖 Agent Status")
    if st.session_state.api_busy:
        st.markdown('<div class="indicator-box" style="background-color: #ff4b4b; color: white;">🔴 Busy</div>', unsafe_allow_html=True)
        st.caption("Processing your analysis...")
    else:
        st.markdown('<div class="indicator-box" style="background-color: #28a745; color: white;">🟢 Ready</div>', unsafe_allow_html=True)
        st.caption("System active.")
    st.markdown("---")

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
        
        if st.button("⬅️ Submit & Return", key="submit_session_btn", use_container_width=True):
            with st.spinner("Submitting academic report..."):
                history_text = ""
                if p_id in st.session_state.chat_sessions:
                    for msg in st.session_state.chat_sessions[p_id].history:
                        role = "Tutor" if msg.role == "model" else "Student"
                        history_text += f"{role}: {msg.parts[0].text}\n"
                analyze_and_send_report(st.session_state.user_name, prob['category'], f"History:\n{history_text}\nStudent Feedback: {feedback}")
                st.toast("Report sent successfully!")
                time.sleep(1)
            st.session_state.page = "landing"; st.rerun()

    with cols[1]:
        st.markdown("### 💬 Socratic Discussion")
        if p_id not in st.session_state.chat_sessions:
            sys_prompt = f"You are Professor Um. Use Socratic Method for: {prob['statement']}. Use LaTeX."
            model = get_gemini_model(sys_prompt)
            st.session_state.chat_sessions[p_id] = model.start_chat(history=[])
            
            # Use append to insert the start message without an immediate AI response
            start_msg = f"Hello {st.session_state.user_name}. To begin, look at the diagram. Where do all the forces meet? That's the point we want to isolate first."
            st.session_state.chat_sessions[p_id].history.append({"role": "model", "parts": [start_msg]})

        chat_container = st.container(height=350)
        with chat_container:
            if p_id in st.session_state.chat_sessions:
                for msg in st.session_state.chat_sessions[p_id].history:
                    role = "assistant" if (hasattr(msg, 'role') and msg.role == "model") or (isinstance(msg, dict) and msg.get('role') == 'model') else "user"
                    text = msg.parts[0].text if hasattr(msg, 'parts') else msg.get('parts')[0]
                    with st.chat_message(role):
                        st.markdown(text)

        if user_input := st.chat_input("Analyze..."):
            st.session_state.api_busy = True
            for target, val in prob['targets'].items():
                if target not in solved and check_numeric_match(user_input, val):
                    st.session_state.grading_data[p_id]['solved'].add(target)
                    st.toast(f"Correct: {target}!")
            
            try:
                st.session_state.chat_sessions[p_id].send_message(user_input)
            except:
                st.error("Connection interrupted.")
            
            st.session_state.api_busy = False
            st.rerun()

# --- Page 3: Interactive Lecture ---
elif st.session_state.page == "lecture":
    topic = st.session_state.lecture_topic
    st.markdown(f"## 🎓 Lab: {topic}")
    col_sim, col_chat = st.columns([1, 1])
    
    with col_sim:
        # Simulation parameters and visual...
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
        
        if st.button("🏠 Exit", key="exit_lecture_btn", use_container_width=True):
            with st.spinner("Submitting lab report..."):
                history_text = ""
                if "lecture_session" in st.session_state and st.session_state.lecture_session:
                    for msg in st.session_state.lecture_session.history:
                        role = "Professor" if msg.role == "model" else "Student"
                        history_text += f"{role}: {msg.parts[0].text}\n"
                analyze_and_send_report(st.session_state.user_name, f"LECTURE: {topic}", history_text)
            st.session_state.page = "landing"; st.rerun()

    with col_chat:
        st.markdown("### 💬 Discussion")
        if "lecture_session" not in st.session_state or st.session_state.lecture_session is None:
            model = get_gemini_model("Professor Um mode")
            st.session_state.lecture_session = model.start_chat(history=[])
            start_msg = f"Hello {st.session_state.user_name}. Based on the current lab parameters, what do you observe about the equilibrium?"
            st.session_state.lecture_session.history.append({"role": "model", "parts": [start_msg]})
        
        chat_l_container = st.container(height=350)
        with chat_l_container:
            if st.session_state.get("lecture_session"):
                for msg in st.session_state.lecture_session.history:
                    role = "assistant" if (hasattr(msg, 'role') and msg.role == "model") or (isinstance(msg, dict) and msg.get('role') == 'model') else "user"
                    text = msg.parts[0].text if hasattr(msg, 'parts') else msg.get('parts')[0]
                    with st.chat_message(role):
                        st.markdown(text)
        
        if l_input := st.chat_input("Discuss..."):
            st.session_state.api_busy = True
            try:
                st.session_state.lecture_session.send_message(l_input)
            except:
                st.error("Connection interrupted.")
            st.session_state.api_busy = False
            st.rerun()
