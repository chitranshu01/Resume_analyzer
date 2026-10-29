# Resume Analyzer

A professional AI-powered resume analysis and job matching application built with Python and Streamlit.

## About the project

This project helps job seekers improve their resume quality and match it against job descriptions. It uses the Groq API to provide AI-powered suggestions, matching insights, and chat-based resume interaction.

The app includes three main workflows:
- **Chatbot** for general career questions
- **Resume Analyzer** for extracting skills and generating ATS-style recommendations
- **JD Matcher** to compare a resume against a target job description and highlight gaps

## Project architecture

```text
Resume_analyzer/
├── chatbot.py             # Streamlit web app (Chatbot, Resume Analyzer, JD Matcher)
├── app.py                 # Optional CLI Groq chatbot
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template (safe to commit)
├── .gitignore             # Ignores .env, venv, cache, and local secrets
├── README.md              # Project documentation
└── .env                   # Local secrets only (never commit)
```

## Features

- Upload a resume in PDF format
- Extract skills from the resume text
- Calculate an ATS-style score using detected skills
- Generate AI recommendations for resume improvement
- Chat with your resume using follow-up questions
- Match resume skills against a pasted job description
- Generate AI fit analysis for JD matching
- Keep API keys outside source code via environment variables

## Models used (Groq)

Each feature uses a dedicated model suited to the task:

| Feature | Model | Purpose |
|---|---|---|
| Chatbot | `openai/gpt-oss-20b` | Fast conversational replies |
| Resume Analyzer | `openai/gpt-oss-120b` | Deeper resume analysis + up to 4 follow-up questions |
| JD Matcher | `openai/gpt-oss-20b` | Resume vs JD comparison under free-tier token limits |
| CLI chatbot (`app.py`) | `openai/gpt-oss-20b` | Terminal chat |

Model IDs and `max_tokens` caps are defined near the top of `chatbot.py` so they can be updated if Groq retires models or changes rate limits.

API calls use capped output tokens and truncated resume/JD text to avoid Groq `rate_limit_exceeded` / OTPM errors on free tiers.

## Security and secrets handling

This project is designed to avoid leaking API keys in source code.

Important rules:
- Never hardcode API keys in Python files
- Store keys in a local `.env` file
- Keep `.env` in `.gitignore`
- Use `.env.example` as the public template only
- Never commit or push a real `.env` file

## Setup guide

### 1) Clone the repository

```bash
git clone https://github.com/chitranshu01/Resume_analyzer.git
cd Resume_analyzer
```

### 2) Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then put your own Groq API key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a key from [Groq Console](https://console.groq.com/keys).

### 5) Run the app

Streamlit app (main UI):

```bash
streamlit run chatbot.py
```

Then open the local URL shown in the terminal (usually `http://localhost:8501`).

Optional CLI chatbot:

```bash
python app.py
```

Type `exit` to quit the CLI chatbot.

## Usage tips

1. Open the **Resume Analyzer** tab and upload a PDF resume.
2. Review extracted skills, ATS score, and AI suggestions (including suggested job roles).
3. Ask up to **4 follow-up questions** about that resume (for example: “For what job roles can I apply?”).
4. Open the **JD Matcher** tab, upload a resume, paste a job description, and review match score + AI analysis.
5. Use the **Chatbot** tab for general career questions.

## Troubleshooting

- **Missing `GROQ_API_KEY`**: create `.env` from `.env.example` and restart the app.
- **`model_not_found` (404)**: Groq may have retired a model ID. Update the model constants in `chatbot.py` / `app.py` to models available on your Groq account.
- **`rate_limit_exceeded` / OTPM (429)**: wait 30–60 seconds and retry. The app already caps `max_tokens`; if it still happens, ask shorter questions or wait for the quota window to reset.
- **PDF text empty**: some scanned PDFs have no extractable text; use a text-based PDF.

## Notes

- `.env` is ignored by Git to avoid credential leaks
- `.env.example` is safe to commit because it contains placeholders only
- Do not upload your real `.env` file to GitHub or any public repo

## License

This project is for educational and portfolio use.
