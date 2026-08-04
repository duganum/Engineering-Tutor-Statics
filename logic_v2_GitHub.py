import json
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st


def get_gemini_model(system_instruction):
    """Initializes and returns the Gemini 2.0 Flash model."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=system_instruction,
        )
    except Exception as e:
        st.error(f"Gemini Initialization Failed: {e}")
        return None


def load_problems():
    """Loads the list of Statics problems from the JSON repository."""
    try:
        with open("problems_v2_GitHub.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Problem bank load error: {e}")
        return []


def check_numeric_match(user_val, correct_val, tolerance=0.05):
    """Extracts numbers and checks if they are within a 5% error margin."""
    try:
        u_match = re.search(r"[-+]?\d*\.\d+|\d+", str(user_val))
        if not u_match:
            return False
        u = float(u_match.group())
        c = float(correct_val)
        if c == 0:
            return abs(u) < tolerance
        return abs(u - c) <= abs(tolerance * c)
    except (ValueError, TypeError, AttributeError):
        return False


def evaluate_understanding_score(chat_history):
    """Evaluates student understanding (0-10) based on Statics principles.

    Focuses on Free Body Diagrams (FBD) and Equilibrium equations.
    """
    if not chat_history or len(str(chat_history).strip()) == 0:
        return 0

    eval_instruction = (
        "You are an Engineering Professor at Texas A&M University - Corpus"
        " Christi. Evaluate the student's level of Statics mastery (0-10) on the"
        " FIRST attempt based ONLY on the chat transcript.\n\n"
        "CORE EVALUATION RULE:\n"
        "If the student successfully solves the assigned Statics problem and"
        " arrives at the correct equilibrium/vector solution, assign a 10/10."
        " Do NOT dock points for receiving tutor guidance, asking clarifying"
        " questions, or solving only a single problem.\n\n"
        "SCORING DIRECTIVES:\n"
        "10/10: Problem solved correctly. The student correctly set up or"
        " applied equilibrium concepts ($\sum F=0$, $\sum M=0$) and reached"
        " the correct target solution.\n"
        "7-9/10: Correct Statics principles and force setup, but minor"
        " algebraic or execution errors occurred before arrival at the target.\n"
        "4-6/10: Partial understanding demonstrated, but core concepts (e.g.,"
        " FBD breakdown, moment arms, vector components) were incomplete or"
        " misapplied.\n"
        "1-3/10: Minimal participation, persistent off-topic responses, or"
        " refusal to engage with hints.\n"
        "0/10: No attempt or empty session history.\n\n"
        "STRICT FORMAT DIRECTIVE:\n"
        "Output ONLY the integer score (e.g., 10). Do not include any"
        " explanation, reconciliation notes, or extra text."
    )

    model = get_gemini_model(eval_instruction)
    if not model:
        return 0

    try:
        response = model.generate_content(
            f"Chat history to evaluate:\n{chat_history}"
        )
        score_match = re.search(r"\d+", response.text)
        if score_match:
            score = int(score_match.group())
            return min(max(score, 0), 10)
        return 0
    except Exception:
        return 0


def analyze_and_send_report(user_name, topic_title, chat_history):
    """Analyzes the Statics session and sends a professional email report to Dr. Um."""

    # Calculate score based on Statics rubric
    score = evaluate_understanding_score(chat_history)

    report_instruction = (
        "You are an academic evaluator analyzing a Statics session for Dr."
        " Dugan Um. Generate a concise mastery report.\n\n"
        "EVALUATION RULES:\n"
        "1. If the score is 10/10, explicitly state that the student"
        " successfully mastered and solved the Statics problem on the first"
        " pass.\n"
        "2. Never mention 'score reconciliation', 'missing syllabus coverage',"
        " 'unaddressed topics', or platform logging states.\n"
        "3. Use standard Markdown headers (##, ###) and bold text (**).\n"
        "4. Ensure all math/vectors in the report use LaTeX notation (e.g.,"
        " $\sum F_x = 0$, $\sum M_A = 0$).\n"
        "5. REQUIRED SECTIONS:\n"
        "   - Session Overview\n"
        f"   - Numerical Understanding Score: {score}/10\n"
        "   - Mathematical Rigor\n"
        "   - Logic Analysis\n"
        "   - Engagement Level\n"
        "   - CRITICAL: Quote the section '--- STUDENT FEEDBACK ---' exactly if"
        " present."
    )

    model = get_gemini_model(report_instruction)
    if not model:
        return "AI Analysis Unavailable"

    prompt = (
        f"Student Name: {user_name}\n"
        f"Topic: {topic_title}\n"
        f"Assigned Score: {score}/10\n\n"
        f"DATA:\n{chat_history}\n\n"
        "Format for Dr. Dugan Um. Ensure all math/vectors in the report use"
        " LaTeX."
    )

    try:
        response = model.generate_content(prompt)
        report_text = response.text
    except Exception as e:
        report_text = f"Analysis failed: {str(e)}"

    # Email Logic
    sender = st.secrets["EMAIL_SENDER"]
    password = st.secrets["EMAIL_PASSWORD"]
    receiver = "dugan.um@gmail.com"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = (
        f"Statics Tutor ({user_name}): {topic_title} [Score: {score}/10]"
    )
    msg.attach(MIMEText(report_text, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"SMTP Error: {e}")

    return report_text
