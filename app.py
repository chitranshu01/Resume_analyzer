import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY. Create a .env file with GROQ_API_KEY=your_key_here and try again.")

client = Groq(api_key=GROQ_API_KEY)
messages = [
    {"role": "system", "content": "You are an expert AI assistant. Give clear, structured, and helpful answers. If possible, explain with examples."}
]

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )

    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})

    print("AI:", reply)
