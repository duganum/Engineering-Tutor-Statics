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

# 2. CSS Styling: Clean, Full-Width Layout
st.markdown("""
    <style>
    /* Remove top padding and hide headers */
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Minimize spacing between blocks */
    .stVerticalBlock { gap: 0.75rem; }
    
    /* Button Styling */
    div.stButton > button {
        height: 50px;
        font-size: 14px;
        font-weight: 700;
        transition: all 0.2s ease;
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
            with st.spinner("Submitting report..."):
                history_text = ""
                if p_id in st.session_state.chat_sessions:
                    for msg in st.session_state.chat_sessions[p_id].history:
                        role = "Tutor" if msg.role == "model" else "Student"
                        history_text += f"{role}: {msg.parts[0].text}\n"
                analyze_and_send_report(st.session_state.user_name, prob['category'], f"History:\n{history_text}\nFeedback: {feedback}")
            st.session_state.page = "landing"; st.rerun()

    with cols[1]:
        st.markdown("### 💬 Socratic Discussion")
        if p_id not in st.session_state.chat_sessions:
            sys_prompt = f"You are Professor Um. Use Socratic Method for: {prob['statement']}. Use LaTeX."
            model = get_gemini_model(sys_prompt)
            st.session_state.chat_sessions[p_id] = model.start_chat(history=[])
            
            # Start message without AI self-trigger
            start_msg = f"Hello {st.session_state.user_name}. Looking at the diagram, where do all the forces meet? Let's start by identifying that point."
            st.session_state.chat_sessions[p_id].history.append({"role": "model", "parts": [start_msg]})

        chat_container = st.container(height=380)
        with chat_container:
            if p_id in st.session_state.chat_sessions:
                for msg in st.session_state.chat_sessions[p_id].history:
                    role = "assistant" if (hasattr(msg, 'role') and msg.role == "model") or (isinstance(msg, dict) and msg.get('role') == 'model') else "user"
                    text = msg.parts[0].text if hasattr(msg, 'parts') else msg.get('parts')[0]
                    with st.chat_message(role):
                        st.markdown(text)

        if user_input := st.chat_input("Analyze..."):
            for target, val in prob['targets'].items():
                if target not in solved and check_numeric_match(user_input, val):
                    st.session_state.grading_data[p_id]['solved'].add(target)
                    st.toast(f"Correct: {target}!")
            
            with st.spinner("Professor Um is reflecting..."):
                try:
                    st.session_state.chat_sessions[p_id].send_message(user_input)
                    st.rerun()
                except:
                    st.error("The Professor is temporarily busy. Please wait 10 seconds.")

# --- Page 3: Interactive Lecture ---
elif st.session_state.page == "lecture":
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
        
        if st.button("🏠 Exit", key="exit_lecture_btn", use_container_width=True):
            with st.spinner("Saving lab session..."):
                history_text = ""
                if "lecture_session" in st.session_state and st.session_state.lecture_session:
                    for msg in st.session_state.lecture_session.history:
                        role = "Professor" if msg.role == "model" else "Student"
                        history_text += f"{role}: {msg.parts[0].text}\n"
                analyze_and_send_report(st.session_state.user_name, f"LAB: {topic}", history_text)
            st.session_state.page = "landing"; st.rerun()

    with col_chat:
        st.markdown("### 💬 Discussion")
        if "lecture_session" not in st.session_state or st.session_state.lecture_session is None:
            model = get_gemini_model("Professor Um Mode")
            st.session_state.lecture_session = model.start_chat(history=[])
            lab_start = f"Hello {st.session_state.user_name}. Based on these sliders, what do you think happens to the reaction forces?"
            st.session_state.lecture_session.history.append({"role": "model", "parts": [lab_start]})
        
        chat_l_container = st.container(height=380)
        with chat_l_container:
            if st.session_state.get("lecture_session"):
                for msg in st.session_state.lecture_session.history:
                    role = "assistant" if (hasattr(msg, 'role') and msg.role == "model") or (isinstance(msg, dict) and msg.get('role') == 'model') else "user"
                    text = msg.parts[0].text if hasattr(msg, 'parts') else msg.get('parts')[0]
                    with st.chat_message(role):
                        st.markdown(text)
        
        if l_input := st.chat_input("Discuss the simulation..."):
            with st.spinner("Thinking..."):
                try:
                    st.session_state.lecture_session.send_message(l_input)
                    st.rerun()
                except:
                    st.error("Connection pause. Please wait.")
