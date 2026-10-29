import os
import time

import streamlit as st
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIError
from PyPDF2 import PdfReader

# =========================
# LOAD ENV
# =========================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY. Create a local .env file with GROQ_API_KEY=your_key_here and restart the app.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Feature-specific Groq models (current account-available IDs)
CHATBOT_MODEL = "openai/gpt-oss-20b"          # fast conversational replies
RESUME_MODEL = "openai/gpt-oss-120b"          # deeper resume analysis
JD_MATCHER_MODEL = "openai/gpt-oss-20b"       # JD matching under free-tier OTPM limits

# Keep responses under Groq free-tier OTPM limits (~1000 tokens/min on some models)
CHAT_MAX_TOKENS = 500
RESUME_MAX_TOKENS = 700
FOLLOWUP_MAX_TOKENS = 350
JD_MAX_TOKENS = 650
MAX_RESUME_CHARS = 6000
MAX_JD_CHARS = 4000
MAX_RESUME_FOLLOWUPS = 4

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Career Assistant", page_icon="🤖", layout="wide")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Settings")
st.sidebar.caption("Models used by each feature")
st.sidebar.markdown(
    f"""
- **Chatbot:** `{CHATBOT_MODEL}`
- **Resume Analyzer:** `{RESUME_MODEL}`
- **JD Matcher:** `{JD_MATCHER_MODEL}`
"""
)

temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.7)

# =========================
# HELPERS
# =========================
def extract_skills(text):
    skills_db = [
        "python", "java", "c++", "sql", "machine learning",
        "deep learning", "nlp", "data analysis",
        "pandas", "numpy", "tensorflow", "pytorch",
        "streamlit", "flask", "django", "react", "node"
    ]

    found = []
    text_lower = text.lower()

    for skill in skills_db:
        if skill in text_lower:
            found.append(skill)

    return found


def truncate_text(text, limit):
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[Resume text truncated to stay within API limits.]"


def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            parts.append(page_text)
    return "\n".join(parts)


def ask_groq(model, messages, *, max_tokens, temperature_value):
    """Call Groq with capped output tokens and friendly rate-limit handling."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature_value,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except RateLimitError:
        return (
            "⚠️ Groq rate limit reached (token/minute quota). "
            "Please wait about 30–60 seconds, then ask again with a shorter question."
        )
    except APIError as exc:
        return f"⚠️ Groq API error: {exc}"


# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["🤖 Chatbot", "📄 Resume Analyzer", "🎯 JD Matcher"])

# =========================
# 🤖 CHATBOT TAB
# =========================
with tab1:
    st.title("🤖 Smart AI Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a professional AI assistant. Keep answers concise and useful."}
        ]

    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {"role": "system", "content": "You are a professional AI assistant. Keep answers concise and useful."}
        ]

    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append({"role": "user", "content": user_input})

        # Keep chat history short to reduce token usage
        while len(st.session_state.messages) > 10:
            st.session_state.messages.pop(1)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            reply = ask_groq(
                CHATBOT_MODEL,
                st.session_state.messages,
                max_tokens=CHAT_MAX_TOKENS,
                temperature_value=temperature,
            )

            for word in reply.split():
                full_response += word + " "
                time.sleep(0.01)
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response.strip()}
        )

# =========================
# 📄 RESUME ANALYZER TAB
# =========================
with tab2:
    st.title("📄 Resume Analyzer")
    st.caption("Upload a resume, get AI analysis, then ask up to 4 follow-up questions (job roles, skills gaps, etc.).")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_upload")

    if uploaded_file:
        file_id = f"{uploaded_file.name}-{uploaded_file.size}"

        # Re-analyze only when a new file is uploaded
        if st.session_state.get("resume_file_id") != file_id:
            st.session_state.resume_file_id = file_id
            st.session_state.resume_text = extract_pdf_text(uploaded_file)
            st.session_state.resume_skills = extract_skills(st.session_state.resume_text)
            st.session_state.resume_analysis = None
            st.session_state.resume_chat = []
            st.session_state.resume_followups_used = 0

        text = st.session_state.resume_text
        skills = st.session_state.resume_skills
        score = min(len(skills) * 5, 100)

        st.success("Resume uploaded successfully!")

        st.subheader("🧠 Extracted Skills")
        st.write(skills if skills else "No listed skills detected from the keyword list.")

        st.subheader("📊 ATS Score")
        st.progress(score / 100)
        st.success(f"{score}/100")

        if st.session_state.resume_analysis is None:
            prompt = f"""
Analyze this resume briefly and clearly. Keep the whole answer under 450 words.

Cover:
1) Strengths
2) Missing skills
3) Improvements
4) 3-5 job roles this person can apply for

Resume:
{truncate_text(text, MAX_RESUME_CHARS)}
"""
            with st.spinner("Analyzing resume..."):
                st.session_state.resume_analysis = ask_groq(
                    RESUME_MODEL,
                    [{"role": "user", "content": prompt}],
                    max_tokens=RESUME_MAX_TOKENS,
                    temperature_value=temperature,
                )

        result = st.session_state.resume_analysis

        st.subheader("📌 AI Suggestions")
        st.write(result)

        st.download_button(
            "📥 Download Report",
            result,
            file_name="resume_analysis.txt",
        )

        # =========================
        # 💬 FOLLOW-UP QUESTIONS
        # =========================
        st.divider()
        st.subheader("💬 Ask about your resume")
        st.write(
            "After analysis, ask 2–4 questions such as: "
            "*What job roles can I apply for?* / *Which skills should I learn next?*"
        )

        used = st.session_state.get("resume_followups_used", 0)
        remaining = MAX_RESUME_FOLLOWUPS - used
        st.info(f"Follow-up questions remaining: **{remaining}/{MAX_RESUME_FOLLOWUPS}**")

        for msg in st.session_state.resume_chat:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if remaining > 0:
            with st.form("resume_followup_form", clear_on_submit=True):
                question = st.text_input(
                    "Your question",
                    placeholder="Example: For what job roles can I apply?",
                )
                submitted = st.form_submit_button("Ask")

            if submitted and question.strip():
                q = question.strip()
                st.session_state.resume_chat.append({"role": "user", "content": q})

                resume_prompt = f"""
Answer ONLY from this resume and the prior analysis. Be concise (under 180 words).
If asked about job roles, suggest concrete roles and why they fit.

Resume:
{truncate_text(text, MAX_RESUME_CHARS)}

Prior analysis:
{truncate_text(result, 2500)}

Question: {q}
"""
                with st.spinner("Thinking..."):
                    answer = ask_groq(
                        RESUME_MODEL,
                        [{"role": "user", "content": resume_prompt}],
                        max_tokens=FOLLOWUP_MAX_TOKENS,
                        temperature_value=temperature,
                    )

                st.session_state.resume_chat.append({"role": "assistant", "content": answer})
                st.session_state.resume_followups_used = used + 1
                st.rerun()
        else:
            st.warning("You used all 4 follow-up questions for this resume. Upload a new file or refresh analysis by re-uploading.")
            if st.button("Reset follow-up questions"):
                st.session_state.resume_chat = []
                st.session_state.resume_followups_used = 0
                st.rerun()

# =========================
# 🎯 JD MATCHER TAB
# =========================
with tab3:
    st.title("🎯 Resume vs Job Description Matcher")

    resume_file = st.file_uploader("Upload Resume", type=["pdf"], key="jd")
    jd_text = st.text_area("Paste Job Description")

    if resume_file and jd_text:
        file_id = f"{resume_file.name}-{resume_file.size}-{hash(jd_text)}"

        if st.session_state.get("jd_file_id") != file_id:
            st.session_state.jd_file_id = file_id
            st.session_state.jd_resume_text = extract_pdf_text(resume_file)
            st.session_state.jd_analysis = None

        resume_text = st.session_state.jd_resume_text
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched = list(set(resume_skills) & set(jd_skills))
        missing = list(set(jd_skills) - set(resume_skills))
        match_score = int((len(matched) / max(len(jd_skills), 1)) * 100)

        st.subheader("📊 Match Score")
        st.progress(match_score / 100)
        st.success(f"{match_score}% Match")

        st.subheader("✅ Matching Skills")
        st.write(matched if matched else "No keyword overlaps found.")

        st.subheader("❌ Missing Skills")
        st.write(missing if missing else "No missing keyword skills detected.")

        if st.session_state.jd_analysis is None:
            match_prompt = f"""
Compare this resume against the job description.
Keep the answer under 400 words and structured:

1) Overall fit summary
2) Strong matching areas
3) Critical gaps / missing skills
4) Concrete improvements to raise match score

Resume:
{truncate_text(resume_text, MAX_RESUME_CHARS)}

Job Description:
{truncate_text(jd_text, MAX_JD_CHARS)}

Keyword matched skills: {matched}
Keyword missing skills: {missing}
Keyword match score: {match_score}%
"""
            with st.spinner("Matching resume to job description..."):
                st.session_state.jd_analysis = ask_groq(
                    JD_MATCHER_MODEL,
                    [{"role": "user", "content": match_prompt}],
                    max_tokens=JD_MAX_TOKENS,
                    temperature_value=temperature,
                )

        ai_match = st.session_state.jd_analysis
        st.subheader("🤖 AI Match Analysis")
        st.write(ai_match)

        st.download_button(
            "📥 Download Match Report",
            ai_match,
            file_name="jd_match_analysis.txt",
        )
