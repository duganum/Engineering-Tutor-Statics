import streamlit as st
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from logic_v2_GitHub import get_gemini_model, load_problems, check_numeric_match, analyze_and_send_report
from render_v2_GitHub import render_problem_diagram, render_lecture_visual

# 1. Page Configuration
st.set_page_config(page_title="Engineering Statics", layout="wide")

# 2. CSS: UI consistency
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
    st.title("🏗️ Engineering Statics")
    st.markdown("### Texas A&M University - Corpus Christi | Dr. Dugan Um")
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
    # 1. Engineering Statics title at the very top
    st.title("🏗️ Engineering Statics")
    st.subheader(f"Welcome, {st.session_state.user_name}!")
    st.info("Texas A&M University - Corpus Christi | Dr. Dugan Um")
    
    # Section A: Interactive Lectures
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

    # Section B: Practice Problems
    st.markdown("---")
    st.subheader("📝 Practice Problems")
    categories = {}
    for p in PROBLEMS:
        cat_main = p.get('category', 'General').split(":")[0].strip()
        if cat_main not in categories: categories[cat_main] = []
        categories[cat_main].append(p)

    for cat_name, probs in categories.items():
        # 2. Removed "Statics" label below "Practice Problems"
        if cat_name != "Statics":
            st.markdown(f"#### {cat_name}")
            
        for i in range(0, len(probs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(probs):
                    prob = probs[i + j]
                    sub_label = prob.get('category', '').split(":")[-1].strip()
                    with cols[j]:
                        if st.button(f"**{sub_label}**\n({prob['id']})", key=f"btn_{prob['id']}", use_container_width=True):
                            st.session_state.current_prob = prob
                            st.session_state.page = "chat"
                            st.rerun()
    st.markdown("---")

# --- Page 2 & 3 (Chat and Lecture logic remains the same) ---
elif st.session_state.page == "chat":
    # (Existing chat logic...)
    pass

elif st.session_state.page == "lecture":
    # (Existing lecture logic...)
    pass

elif st.session_state.page == "report_view":
    st.title("📊 Performance Summary")
    st.markdown(st.session_state.get("last_report", "No report available."))
    if st.button("Return to Main Menu"):
        st.session_state.page = "landing"; st.rerun()
