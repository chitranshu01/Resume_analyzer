# Resume Analyzer

A professional AI-powered resume analysis and job matching application built with Python and Streamlit.

## About the project

This project helps job seekers improve their resume quality and match it against job descriptions. It uses the Groq API to provide AI-powered suggestions, matching insights, and chat-based resume interaction.

The app includes three main workflows:
- Chatbot assistant for general questions
- Resume Analyzer for extracting skills and generating ATS-like recommendations
- Job Description Matcher to compare a resume against a target JD and highlight missing skills

## Project architecture

```text
Resume_analyzer/
├── app.py                 # Streamlit web application
├── chatbot.py             # CLI-based Groq chatbot
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Ignored local secrets and build files
├── README.md              # Project documentation
├── .env                   # Local environment file (not committed)
└── __pycache__/           # Generated local cache files (ignored)
```

## Features

- Upload a resume in PDF format
- Extract skills from the resume text
- Calculate ATS-style score using detected skills
- Generate AI recommendations for resume improvement
- Chat with a resume to ask targeted questions
- Match resume skills against a job description
- Keep sensitive credentials outside source code via environment variables

## Security and secrets handling

This project is designed to avoid leaking any API keys in source code.

Important rules:
- Never hardcode API keys in Python files
- Store keys in a local `.env` file
- Keep `.env` in `.gitignore`
- Use `.env.example` as the public template only

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

Then add your own Groq API key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5) Run the app

For the Streamlit app:

```bash
streamlit run app.py
```

For the terminal chatbot:

```bash
python chatbot.py
```

## Notes

- `.env` is ignored by Git to avoid credential leaks
- `.env.example` is safe to commit because it contains placeholders only
- Do not upload your real `.env` file to GitHub or any public repo

## License

This project is for educational and portfolio use.
