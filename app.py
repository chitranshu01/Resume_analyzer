import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import time
from PyPDF2 import PdfReader

# =========================
# LOAD ENV
# =========================
load_dotenv()
client = Groq(api_key=os.getenv("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"))

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Career Assistant", page_icon="🤖", layout="wide")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Settings")

model = st.sidebar.selectbox(
    "Choose Model",
    ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"]
)

temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.7)

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["🤖 Chatbot", "📄 Resume Analyzer", "🎯 JD Matcher"])

# =========================
# SKILL EXTRACTION
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

# =========================
# 🤖 CHATBOT TAB
# =========================
with tab1:
    st.title("🤖 Smart AI Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a professional AI assistant."}
        ]

    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []

    # Display chat
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append({"role": "user", "content": user_input})

        if len(st.session_state.messages) > 12:
            st.session_state.messages.pop(1)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature
            )

            reply = response.choices[0].message.content

            for word in reply.split():
                full_response += word + " "
                time.sleep(0.02)
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

# =========================
# 📄 RESUME ANALYZER TAB
# =========================
with tab2:
    st.title("📄 Resume Analyzer")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file:
        st.success("Resume uploaded successfully!")

        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        # Skill extraction
        skills = extract_skills(text)

        st.subheader("🧠 Extracted Skills")
        st.write(skills)

        # ATS score logic
        score = min(len(skills) * 5, 100)

        st.subheader("📊 ATS Score")
        st.progress(score / 100)
        st.success(f"{score}/100")

        # AI suggestions
        prompt = f"""
        Analyze this resume and give:
        - Missing skills
        - Improvements
        - Career suggestions

        Resume:
        {text}
        """

        with st.spinner("Analyzing resume..."):
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )

        result = response.choices[0].message.content

        st.subheader("📌 AI Suggestions")
        st.write(result)

        # Download
        st.download_button(
            "📥 Download Report",
            result,
            file_name="resume_analysis.txt"
        )

        # =========================
        # 💬 CHAT WITH RESUME
        # =========================
        st.divider()
        st.subheader("💬 Chat with your Resume")

        if "resume_chat" not in st.session_state:
            st.session_state.resume_chat = []

        question = st.text_input("Ask something about your resume...")

        if question:
            st.session_state.resume_chat.append({"role": "user", "content": question})

            resume_prompt = f"""
            Answer based on this resume:

            {text}

            Question: {question}
            """

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": resume_prompt}]
            )

            answer = response.choices[0].message.content

            st.session_state.resume_chat.append({"role": "assistant", "content": answer})

        for msg in st.session_state.resume_chat:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

# =========================
# 🎯 JD MATCHER TAB
# =========================
with tab3:
    st.title("🎯 Resume vs Job Description Matcher")

    resume_file = st.file_uploader("Upload Resume", type=["pdf"], key="jd")

    jd_text = st.text_area("Paste Job Description")

    if resume_file and jd_text:
        reader = PdfReader(resume_file)
        resume_text = ""

        for page in reader.pages:
            resume_text += page.extract_text()

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        matched = list(set(resume_skills) & set(jd_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        match_score = int((len(matched) / max(len(jd_skills), 1)) * 100)

        st.subheader("📊 Match Score")
        st.progress(match_score / 100)
        st.success(f"{match_score}% Match")

        st.subheader("✅ Matching Skills")
        st.write(matched)

        st.subheader("❌ Missing Skills")
        st.write(missing)