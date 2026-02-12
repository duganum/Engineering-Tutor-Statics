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

# 2. CSS Styling
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .status-badge {
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        display: inline-block;
        border: 1px solid rgba(0,0,0,0.1);
        margin-top: 10px;
    }
    div.stButton > button {
        height: 50px;
        font-size: 14px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "grading_data" not in st.session_state: st.session_state.grading_data = {}
if "user_name" not in st.session_state: st.session_state.user_name = None
if "api_busy" not in st.session_state: st.session_state.api_busy = False
if "current_msg" not in st.session_state: st.session_state.current_msg = None

PROBLEMS = load_problems()

# --- Helper Logic: Extract text from message history safely ---
def get_msg_text(msg):
    if hasattr(msg, 'parts'):
        return msg.parts[0].text
    elif isinstance(msg, dict):
        return msg.get('parts')[0]
    return ""

def get_msg_role(msg):
    role = msg.role if hasattr(msg, 'role') else msg.get('role', 'user')
    return "assistant" if role == "model" else "user"

# --- Helper: Activity Indicator in Header ---
def draw_header_with_status(title_text):
    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.title(title_text)
    with head_col2:
        if st.session_state.api_busy:
            st.markdown('<div class="status-badge" style="background-color: #ff4b4b; color: white;">🔴 Professor Busy</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge" style="background-color: #28a745; color: white;">🟢 Professor Ready</div>', unsafe_allow_html=True)

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
    draw_header_with_status("🏗️ Engineering Statics")
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.markdown("---")
    
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    lectures = [("Free Body Diagram", "S_1.1"), ("Truss", "S_1.2"), ("Geometric Properties", "S_1.3"), ("Equilibrium", "S_1.4")]
    for i, (name, pref) in enumerate(lectures):
        with [col_l1, col_l2, col_l3, col_l4][i]:
            if st.button(f"🎓 Lecture: {name}", key=f"lec_{pref}", use_container_width=True):
                st.session_state.lecture_topic = name
                st.session_state.page = "lecture"; st.rerun()

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
    
    draw_header_with_status(f"📌 {prob['category']}")
    cols = st.columns([1, 1.2])
    
    with cols[0]:
        st.info(prob['statement'])
        st.image(render_problem_diagram(prob), use_container_width=False)
        feedback = st.text_area("Notes for Dr. Um:", placeholder="Provide feedback...", height=70)
        
        if st.button("⬅️ Submit & Return", key="submit_session_btn", use_container_width=True):
            with st.spinner("Submitting..."):
                history_text = ""
                if p_id in st.session_state.chat_sessions:
                    history_text = "".join([f"{'Tutor' if get_msg_role(m)=='assistant' else 'Student'}: {get_msg_text(m)}\n" for m in st.session_state.chat_sessions[p_id].history])
                analyze_and_send_report(st.session_state.user_name, prob['category'], f"History:\n{history_text}\nFeedback: {feedback}")
                del st.session_state.chat_sessions[p_id]
            st.session_state.page = "landing"; st.rerun()

    with cols[1]:
        st.markdown("### 💬 Socratic Discussion")
        if p_id not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[p_id] = get_gemini_model(f"You are Prof. Um. Use Socratic Method for: {prob['statement']}").start_chat(history=[])
            st.session_state.chat_sessions[p_id].history.append({"role": "model", "parts": [f"Hello {st.session_state.user_name}. Look at the diagram; where do the forces meet?"]})

        chat_container = st.container(height=380)
        with chat_container:
            for msg in st.session_state.chat_sessions[p_id].history:
                with st.chat_message(get_msg_role(msg)): 
                    st.markdown(get_msg_text(msg))

        if not st.session_state.api_busy:
            if user_input := st.chat_input("Analyze..."):
                st.session_state.current_msg = user_input
                st.session_state.api_busy = True
                st.rerun()

    if st.session_state.api_busy and st.session_state.current_msg:
        for target, val in prob['targets'].items():
            if target not in solved and check_numeric_match(st.session_state.current_msg, val):
                st.session_state.grading_data[p_id]['solved'].add(target)
                st.toast(f"Correct: {target}!")
        with st.spinner("Professor Um is reflecting..."):
            try: st.session_state.chat_sessions[p_id].send_message(st.session_state.current_msg)
            except: st.error("Connection pause.")
        st.session_state.api_busy = False
        st.session_state.current_msg = None
        st.rerun()

# --- Page 3: Interactive Lecture ---
elif st.session_state.page == "lecture":
    topic = st.session_state.lecture_topic
    draw_header_with_status(f"🎓 Lab: {topic}")
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
            with st.spinner("Saving..."):
                history_text = ""
                if "lecture_session" in st.session_state:
                    history_text = "".join([f"Prof: {get_msg_text(m)}\n" for m in st.session_state.lecture_session.history])
                analyze_and_send_report(st.session_state.user_name, f"LAB: {topic}", history_text)
                if "lecture_session" in st.session_state: del st.session_state.lecture_session
            st.session_state.page = "landing"; st.rerun()

    with col_chat:
        st.markdown("### 💬 Socratic Teaching")
        if "lecture_session" not in st.session_state:
            # TIGHTENED SYSTEM PROMPT: Forces Socratic Method
            sys_msg = f"You are Professor Um teaching a lab on {topic}. STRICTOR RULE: Do NOT give the full lecture at once. You must use the Socratic Method. Ask the student one question at a time to lead them to the concept. Keep responses short."
            st.session_state.lecture_session = get_gemini_model(sys_msg).start_chat(history=[])
            
            # Start message
            lab_start = f"Hello {st.session_state.user_name}. Looking at the simulation on the left, if you increase the parameters, what do you think happens to the force vectors?"
            st.session_state.lecture_session.history.append({"role": "model", "parts": [lab_start]})
        
        chat_l_container = st.container(height=380)
        with chat_l_container:
            for msg in st.session_state.lecture_session.history:
                with st.chat_message(get_msg_role(msg)): 
                    st.markdown(get_msg_text(msg))
        
        if not st.session_state.api_busy:
            if l_input := st.chat_input("Answer the Professor..."):
                st.session_state.current_msg = l_input
                st.session_state.api_busy = True
                st.rerun()

    if st.session_state.api_busy and st.session_state.current_msg:
        with st.spinner("Thinking..."):
            try: st.session_state.lecture_session.send_message(st.session_state.current_msg)
            except: st.error("Rate limit pause.")
        st.session_state.api_busy = False
        st.session_state.current_msg = None
        st.rerun()
